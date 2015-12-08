import mock
import pickle

from test.botsworth_test_base import BotsworthTestBase
from const import MessageType
from model import BotUser
from lib.states.create import ChooseUsernameState, ConfirmUsernameState, MoreSetupState
from lib.states.create.create_bot_flow import CreateBotStrings
from lib.states import DefaultState, UpdateDisplayNameState, UpdateProfilePictureState, MenuState
from lib.states.menu.menu_state import MenuStateStrings
from lib.states.state_types import StateTypes
from lib.admin_requests_mixin import UsernameAvailableCheckError, CreateBotError
from lib.botsworth_state_machine import state_machine
from lib.state_machine import State, PopTransition


class AlwaysPoppingTestState(State):
    @staticmethod
    def type():
        return 'pop-state'

    def on_message(self, message):
        return PopTransition([])


class ChooseUsernameStateTest(BotsworthTestBase):
    def test_static(self):
        self.assertEqual(ChooseUsernameState(None).type(), StateTypes.CREATE_BOT_USERNAME_SELECT)

    def test_not_text(self):
        BotUser(id='remvst', states=[ChooseUsernameState.type()]).put()
        incoming_message = {'type': MessageType.PICTURE, 'from': 'remvst', 'picUrl': 'http://yolo.fr'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remvst',
            'body': CreateBotStrings.CONFUSED_MESSAGE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('remvst').states, [ChooseUsernameState.type()])

    def test_cancel(self):
        BotUser(id='remvst', states=[MenuState.type(), ChooseUsernameState.type()]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'remvst', 'body': 'Cancel that yoyo'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remvst',
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('remvst').states, [MenuState.type()])

    def test_invalid_username(self):
        BotUser(id='remvst', states=[ChooseUsernameState.type()]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'remvst', 'body': 'I wanna create a bot, yo!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remvst',
            'body': CreateBotStrings.INVALID_USERNAME_MESSAGE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('remvst').states, [ChooseUsernameState.type()])

    @mock.patch('lib.states.create.create_bot_flow.ChooseUsernameState._check_username_available',
                side_effect=UsernameAvailableCheckError)
    def test_bot_id_available_check_error(self, check_available):
        BotUser(id='remvst', states=[ChooseUsernameState.type()]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'remvst', 'body': 'somebot'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remvst',
            'body': CreateBotStrings.ERROR_CHECKING_AVAILABILITY_MESSAGE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('remvst').states, [ChooseUsernameState.type()])

        self.assertEqual(check_available.call_count, 1)
        self.assertEqual(check_available.call_args[0][0], 'somebot')

    @mock.patch('lib.states.create.create_bot_flow.ChooseUsernameState._check_username_available',
                return_value={'available': False})
    def test_bot_id_not_available(self, check_available):
        BotUser(id='remvst', states=[ChooseUsernameState.type()]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'remvst', 'body': 'somebot'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remvst',
            'body': CreateBotStrings.UNAVAILABLE_MESSAGE.format('somebot'),
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('remvst').states, [ChooseUsernameState.type()])

        self.assertEqual(check_available.call_count, 1)
        self.assertEqual(check_available.call_args[0][0], 'somebot')

    @mock.patch('lib.states.create.create_bot_flow.ChooseUsernameState._check_username_available',
                return_value={'available': True})
    def test_bot_id_available(self, check_available):
        BotUser(id='remvst', states=[ChooseUsernameState.type()]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'remvst', 'body': 'somebot'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remvst',
            'body': CreateBotStrings.CONFIRM_MESSAGE.format('somebot'),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('remvst').states, [ConfirmUsernameState.type()])

        self.assertEqual(check_available.call_count, 1)
        self.assertEqual(check_available.call_args[0][0], 'somebot')


class ConfirmUsernameStateTest(BotsworthTestBase):
    def setUp(self):
        super(ConfirmUsernameStateTest, self).setUp()

        self.bot_username = 'somebot'
        self.user = BotUser(id='remvst',
                            states=[ConfirmUsernameState.type()],
                            state_data={ConfirmUsernameState.type(): {
                                'bot-username': self.bot_username
                            }})
        self.user.put()

    def test_static(self):
        self.assertEqual(ConfirmUsernameState(None).type(), StateTypes.CREATE_BOT_USERNAME_CONFIRM)

    def test_unmatched(self):
        incoming_message = {'type': MessageType.PICTURE, 'from': self.user.id, 'picUrl': 'http://picurl.com'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.CONFIRMATION_CONFUSED_MESSAGE.format(self.bot_username),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id(self.user.id).states, [ConfirmUsernameState.type()])

    def test_negative_answer(self):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'no'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.NEGATIVE_CONFIRMATION_MESSAGE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id(self.user.id)
        self.assertEqual(user.states, [ChooseUsernameState.type()])
        self.assertEqual(user.get_state_data(ConfirmUsernameState.type()), {})

    @mock.patch('lib.states.create.create_bot_flow.ConfirmUsernameState._create_bot', side_effect=CreateBotError)
    def test_positive_answer_error(self, create_bot):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'yes'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.CREATE_BOT_ERROR_RETRY_MESSAGE,
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id(self.user.id).states, [ConfirmUsernameState.type()])

        self.assertEqual(create_bot.call_count, 1)
        self.assertEqual(create_bot.call_args[1]['username'], self.user.id)
        self.assertEqual(create_bot.call_args[1]['bot_id'], self.bot_username)
        self.assertEqual(create_bot.call_args[1]['display_name'], self.bot_username)

    @mock.patch('lib.states.create.create_bot_flow.ConfirmUsernameState._create_bot', return_value={})
    def test_positive_answer_success(self, create_bot):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'yes'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.BOT_CREATED_MESSAGE.format(self.bot_username),
            'suggestedResponses': ['Set profile picture', 'Set display name', 'Menu']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id(self.user.id)
        self.assertEqual(user.states, [MoreSetupState.type()])
        self.assertEqual(user.get_state_data(ConfirmUsernameState.type()), {})

        self.assertEqual(create_bot.call_count, 1)
        self.assertEqual(create_bot.call_args[1]['username'], self.user.id)
        self.assertEqual(create_bot.call_args[1]['bot_id'], self.bot_username)
        self.assertEqual(create_bot.call_args[1]['display_name'], self.bot_username)


class MoreSetupStateTest(BotsworthTestBase):
    def test_static(self):
        self.assertEqual(MoreSetupState(None).type(), StateTypes.CREATE_BOT_MORE_OPTIONS)

    def setUp(self):
        super(MoreSetupStateTest, self).setUp()

        self.old_state_machine_states = pickle.dumps(state_machine._states)
        state_machine.register_state(AlwaysPoppingTestState)

        self.bot_username = 'somebot'
        self.user = BotUser(id='remvst',
                            states=[DefaultState.type(), MoreSetupState.type()],
                            state_data={MoreSetupState.type(): {
                                'bot-username': self.bot_username
                            }})
        self.user.put()

    def tearDown(self):
        super(MoreSetupStateTest, self).tearDown()
        state_machine._states = pickle.loads(self.old_state_machine_states)

    def test_cancel(self):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'cancel'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.MORE_SETUP_BACK_MESSAGE,
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id(self.user.id)
        self.assertEqual(user.states, [DefaultState.type()])
        self.assertEqual(user.get_state_data(MoreSetupState.type()), {})

    def test_confused(self):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'poop'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.MORE_SETUP_CONFUSED_MESSAGE,
            'suggestedResponses': ['Set profile picture', 'Set display name', 'Menu']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id(self.user.id).states, [DefaultState.type(), MoreSetupState.type()])

    def test_profile_pic(self):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'pic'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.SET_PICTURE_MESSAGE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id(self.user.id)
        self.assertEqual(user.states, [DefaultState.type(), MoreSetupState.type(), UpdateProfilePictureState.type()])
        self.assertEqual(user.get_state_data(UpdateProfilePictureState.type())['bot-username'], self.bot_username)

    def test_display_name(self):
        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'name'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.SET_DISPLAY_NAME_MESSAGE,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id(self.user.id)
        self.assertEqual(user.states, [DefaultState.type(), MoreSetupState.type(), UpdateDisplayNameState.type()])
        self.assertEqual(user.get_state_data(UpdateDisplayNameState.type())['bot-username'], self.bot_username)

    def test_on_resume(self):
        self.user.states.append(AlwaysPoppingTestState.type())
        self.user.put()

        incoming_message = {'type': MessageType.TEXT, 'from': self.user.id, 'body': 'resume yo or ill kill u'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': self.user.id,
            'body': CreateBotStrings.MORE_SETUP_MESSAGE,
            'suggestedResponses': ['Set profile picture', 'Set display name', 'Menu']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id(self.user.id)
        self.assertEqual(user.states, [DefaultState.type(), MoreSetupState.type()])
