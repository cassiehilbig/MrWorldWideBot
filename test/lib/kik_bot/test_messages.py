from test.test_base import TestBase
from const import MessageType
from lib.kik_bot import make_text_message, make_link_message, make_video_message


class KikBotMessagesTest(TestBase):
    def test_make_text_message(self):
        message = make_text_message('Some text', 'eagerod')
        self.assertEqual(message, {
            'type': MessageType.TEXT,
            'to': 'eagerod',
            'body': 'Some text'
        })

    def test_make_text_message_suggested_responses(self):
        message = make_text_message('Some text', 'eagerod', suggested_responses=['A', 'B', 'C'])
        self.assertEqual(message, {
            'type': MessageType.TEXT,
            'to': 'eagerod',
            'body': 'Some text',
            'suggestedResponses': ['A', 'B', 'C']
        })

    def test_make_link_message(self):
        message = make_link_message('http://foo.bar', 'A Title', 'Some text', 'eagerod')
        self.assertEqual(message, {
            'type': MessageType.LINK,
            'to': 'eagerod',
            'url': 'http://foo.bar',
            'title': 'A Title',
            'text': 'Some text'
        })

    def test_make_link_message_suggested_responses(self):
        message = make_link_message(
            'http://foo.bar', 'A Title', 'Some text', 'eagerod', suggested_responses=['A', 'B', 'C']
        )
        self.assertEqual(message, {
            'type': MessageType.LINK,
            'to': 'eagerod',
            'url': 'http://foo.bar',
            'title': 'A Title',
            'text': 'Some text',
            'suggestedResponses': ['A', 'B', 'C']
        })

    def test_make_video_message(self):
        message = make_video_message('avideoid', 'eagerod')
        self.assertEqual(message, {
            'type': MessageType.VIDEO,
            'to': 'eagerod',
            'videoId': 'avideoid',
            'muted': False,
            'loop': False,
            'autoplay': False
        })

    def test_make_video_message_suggested_responses(self):
        message = make_video_message('avideoid', 'eagerod', suggested_responses=['A', 'B', 'C'])
        self.assertEqual(message, {
            'type': MessageType.VIDEO,
            'to': 'eagerod',
            'videoId': 'avideoid',
            'muted': False,
            'loop': False,
            'autoplay': False,
            'suggestedResponses': ['A', 'B', 'C']
        })
