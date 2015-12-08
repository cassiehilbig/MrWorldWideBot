class Config:

    # AppEngine supports queueing up 100 tasks at once
    MAX_TASKQUEUE_BATCH_SIZE = 100

    # Percentage of users to send metrics for
    METRICS_SAMPLING_RATE = 0.001

    DO_NOT_TRACK_FIELDS = [
        'previewImageData',
        'iconData',
        'body',
        'picUrl',
        'url',
        'appName',
        'title',
        'stickerUrl',
        'stickerPackId',
        'data',
        'text'
    ]

    MAX_BODY_LENGTH = 140
    MAX_TITLE_LENGTH = 140
    MAX_TEXT_LENGTH = 140

    BOTSWORTH_USERNAME = 'botsworth'

    EARLY_ACCESS_WHITELIST = ['remvst', 'eagerod', 'craig', 'newton.laura', 'laura', 'vasimr']
