from jenni.tests.unittestutils import StepTestCase


class Tests(StepTestCase):
    def test_build(self):
        self.assertEqual(
            self.workflow.build(job="x"),
            """build(job:'x', propagate:true, wait:true)""",
        )

        self.assertEqual(
            self.workflow.build(job="x", propagate=False),
            """build(job:'x', propagate:false, wait:true)""",
        )

        self.assertEqual(
            self.workflow.build(job="x", wait=False),
            """build(job:'x', propagate:true, wait:false)""",
        )

        self.assertEqual(
            self.workflow.build(job="x", wait=False, parameters=[["string", "s1", "v1"]]),
            """build(job:'x', propagate:true, wait:false, parameters: [[$class: 'StringParameterValue', name: 's1', value: 'v1']])""",
        )

        self.assertEqual(
            self.workflow.build(job="x", wait=False, parameters=[["bool", "s1", True]]),
            """build(job:'x', propagate:true, wait:false, parameters: [[$class: 'BooleanParameterValue', name: 's1', value: true]])""",
        )

        self.assertEqual(
            self.workflow.build(job="x", wait=False, parameters=[["text", "s1", "v1"]]),
            """build(job:'x', propagate:true, wait:false, parameters: [[$class: 'TextParameterValue', name: 's1', value: 'v1']])""",
        )

        self.assertEqual(
            self.workflow.build(
                job="x",
                wait=False,
                parameters=[["string", "s1", "v1"], ["text", "s1", "v1"]],
            ),
            """build(job:'x', propagate:true, wait:false, parameters: [[$class: 'StringParameterValue', name: 's1', value: 'v1'],
[$class: 'TextParameterValue', name: 's1', value: 'v1']])""",
        )
