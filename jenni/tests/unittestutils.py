import importlib
import logging
import os
import subprocess
import sys
import unittest
from contextlib import contextmanager
from typing import List

from io import StringIO

from jenni.instance import Configuration
from jenni.models import FolderBase, RootFolderBase, PythonPipelineJobBase
from jenni.models.itembase import reset
from jenni.models.jobbase import JobBase
from jenni.steps import Step

logging.captureWarnings(True)
FORMAT = "%(asctime)-15s %(levelname)-8s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


@contextmanager
def setup_environment_vars(**kwargs):
    orig_values = {}
    for key, new_value in kwargs.items():
        orig_values[key] = os.environ.get(key, None)
        if new_value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = str(new_value)
    try:
        yield
    finally:
        for key, orig_value in orig_values.items():
            if orig_value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = orig_value


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.clear_item_setup()

    def tearDown(self) -> None:
        super().tearDown()
        sys.path = self.orig_path
        self.clear_item_setup()

    def clear_item_setup(self):
        reset()
        self.clear_jobs_modules()
        self.orig_path = list(sys.path)
        # The folder containing this test file
        self.folder = os.path.dirname(sys.modules[self.__module__].__file__)
        sys.path.insert(0, self.folder)
        importlib.invalidate_caches()
        # print(f"sys.path now {sys.path}")

    @staticmethod
    def clear_jobs_modules():
        """
        Remove all modules starting with "jobs." + "jobs" itself, from sys.modules
        """
        for name in list(sys.modules.keys()):
            if name.startswith("jobs."):
                del sys.modules[name]
        try:
            del sys.modules["jobs"]
        except KeyError:
            pass

    def run_job(self, job_name: str):
        self.clear_item_setup()
        with setup_environment_vars(JOB_NAME=job_name):
            Configuration(config_dir=self.folder).run_job(start_stepserver=False)

    def generate(
        self,
        contains: List[str] = None,
        not_contains: List[str] = None,
        regexs: List[str] = None,
        not_regexs: List[str] = None,
    ) -> str:
        self.clear_item_setup()
        buf = StringIO()
        Configuration(config_dir=self.folder).generate(fp=buf)
        s = buf.getvalue()
        logging.info("Generated code:\n" + s)
        self.validate_text(s, contains, not_contains, regexs, not_regexs)
        self.validate_groovy_syntax(s, None)
        return s

    def validate_text(
        self,
        s: str,
        contains: List[str] = None,
        not_contains: List[str] = None,
        regexs: List[str] = None,
        not_regexs: List[str] = None,
    ):
        if contains:
            for needle in contains:
                self.assertIn(needle, s)
        if not_contains:
            for needle in not_contains:
                self.assertNotIn(needle, s)
        if regexs:
            for regex in regexs:
                self.assertRegex(s, regex)
        if not_regexs:
            for regex in not_regexs:
                self.assertNotRegex(s, regex)

    def validate_groovy_syntax(self, code: str, job: JobBase = None):
        test_code = (
            "def folder(def name, def body) {assert body instanceof Closure}; "
            + "def pipelineJob(def name, def body) {assert body instanceof Closure}; "
            + code
            + " ; print 'SYNTAX_IS_OK'; System.exit(0);"
        )
        cmd = ["groovy", "-e", test_code]
        logging.debug(f"Running groovy to check syntax")
        # logging.debug(f"Running groovy to check syntax for job {job.name}")
        process = subprocess.run(cmd, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # logging.debug(f"stdout: {process.stdout}")
        # logging.debug(f"stderr: {process.stderr}")
        if process.returncode != 0:
            error_msg = f"return code {process.returncode}"
        elif process.stdout != "SYNTAX_IS_OK":
            error_msg = f"stdout != SYNTAX_IS_OK"
        else:
            error_msg = None
        if error_msg is not None:
            self.fail(
                f"Groovy check failed: {error_msg}:\nstdout: {process.stdout}\nstderr: {process.stderr}\nGroovy: {code}"
            )


class StepTestCase(TestCase):
    def setUp(self):
        self.workflow = self.StepsTester(self)
        self.groovy: List[str] = []
        self.clear_item_setup()

    def tearDown(self) -> None:
        self.validate_groovy_syntax("{ -> " + "\n".join(self.groovy) + "\n}\n")

    class StepsTester(Step):
        def __init__(self, test_case):
            self.test_case = test_case

        def execute_groovy(self, code: str) -> str:
            self.test_case.groovy.append(code)
            return code


class RootFolder(RootFolderBase):
    def pythonpipelinejob_inside_node_wrapper(self, job: PythonPipelineJobBase, groovy_code: str) -> str:
        return f"""\
//pythonpipelinejob_inside_node_wrapper start
git("...") // git checkout
{groovy_code}
//pythonpipelinejob_inside_node_wrapper end
"""

    def __init__(self, **kwargs):
        super().__init__(description="Root folder", url="http://my-jenkins.example.com/", **kwargs)

    def pythonpipelinejob_main_wrapper(self, job: PythonPipelineJobBase, groovy_code: str) -> str:
        return f"""\
//pythonpipelinejob_main_wrapper start
{groovy_code}
//pythonpipelinejob_main_wrapper end
"""
