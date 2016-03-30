class MessageType(object):
    TEXT = 'text'
    GROUP = 'group'
    LINK = 'link'
    VIDEO = 'video'
    PICTURE = 'picture'
    STICKER = 'sticker'
    NATIVE_PLATFORM = 'native-platform'
    SCAN_DATA = 'scan-data'
    APP_LINK = 'app-link'
    VIRAL = 'viral'
    IS_TYPING = 'is-typing'
    DELIVERY_RECEIPT = 'delivery-receipt'
    PUSH_RECEIPT = 'push-receipt'
    READ_RECEIPT = 'read-receipt'

    ALL = [TEXT, GROUP, LINK, VIDEO, PICTURE, STICKER, NATIVE_PLATFORM, SCAN_DATA, APP_LINK, VIRAL, IS_TYPING,
           DELIVERY_RECEIPT, PUSH_RECEIPT, READ_RECEIPT]
    TRANSIENT = [IS_TYPING, DELIVERY_RECEIPT, PUSH_RECEIPT, READ_RECEIPT]
    NON_TRANSIENT = [TEXT, GROUP, LINK, VIDEO, PICTURE, STICKER, NATIVE_PLATFORM, SCAN_DATA, APP_LINK, VIRAL]
    CONTENT = [LINK, VIDEO, PICTURE, STICKER, NATIVE_PLATFORM]
