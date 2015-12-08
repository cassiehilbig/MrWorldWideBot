from lib.base_handler import BaseHandler


class WarmupHandler(BaseHandler):
    """
    Warmup
    """

    def get(self):
        self.respond({})


routes = [
    (r'/_ah/warmup', WarmupHandler)
]
