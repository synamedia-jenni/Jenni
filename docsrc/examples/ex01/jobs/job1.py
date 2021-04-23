from jenni.models import GroovyJobBase


class Job(GroovyJobBase):
    def __init__(self):
        super().__init__(description="A very simple job!", trigger_cron_spec="H 8 * * *")
        self.code(f"echo 'hello from {self.name}';")
        self.include("job1.groovy")
