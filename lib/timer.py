from datetime import datetime


class Timer:
    def __enter__(self):
        self.start = datetime.now()
        return self

    def __exit__(self, *args):
        self.end = datetime.now()
        self.interval = int(round((self.end - self.start).total_seconds() * 1000))

    def start(self):
        return self.__enter__()

    def stop(self):
        return self.__exit__()
