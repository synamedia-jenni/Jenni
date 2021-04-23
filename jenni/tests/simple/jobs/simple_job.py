import jenni


class Job(jenni.models.PythonPipelineJobBase):
    def __init__(self):
        super().__init__(
            description="simple_job!",
            title="Simple Job",
        )
        self.count = jenni.models.params.IntParam(self, "count", "Number of things")
        self.logrotator_spec = "numToKeep(5)"
        self.throttleconcurrentbuilds_spec = "maxPerNode(1)"
        self.trigger_on_github_push = True

    def run(self):
        print("hello")
        assert self.count.value == 99
        self.workflow.stash("stash1", includes="inc1")
