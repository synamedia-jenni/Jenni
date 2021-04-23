import jenni


class Job(jenni.models.GroovyJobBase):
    def __init__(self):
        super(Job, self).__init__()
        self.code("""  {python("'echo 123'")}   """)
