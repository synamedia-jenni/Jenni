import os
from unittest import mock

from jenni.steps import Step
from jenni.tests.unittestutils import *
from jenni import instance


class Tests(TestCase):
    def test_missing_job_name_env_var(self):
        with self.assertRaisesRegex(SystemExit, r"ERROR: expecting JOB_NAME environment variable to be set") as ex:
            with setup_environment_vars(count=99):
                instance.run_main(["--config-dir", self.folder, "run"])
        print(f"Assertion correctly occurred: {ex.exception}")

    def test_run(self):
        with mock.patch.object(Step, "stash", return_value=None) as mock_method:
            with setup_environment_vars(count=99):
                self.run_job("simple_job")
        mock_method.assert_called_once_with("stash1", includes="inc1")
