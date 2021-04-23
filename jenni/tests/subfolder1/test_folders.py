from jenni.models import FolderBase
from jenni.models.jobbase import JobBase
from jenni.tests.unittestutils import TestCase


class Tests(TestCase):
    def test_generate(self):
        self.generate(
            contains=[
                """pipelineJob('''folder1/job1''')""",
                """folder('folder1')""",
                """description('''This is folder1''')""",
            ],
        )

    def test_run(self):
        self.run_job("folder1/job1")
