from jenni.tests.unittestutils import StepTestCase


class Tests(StepTestCase):
    def test_sh(self):
        with self.assertRaisesRegex(
            SystemExit,
            r"""sh step cannot have returnStatus and returnStdout set to True""",
        ):
            # noinspection PyArgumentList
            self.workflow.sh("ls", returnStatus=True, returnStdout=True)

        self.assertEqual(
            self.workflow.sh(script="x"),
            """sh(script:'''x''', returnStatus:false, returnStdout:false)""",
        )

        self.assertEqual(
            self.workflow.sh(script="x", returnStatus=True),
            """sh(script:'''x''', returnStatus:true, returnStdout:false)""",
        )

        self.assertEqual(
            self.workflow.sh(script="x", returnStdout=True),
            """sh(script:'''x''', returnStatus:false, returnStdout:true)""",
        )
