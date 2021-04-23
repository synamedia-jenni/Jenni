from jenni.models import FolderBase
from jenni.models.jobbase import JobBase
from jenni.tests.unittestutils import TestCase


class Tests(TestCase):
    def test_generate(self):
        self.generate(
            contains=[
                """folder('generated_subfolder0')""",
                """pipelineJob('''generated_job0''')""",
                """pipelineJob('''generated_job1''')""",
                """pipelineJob('''generated_subfolder0/generated_subjob0''')""",
            ],
        )

    def xxxtest_run(self):
        self.run_job("generated_job0")
        self.run_job("generated_job1")
