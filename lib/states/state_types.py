class StateTypes(object):
    """
    Class designed to let us hold a ton of constant strings so that we don't get import cycles for the sole purpose
    of avoiding hard-coding strings.
    """
    DEFAULT = 'default'
    MENU = 'menu'
    CHOOSE_COLOR = 'choose-color'
    CONFIRM_COLOR = 'confirm-color'
    SENT_PICTURE = 'sent-picture'
    GENERIC = 'foo'
    ALWAYS_POPPING = 'pop'
    CHOOSE_LANGUAGE = 'choose-language'
    INPUT_TEXT_TOTRANSLATE = 'input-text-totranslate'
