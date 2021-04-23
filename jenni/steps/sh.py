from abc import ABC
from typing import Union

from jenni.stepbase import StepBase
from jenni.utils import quote3xs, bool2groovy


class Step(StepBase, ABC):
    def sh(self, script: str, returnStatus: bool = False, returnStdout: bool = False) -> Union[None, int, str]:
        """
        Runs sh workflow step.
        @see https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/#sh-shell-script
        :param script:
        Runs a Bourne shell script, typically on a Unix node. Multiple lines are accepted.
        An interpreter selector may be used, for example: #!/usr/bin/perl
        Otherwise the system default shell will be run, using the -xe flags
        (you can specify set +e and/or set +x to disable those).
        :param returnStatus:  Normally, a script which exits with a nonzero status code will cause
        the step to fail with an exception. If this option is checked, the return value of the step
        will instead be the status code. You may then compare it to zero, for example.
        :param returnStdout:
        If checked, standard output from the task is returned as the step value as a String,
        rather than being printed to the build log. (Standard error, if any, will still be printed to the log.)
        You will often want to call .trim() on the result to strip off a trailing newline.
        :return:
        """
        if returnStatus and returnStdout:
            raise SystemExit("sh step cannot have returnStatus and returnStdout set to True")
        code = (
            "sh(script:"
            + quote3xs(script)
            + ", returnStatus:"
            + bool2groovy(returnStatus)
            + ", returnStdout:"
            + bool2groovy(returnStdout)
            + ")"
        )
        return self.execute_groovy(code)
