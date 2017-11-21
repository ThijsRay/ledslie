import pytest

import ledslie.processors.typesetter
from ledslie.definitions import LEDSLIE_TOPIC_TYPESETTER_SIMPLE_TEXT, LEDSLIE_TOPIC_TYPESETTER_1LINE, \
    LEDSLIE_TOPIC_TYPESETTER_3LINES, LEDSLIE_TOPIC_SEQUENCES_PROGRAMS, LEDSLIE_TOPIC_SEQUENCES_UNNAMED
from ledslie.messages import TextSingleLineLayout, TextTripleLinesLayout, ImageSequence
from ledslie.processors.service import Config
from ledslie.processors.typesetter import Typesetter
from ledslie.tests.fakes import FakeMqttProtocol, FakeLogger


class TestTypesetter(object):

    @pytest.fixture
    def tsetter(self):
        endpoint = None
        factory = None
        s = Typesetter(endpoint, factory)
        s.protocol = FakeMqttProtocol()
        return s

    def test_on_connect(self, tsetter):
        ledslie.processors.typesetter.log = FakeLogger()
        protocol = FakeMqttProtocol()
        tsetter.connectToBroker(protocol)

    def test_typeset_simple_text(self, tsetter):
        topic = LEDSLIE_TOPIC_TYPESETTER_SIMPLE_TEXT
        payload = "Hello world!"
        assert 0 == len(tsetter.protocol._published_messages)
        tsetter.onPublish(topic, payload, qos=0, dup=False, retain=False, msgId=0)
        assert 1 == len(tsetter.protocol._published_messages)
        seq_topic, seq_data = tsetter.protocol._published_messages[-1]
        assert seq_topic == LEDSLIE_TOPIC_SEQUENCES_UNNAMED

    def test_ledslie_typesetter_1line(self, tsetter):
        topic = LEDSLIE_TOPIC_TYPESETTER_1LINE
        msg = TextSingleLineLayout()
        msg.text = 'Foo bar quux.'
        assert 0 == len(tsetter.protocol._published_messages)
        tsetter.onPublish(topic, bytes(msg), qos=0, dup=False, retain=False, msgId=0)
        assert 1 == len(tsetter.protocol._published_messages)
        seq_topic, seq_data = tsetter.protocol._published_messages[-1]
        assert seq_topic == LEDSLIE_TOPIC_SEQUENCES_UNNAMED

    def test_ledslie_typesetter_3lines(self, tsetter):
        topic = LEDSLIE_TOPIC_TYPESETTER_3LINES
        msg = TextTripleLinesLayout()
        msg.lines = ["One", "Two", "Three"]
        assert 0 == len(tsetter.protocol._published_messages)
        tsetter.onPublish(topic, bytes(msg), qos=0, dup=False, retain=False, msgId=0)
        assert 1 == len(tsetter.protocol._published_messages)
        seq_topic, seq_data = tsetter.protocol._published_messages[-1]
        assert seq_topic == LEDSLIE_TOPIC_SEQUENCES_UNNAMED

    def test_ledslie_typesetter_fields(self, tsetter):
        topic = LEDSLIE_TOPIC_TYPESETTER_1LINE
        msg = TextSingleLineLayout()
        msg.text = 'Foo bar quux.'
        msg.duration = 1000
        msg.program = 'foobar'
        assert 0 == len(tsetter.protocol._published_messages)
        tsetter.onPublish(topic, bytes(msg), qos=0, dup=False, retain=False, msgId=0)
        assert 1 == len(tsetter.protocol._published_messages)

        seq_topic, seq_data = tsetter.protocol._published_messages[-1]
        assert (LEDSLIE_TOPIC_SEQUENCES_PROGRAMS[:-1] + b"foobar") == seq_topic
        seq = ImageSequence().load(seq_data)
        assert 1000 == seq.duration
