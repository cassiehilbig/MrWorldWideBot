import os
import json
import requests



class Config(object):
    # AppEngine supports queueing up 100 tasks at once
    MAX_TASKQUEUE_BATCH_SIZE = 100

    # Taskqueues can't take more than 100KB, this is a little smaller to allow for headers
    TASKQUEUE_MAX_LENGTH = 90 * 1024

    BOT_USERNAME = os.environ.get('BOT_USERNAME', 'mrworldwidebot')
    BOT_API_KEY = os.environ.get('BOT_API_KEY', '0a4ca262-4274-424f-ab9e-4666e0d0751b')
    MIXPANEL_TOKEN = os.environ.get('MIXPANEL_TOKEN')