import mock

from test.botsworth_test_base import BotsworthTestBase
from const import MessageType
from lib.admin_requests_mixin import UpdateProfilePictureError
from lib.states.menu.menu_state import MenuStateStrings
from lib.states.update_profile_picture.update_profile_picture_flow import UpdateProfilePictureStateStrings
from lib.states.state_types import StateTypes
from model import BotUser


class SelectBotUpdateProfilePictureStateTest(BotsworthTestBase):
    def test_start_flow(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU]
        user.put()
        self.route_urlfetch_response(
            'get',
            'http://localhost:8080/api/v1/botsworth/admin?username=aleem',
            content='{"bots": [{"id": "abotid"}]}'
        )

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'update my pic?'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': MenuStateStrings.UPDATE_PROFILE_PICTURE,
            'suggestedResponses': ['abotid', 'Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states,
                         [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT])

    def test_flow_started_answer_with_good_bot_name(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT]
        user.put()
        self.route_urlfetch_response(
            'get',
            'http://localhost:8080/api/v1/botsworth/admin?username=aleem',
            content='{"bots": [{"id": "abotid"}]}'
        )

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'abotid'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateProfilePictureStateStrings.SELECTED_BOT_NAME.format('abotid'),
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT)['bot-username'], 'abotid')
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT), {})
        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT])

    def test_flow_started_answer_with_cancel(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT]
        user.put()
        self.route_urlfetch_response(
            'get',
            'http://localhost:8080/api/v1/botsworth/admin?username=aleem',
            content='{"bots": [{"id": "abotid"}]}'
        )

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'cancel'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU])

    def test_update_profile_picture_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.PICTURE, 'picUrl': 'http://example.com/i.png'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateProfilePictureStateStrings.PROFILE_PICTURE_CONFIRMATION_MESSAGE.format('abotid'),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.get_state_data('update-bot-profile-pic-confirmation')['bot-username'], 'abotid')
        self.assertEqual(
            user.get_state_data('update-bot-profile-pic-confirmation')['profile-picture-url'],
            'http://example.com/i.png'
        )
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT), {})
        self.assertEqual(user.states, [StateTypes.MENU, 'update-bot-profile-pic-confirmation'])

    def test_update_profile_picture_text_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Can it be a kitten?'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateProfilePictureStateStrings.PROFILE_PICTURE_INVALID_MESSAGE_TYPE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states,
                         [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT])

    def test_update_profile_picture_cancel_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT)['bot-username'] = 'abotid'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Cancel'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU])

    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._update_bot_profile_picture')
    def test_update_profile_picture_positive_confirmation_message(self, update_profile_picture):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['profile-picture-url'] = 'http://e.com/i.png'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Yeah'}
        outgoing_message_profile_picture = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': UpdateProfilePictureStateStrings.PROFILE_PICTURE_UPDATE_SUCCESS.format('abotid')
        }
        outgoing_message_menu = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message_profile_picture, outgoing_message_menu])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU])
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM), {})

    def test_update_profile_picture_negative_confirmation_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['profile-pic'] = 'Superman'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'No'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateProfilePictureStateStrings.PROFILE_PICTURE_REPLACEMENT_MESSAGE.format('abotid'),
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT])
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM), {})
        self.assertEqual(user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT), {'bot-username': 'abotid'})

    @mock.patch(
        'lib.admin_requests_mixin.AdminRequestsMixin._update_bot_profile_picture',
        side_effect=UpdateProfilePictureError
    )
    def test_update_profile_picture_confirmation_error(self, update_profile_picture):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['profile-picture-url'] = 'http://e.com/i.png'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Yea'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateProfilePictureStateStrings.PROFILE_PICTURE_UPDATE_ERROR,
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM])

    def test_update_profile_picture_confirmation_unknown_message(self):
        user = BotUser(id='aleem')
        user.states = [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM]
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['bot-username'] = 'abotid'
        user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM)['profile-picture-url'] = 'http://e.com/i.png'
        user.put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'Potato'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': UpdateProfilePictureStateStrings.PROFILE_PICTURE_CONFIRMATION_UNKNOWN_MESSAGE.format(
                'abotid', 'Superman'
            ),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')

        self.assertEqual(user.states, [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM])
