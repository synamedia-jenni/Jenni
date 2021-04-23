import os
from unittest import mock

from jenni.steps.stashing import Step
from jenni.tests.unittestutils import *


class Tests(TestCase):
    def test_generate(self):
        self.generate(
            contains=[
                # TODO more checks of code
                # """Start of setup code""",
                # """End of setup code""",
                """pipelineJob('''simple_job''')""",
                """displayName('''Simple Job''')""",
                """description('''simple_job!''')""",
                """archiveArtifacts("*.log, */*.log")""",
                """pipelineJob('''skip_seed_job''')""",
                """logRotator { numToKeep(5) }""",
                """throttleConcurrentBuilds { maxPerNode(1) }""",
                """githubPush()""",
                """script('''echo 123''')""",
            ],
            not_contains=[
                "cron",
                "folder(",
            ],
        )

    def test_generate_in_ci(self):
        with setup_environment_vars(BUILD_URL="http://a/b/c/d"):
            self.generate(
                contains=[
                    # TODO more checks of code
                    # """Start of setup code""",
                    # """End of setup code""",
                    """pipelineJob('''simple_job''')""",
                    """displayName('''Simple Job''')""",
                    """description('''simple_job!''')""",
                    """archiveArtifacts("*.log, */*.log")""",
                    """skipped since skip_seed is True""",
                ],
                not_contains=[
                    """pipelineJob('''skip_seed_job''')""",
                    "cron",
                    "folder(",
                ],
            )
