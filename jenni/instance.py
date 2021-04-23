import argparse
from io import TextIOWrapper
from pathlib import Path
import logging
import os
import sys
from importlib import import_module
from typing import Optional

from .models import itembase, PythonPipelineJobBase, FolderBase
from .models.itembase import ItemBase
from . import stepserver
from .models.params import ParamBase
from .steps import Step


class Configuration(Step):
    def __init__(self, config_dir):
        config_dir = Path(config_dir)
        self.config_dir = config_dir.resolve()
        self.jobs_dir = (config_dir / "jobs").resolve()
        if not self.jobs_dir.is_dir():
            raise SystemExit(f"Configuration directory should contain jobs subfolder: {config_dir}")
        self.models_dir = (config_dir / "models").resolve()
        logging.info(f"Jobs   from: {self.jobs_dir}")
        logging.info(f"Models from: {self.models_dir}")
        self.in_ci = os.getenv("BUILD_URL") is not None
        itembase.config_dir = self.config_dir

    def generate(self, fp: TextIOWrapper):
        orig_sys_path = list(sys.path)
        try:
            sys.path.insert(0, str(self.config_dir))
            self._generate_jobdsl(fp)
        finally:
            sys.path = orig_sys_path

    def _setup_job_params(self, job: PythonPipelineJobBase):
        for name, value in job.__dict__.items():
            if value is not None and isinstance(value, ParamBase):
                logging.debug(f"Setting up param {value}")
                value._set_value()

    def _generate_jobdsl(self, fp: TextIOWrapper):
        logging.info("_generate_jobdsl start")
        item: ItemBase
        items_set = set()
        items_list = []
        import jobs

        sys.modules["jobs"].__item_name__ = ""
        sys.modules["jobs"].__parent_item__ = None
        root_folder = jobs.Folder()
        # First create _all_ the items, then generate jobdsl code for them all.
        for item in root_folder.yield_items():
            if item in items_set:
                raise SystemExit(f"Duplicated item in jobdsl generation ({item})")
            items_set.add(item)
            items_list.append(item)
        self._call_post_yield_handlers(root_folder)
        for item in items_list:
            fp.write(f"\n// Processing {item}\n")
            if item.skip_seed and self.in_ci:
                logging.warning(f"write_jobdsl skipped since skip_seed is True: {item}")
                fp.write(f"\n// write_jobdsl skipped since skip_seed is True: {item}\n")
            else:
                item.write_jobdsl(fp)
            fp.write(f"\n")
        logging.info("_generate_jobdsl done")

    def _call_post_yield_handlers(self, item):
        for child in item.children:
            self._call_post_yield_handlers(child)
        item.post_yield_handler()

    def run_job(self, job_name: str = None, start_stepserver=True):
        """
        :param job_name: optional name of the job.
        Default is value of the JOB_NAME jenkins environment variable.
        :param start_stepserver: during unittesting this could be set to False.
        """

        if job_name is None:
            # Use JOB_NAME env var to find the python module to load.
            job_name = os.getenv("JOB_NAME")
            if not job_name:
                raise SystemExit(
                    "ERROR: expecting JOB_NAME environment variable to be set"
                    ", or an explicit job name to be specified"
                )
        else:
            os.environ["JOB_NAME"] = job_name

        # module_name = "jobs." + job_name.replace("/", ".")
        # module_name = re.sub(r"[^\w.]", "_", module_name)

        module_name_parts = job_name.replace("-", "_").split("/")
        module_name = f"jobs.{'.'.join(module_name_parts)}"
        module_name_to_load = "jobs"
        # logging.debug(f"Importing module {module_name}")
        try:
            module = import_module(module_name_to_load)
            while module_name_parts:
                folder: FolderBase = itembase.item_by_module.get(module_name_to_load)
                if folder is None:
                    folder = module.Folder()
                module_name_to_load = f"{module_name_to_load}.{module_name_parts.pop(0)}"
                for item in folder.yield_items(module_name_to_load):
                    logging.debug(f"Yielded item {item}")
                module = import_module(module_name_to_load)
        except Exception as ex:
            logging.error(f"Import problem: {ex}", exc_info=True)
            logging.error(f"Python path is: {sys.path}")
            raise ex
        # logging.debug(f"Imported: module = {module}")

        job_class: type = module.Job
        if job_class is None:
            raise SystemExit(
                f"Module {module_name} which the job name ({job_name} mapped to, should contain a class called JobBase"
            )
        if not issubclass(job_class, PythonPipelineJobBase):
            raise SystemExit(
                f"Module {module_name} contains {job_class} but it is not a sub-class of PythonPipelineJobBase, so it cannot be run"
            )

        job: PythonPipelineJobBase = itembase.item_by_module[module_name]
        self._setup_job_params(job)

        if start_stepserver:
            stepserver.start_server()

        exception = None
        try:
            job.run()
            logging.info("Exiting OK")
            if start_stepserver:
                stepserver.execute_groovy("done = true", exit_status=0)
        except Exception as ex:
            exception = ex
            logging.error(f"Exiting with ERROR: {ex}")
            if start_stepserver:
                stepserver.execute_groovy("done = true", exit_status=1)
        if exception:
            raise exception


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="jenni",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        help="No -q: DEBUG, -q: INFO, -qq: WARNING, -qqq: ERROR",
        default=0,
    )
    parser.add_argument(
        "-c",
        "--config-dir",
        dest="config_dir",
        required=True,
        help="Configuration directory, must contain at least a jobs subfolder, and optionally a models subfolder",
    )
    parser.add_argument("-l", "--log-file", help="Log to file")
    # https://docs.python.org/3.6/library/argparse.html?highlight=arg#sub-commands
    subparsers = parser.add_subparsers(dest="action", help="sub-command help")

    parser_run = subparsers.add_parser("run", help="Run the job")
    parser_run.add_argument("-j", "--job", dest="job_name", help="Name of job to run. Default is $JOB_NAME")
    parser_run.add_argument("param_assignment", nargs="*", help="name=value for each job parameter")

    parser_seed = subparsers.add_parser("seed", help="Seed jobs, IE write job dsl Groovy code")
    parser_seed.add_argument("-o", "--output", dest="output_file", help="Output jobdsl filename")
    parser_seed.add_argument(
        "--append",
        action="store_true",
        help="Append rather than overwrite output jobdsl file",
    )

    return parser.parse_args(args)


configuration: Optional[Configuration] = None


def run_main(args=None):
    logging.captureWarnings(True)
    logging_format = "%(asctime)-15s %(levelname)-8s %(message)s"
    logging.basicConfig(format=logging_format, level=logging.DEBUG)

    options = parse_args(args)
    if options.quiet == 0:
        logging.root.setLevel(logging.DEBUG)
    elif options.quiet == 1:
        logging.root.setLevel(logging.INFO)
    elif options.quiet == 2:
        logging.root.setLevel(logging.WARNING)
    else:
        logging.root.setLevel(logging.ERROR)
    if options.log_file:
        f_handler = logging.FileHandler(options.log_file)
        logging.root.addHandler(f_handler)
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(logging.Formatter(logging_format))

    global configuration
    configuration = Configuration(config_dir=options.config_dir)

    if options.action == "run":
        configuration.run_job(job_name=options.job_name)
    elif options.action == "seed":
        if options.output_file:
            logging.info(f"Writing {options.output_file}")
            file_open_mode = "at" if options.append else "wt"
            output = open(options.output_file, file_open_mode)
        else:
            output = sys.stdout
        configuration.generate(fp=output)
        if options.output_file:
            logging.info(f"See {options.output_file}")
    else:
        raise ValueError(f"Unexpected action value: {options.action}, expecting seed or run")
