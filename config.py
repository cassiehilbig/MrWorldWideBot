import os


class Config:

    # AppEngine supports queueing up 100 tasks at once
    MAX_TASKQUEUE_BATCH_SIZE = 100

    BOT_USERNAME = os.environ['BOT_USERNAME']
    BOT_API_KEY = os.environ['BOT_API_KEY']
