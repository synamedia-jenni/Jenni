from jenni.tests.unittestutils import StepTestCase


class Tests(StepTestCase):
    # TODO make a more efficient test system for steps,
    def test_archiveArtifacts(self):
        with self.assertRaisesRegex(TypeError, r"""missing 1 required positional argument: 'artifacts"""):
            # noinspection PyArgumentList
            self.workflow.archiveArtifacts()

        self.assertRegex(self.workflow.archiveArtifacts(artifacts="x"), r"""archiveArtifacts\('x',""")

        self.assertRegex(
            self.workflow.archiveArtifacts(artifacts="x"),
            r"""archiveArtifacts\('x',.*excludes:''""",
        )
        self.assertRegex(
            self.workflow.archiveArtifacts(artifacts="x", excludes="y"),
            r"""archiveArtifacts\('x',.*excludes:'y'""",
        )

        self.assertRegex(
            self.workflow.archiveArtifacts(artifacts="x"),
            r"""archiveArtifacts\('x',.*allowEmptyArchive:false""",
        )
        self.assertRegex(
            self.workflow.archiveArtifacts(artifacts="x", allowEmptyArchive=True),
            r"""archiveArtifacts\('x',.*allowEmptyArchive:true""",
        )
