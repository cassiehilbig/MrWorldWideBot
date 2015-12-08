class StateTypes(object):
    """
    Class designed to let us hold a ton of constant strings so that we don't get import cycles for the sole purpose
    of avoiding hard-coding strings.
    """
    DEFAULT = 'default'

    LINK_WITH_KIK_SCAN = 'link-with-kik-begin'
    LINK_WITH_KIK_CONFIRM = 'link-confirm'

    LOGIN_WITH_KIK_SCAN = 'login-with-kik-begin'
    LOGIN_WITH_KIK_CONFIRM = 'login-confirm'

    MENU = 'menu'

    UPDATE_BOT_DISPLAY_NAME_SELECT_BOT = 'select-bot-update-display-name'
    UPDATE_BOT_DISPLAY_NAME_INPUT = 'update-bot-username'
    UPDATE_BOT_DISPLAY_NAME_CONFIRM = 'update-bot-username-confirmation'

    UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT = 'select-bot-update-profile-pic'
    UPDATE_BOT_PROFILE_PICTURE_INPUT = 'update-bot-profile-pic'
    UPDATE_BOT_PROFILE_PICTURE_CONFIRM = 'update-bot-profile-pic-confirmation'

    CREATE_BOT_USERNAME_SELECT = 'create-bot-choose-username'
    CREATE_BOT_USERNAME_CONFIRM = 'create-bot-confirm-username'
    CREATE_BOT_MORE_OPTIONS = 'create-bot-more-setup'
