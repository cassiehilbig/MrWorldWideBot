class MessageType(object):
    TEXT = 'text'
    LINK = 'link'
    VIDEO = 'video'
    PICTURE = 'picture'
    STICKER = 'sticker'
    SCAN_DATA = 'scan-data'
    IS_TYPING = 'is-typing'
    DELIVERY_RECEIPT = 'delivery-receipt'
    READ_RECEIPT = 'read-receipt'

    ALL = [TEXT, LINK, VIDEO, PICTURE, STICKER, SCAN_DATA, IS_TYPING, DELIVERY_RECEIPT, READ_RECEIPT]
    TRANSIENT = [IS_TYPING, DELIVERY_RECEIPT, READ_RECEIPT]
    NON_TRANSIENT = [TEXT, LINK, VIDEO, PICTURE, STICKER, SCAN_DATA]
    CONTENT = [LINK, VIDEO, PICTURE, STICKER]
