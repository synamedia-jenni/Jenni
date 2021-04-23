import jenni


class Job(jenni.models.PythonPipelineJobBase):
    def __init__(self):
        super().__init__(description="job that should skip seed in CI", skip_seed=True)

    def run(self):
        print("hello")
