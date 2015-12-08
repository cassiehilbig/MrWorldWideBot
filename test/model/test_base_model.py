from datetime import datetime, timedelta
from google.appengine.ext import ndb

from test.test_base import TestBase
from lib.datetime_utils import datetime_to_utc_timestamp_millis
from model.base_model import BaseModel


class TestModel(BaseModel):
    text = ndb.TextProperty()
    integer = ndb.IntegerProperty()
    multi_text = ndb.TextProperty(repeated=True)


class TestRelatedModel(BaseModel):
    related = ndb.KeyProperty(kind=TestModel)


class TestTimestampModel(BaseModel):
    timestamp = ndb.DateTimeProperty()


class TestTimestampMultiModel(BaseModel):
    ts_list = ndb.DateTimeProperty(repeated=True)


class TestIncludeModel(BaseModel):
    _include = ['text1']
    text1 = ndb.TextProperty()
    text2 = ndb.TextProperty()


class BaseModelTest(TestBase):
    def test_get_or_create_existing(self):
        entity = TestModel.get_or_create('test')
        self.assertIsNotNone(entity)
        self.assertEqual(entity.key.id(), 'test')

    def test_get_or_create_new(self):
        TestModel(id='test').put()
        entity = TestModel.get_or_create('test')
        self.assertIsNotNone(entity)
        self.assertEqual(entity.key.id(), 'test')

    def test_get_or_create_kwargs(self):
        entity = TestModel.get_or_create('test', text='foo')
        self.assertIsNotNone(entity)
        self.assertEqual(entity.key.id(), 'test')
        self.assertEqual(entity.text, 'foo')

    def test_to_dict(self):
        tm = TestModel(text='abc', integer=123, multi_text=['a', 'b', '3'])
        tm.put()
        tm = tm.key.get()

        tm_dict = tm.to_dict()

        self.assertEqual(type(tm_dict['id']), long)
        self.assertEqual(tm_dict['text'], 'abc')
        self.assertEqual(tm_dict['integer'], 123)
        self.assertEqual(tm_dict['multi_text'], ['a', 'b', '3'])

    def test_to_dict_include(self):
        tm = TestModel(text='abc', integer=123, multi_text=['a', 'b', '3'])
        tm.put()
        tm = tm.key.get()

        tm_dict = tm.to_dict(include=['text', 'integer'])

        self.assertDictEqual(tm_dict, {
            'text': 'abc',
            'integer': 123
        })

    def test_to_dict_model_include(self):
        tm = TestIncludeModel(text1='abc', text2='def')
        tm.put()
        tm = tm.key.get()

        tm_dict = tm.to_dict()

        self.assertEqual(tm_dict['text1'], 'abc')
        self.assertNotIn('text2', tm_dict)

    def test_to_dict_fetch_keys(self):
        tm = TestModel(text='abc', integer=123, multi_text=['a', 'b', '3'])
        tm.put()
        tm = tm.key.get()
        trm = TestRelatedModel(related=tm.key)
        trm.put()

        trm_dict = trm.to_dict()
        self.assertEqual(type(trm_dict['related']['id']), long)
        self.assertEqual(trm_dict['related']['text'], 'abc')
        self.assertEqual(trm_dict['related']['integer'], 123)
        self.assertEqual(trm_dict['related']['multi_text'], ['a', 'b', '3'])

        trm_dict = trm.to_dict(fetch_keys=False)
        self.assertEqual(trm_dict['related'], tm.key.id())

    def test_timestamp_field(self):
        now = datetime.utcnow()
        tm = TestTimestampModel(timestamp=now)
        tm.put()
        tm = tm.key.get()

        tm_dict = tm.to_dict()

        self.assertEqual(tm_dict['timestamp'], datetime_to_utc_timestamp_millis(now))

    def test_timestamp_field_repeated(self):
        now = datetime.utcnow()
        five_mins_ago = now - timedelta(seconds=300)
        tm = TestTimestampMultiModel(ts_list=[now, five_mins_ago])
        tm.put()
        tm = tm.key.get()

        tm_dict = tm.to_dict()

        self.assertEqual(tm_dict['ts_list'][0], datetime_to_utc_timestamp_millis(now))
        self.assertEqual(tm_dict['ts_list'][1], datetime_to_utc_timestamp_millis(five_mins_ago))
