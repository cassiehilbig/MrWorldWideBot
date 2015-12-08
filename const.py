class MessageType:
    LINK = 'link'
    VIDEO = 'video'
    PICTURE = 'picture'
    TEXT = 'text'
    STICKER = 'sticker'
    GROUP = 'group'
    IS_TYPING = 'is-typing'
    NATIVE_PLATFORM = 'native-platform'
    DELIVERY_RECEIPT = 'delivery-receipt'
    PUSH_RECEIPT = 'push-receipt'
    READ_RECEIPT = 'read-receipt'
    SCAN_DATA = 'scan-data'
    APP_LINK = 'app-link'
    VIRAL = 'viral'

    ALL = [
        TEXT, STICKER, GROUP, IS_TYPING, NATIVE_PLATFORM,
        DELIVERY_RECEIPT, READ_RECEIPT, PUSH_RECEIPT, SCAN_DATA,
        APP_LINK, VIRAL
    ]
    ALL_CONTENT = [
        LINK, STICKER, NATIVE_PLATFORM
    ]
    ALL_NON_TRANSIENT = [
        LINK, TEXT, STICKER, GROUP, NATIVE_PLATFORM, APP_LINK, VIRAL, SCAN_DATA
    ]
    ALL_TRIGGERS_OPT_IN = [
        LINK, TEXT, STICKER, GROUP, SCAN_DATA, NATIVE_PLATFORM, PICTURE, VIDEO
    ]
    ALL_RECEIPT = [PUSH_RECEIPT, DELIVERY_RECEIPT, READ_RECEIPT]

    # all messages that can be filtered out instead of delivered to custom engine webhooks
    ALL_FILTERABLE = [IS_TYPING, READ_RECEIPT, PUSH_RECEIPT, DELIVERY_RECEIPT]


class MetricsEvent:
    IN_READ_RECEIPT = 'Received Read Receipt'
    IN_DELIVERY_RECEIPT = 'Received Delivery Receipt'
    IN_MESSAGE = 'Received User Reply'  # will include msg meta (body, etc)
    OUT_SIGNUP_RESPONSE = 'Sent Welcome Reply'  # include meta
    OUT_AUTO_RESPONSE = 'Sent Automatic Reply'  # include meta
    OUT_BLAST = 'Sent Broadcast Message'  # include meta
    TOTAL_SENT = 'Total Messages Sent'  # this will be calculated on our end


ALL_METRICS_EVENTS = [
    MetricsEvent.OUT_SIGNUP_RESPONSE,
    MetricsEvent.OUT_AUTO_RESPONSE,
    MetricsEvent.OUT_BLAST,
    MetricsEvent.IN_DELIVERY_RECEIPT,
    MetricsEvent.IN_READ_RECEIPT,
    MetricsEvent.IN_MESSAGE,
]

TOTAL_SENT_EVENTS = [
    MetricsEvent.OUT_SIGNUP_RESPONSE,
    MetricsEvent.OUT_AUTO_RESPONSE,
    MetricsEvent.OUT_BLAST,
]

TIME_SERIES_EVENTS = [
    MetricsEvent.OUT_SIGNUP_RESPONSE,
    MetricsEvent.OUT_AUTO_RESPONSE,
    MetricsEvent.OUT_BLAST,
    MetricsEvent.IN_READ_RECEIPT,
    MetricsEvent.IN_MESSAGE,
]


class TTL:
    MINUTE = 60
    HOUR = 3600
    DAY = 24 * HOUR
    MONTH = 30 * DAY
    YEAR = 365 * DAY


BOT_ID_REGEX = "^[a-z0-9_\.]{2,20}$"
USERNAME_REGEX = "^[\w\.]{2,30}$"
JID_REGEX = r'^(?:([\w\.]+)_\w{3}|(kikteam))@talk\.kik\.com$'
BYLINE_REGEX = "^.{0,40}$"
FIRST_NAME_REGEX = "^.{1,255}$"
LAST_NAME_REGEX = "^.{0,255}$"
UUID_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
USER_AGENT_REGEX = "^Kik\/([0-9]+\.[0-9]+)[0-9a-zA-Z.-]* \((iOS|Android) ([0-9]+\.[0-9]+)[0-9.]*\)$"
EMAIL_REGEX = "^\S+@\S+\.\S+$"
DISPLAY_NAME_REGEX = "^.{1,32}$"

# Source: https://gist.github.com/dperini/729294
URL_REGEX = (u"^"
             u"(?:(?:https?)://)"
             u"(?:\S+(?::\S*)?@)?"
             u"(?:"
             u"(?!(?:10|127)(?:\.\d{1,3}){3})"
             u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
             u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
             u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
             u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
             u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
             u"|"
             u"(?:(?:[a-zA-Z\u00a1-\uffff0-9]-*)*[a-zA-Z\u00a1-\uffff0-9]+)"
             u"(?:\.(?:[a-zA-Z\u00a1-\uffff0-9]-*)*[a-zA-Z\u00a1-\uffff0-9]+)*"
             u"(?:\.(?:[a-zA-Z\u00a1-\uffff]{2,}))"
             u")"
             u"(?::\d{2,5})?"
             u"(?:/\S*)?"
             u"$")

SHA1_REGEX = "^[0-9a-f]{40}$"
SHA256_REGEX = "^[0-9a-f]{64}$"

PICTURE_MESSAGE_MAX_IMAGE_SIZE = 960
PROFILE_PICTURE_MAX_IMAGE_SIZE = 640

# Taskqueues can't take more than 100KB, this is a little smaller to allow for headers
TASKQUEUE_MAX_LENGTH = 90 * 1024
