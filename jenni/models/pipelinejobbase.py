from .jobbase import JobBase
import logging
from io import TextIOWrapper
from typing import List

# See https://docs.python.org/3.6/library/abc.html
from abc import ABC, abstractmethod


from .params import ParamBase
from ..utils import quote3xs, tidy_text, quote1s


class PipelineJobBase(JobBase, ABC):
    @abstractmethod
    def __init__(
        self,
        github_project_url: str = "",
        logrotator_spec: str = "",
        quiet_period: int = 0,
        throttleconcurrentbuilds_spec: str = "",
        trigger_cron_spec: str = "",
        trigger_on_github_push: bool = False,
        **kwargs,
    ):
        """
        :param github_project_url: If set, ensure Jenkins job shows the Github icon linking to this url.

        :param trigger_on_github_push: if True, trigger on github push.

        :param logrotator_spec: spec according to
            https://jenkinsci.github.io/job-dsl-plugin/#path/pipelineJob-logRotator
            Example:

            * ``numToKeep(50)``
            * ``artifactNumToKeep(10)``

        :param throttleconcurrentbuilds_spec: spec according to
            https://jenkinsci.github.io/job-dsl-plugin/#path/pipelineJob-throttleConcurrentBuilds
            Example:

            * ``maxPerNode(1)``
            * ``maxTotal(2)``

        :param trigger_cron_spec: cron spec according to
            https://jenkinsci.github.io/job-dsl-plugin/#path/pipelineJob-triggers-cron
            Example:

            * ``H * * * *``
            * ``0 8 * * *``

        :param kwargs: optional arguments. Passed through to :class:`~jenni.models.JobBase` :func:`~jenni.models.PipelineJobBase.__init__`.
        """
        super().__init__(**kwargs)

        self.github_project_url = github_project_url
        self.logrotator_spec: str = logrotator_spec
        self.quiet_period: int = quiet_period
        self.throttleconcurrentbuilds_spec = throttleconcurrentbuilds_spec
        self.trigger_cron_spec: str = trigger_cron_spec

        self.trigger_on_github_push: bool = trigger_on_github_push

    @abstractmethod
    def _get_script(self) -> str:
        raise NotImplementedError()

    def write_jobdsl(self, fp: TextIOWrapper):
        logging.debug(f"write_jobdsl start {self}")
        script = self._get_script()
        jobdsl = [f"""pipelineJob('''{self.jenkins_path}''')""", "{"]

        jobdsl.append(f"    displayName({quote3xs(self.name if self.title == '' else self.title)})")

        jobdsl.append(f"    description({quote3xs(tidy_text(self.description))})")

        if self.github_project_url:
            jobdsl.append(f"    properties {{ githubProjectUrl({quote1s(self.github_project_url)}) }}")

        if self.logrotator_spec:
            jobdsl.append("    logRotator { " + self.logrotator_spec + " }")

        if self.throttleconcurrentbuilds_spec:
            jobdsl.append("    throttleConcurrentBuilds { " + self.throttleconcurrentbuilds_spec + " }")

        if self.trigger_cron_spec or self.trigger_on_github_push:
            jobdsl.append("    triggers {")
            if self.trigger_cron_spec:
                jobdsl.append(f"      cron({quote3xs(self.trigger_cron_spec)})")
            if self.trigger_on_github_push:
                jobdsl.append("      githubPush()")
            jobdsl.append("    }")

            if self.trigger_on_github_push:
                if self.quiet_period != 0:
                    jobdsl.append(f"    quietPeriod({self.quiet_period})")

        self._generate_job_parameters_jobdsl(jobdsl)

        jobdsl.append(
            f"""
            definition {{
                cps {{
                    script({quote3xs(script)})
                    sandbox()
                }}
            }}
        """
        )

        jobdsl.append("}")
        jobdsl.append("")  # Ensures code ends with \n
        fp.write("\n".join(jobdsl))

    def _generate_job_parameters_jobdsl(self, jobdsl: List[str]):

        has_parameters = False

        params = [value for value in self.__dict__.values() if isinstance(value, ParamBase)]
        params.sort(key=lambda param: f"{param.order:02d}-{param.name}")
        for param in params:
            if not has_parameters:
                has_parameters = True
                jobdsl.append("    parameters {")
            param.write_jobdsl(jobdsl)
        if has_parameters:
            jobdsl.append("    }")
