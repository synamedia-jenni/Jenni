from jenni.tests.unittestutils import StepTestCase


class Tests(StepTestCase):
    def test_stash(self):
        with self.assertRaisesRegex(
            TypeError,
            r"""missing 2 required positional arguments: 'name' and 'includes""",
        ):
            # noinspection PyArgumentList
            self.workflow.stash()

        self.assertEqual(
            self.workflow.stash(name="x", includes="y"),
            """stash(name:'''x''', includes:'''y''')""",
        )

    def test_unstash(self):
        with self.assertRaisesRegex(TypeError, r"""missing 1 required positional argument: 'name"""):
            # noinspection PyArgumentList
            self.workflow.unstash()

        self.assertEqual(self.workflow.unstash(name="x"), """unstash(name:'''x''')""")
