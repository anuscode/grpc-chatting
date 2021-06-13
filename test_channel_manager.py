import chat_pb2
import grpc_testing
import unittest

from chat_server import ChatServicer
from chat_pb2 import Message
from channel_manager import ChannelManager


class TestChannelManager(unittest.TestCase):
    def setUp(self):
        servicers = {
            chat_pb2.DESCRIPTOR.services_by_name['Chat']: ChatServicer(ChannelManager())
        }
        self.test_server = grpc_testing.server_from_dictionary(
            servicers, grpc_testing.strict_real_time())

    def test_create(self):
        manager = ChannelManager()
        channel_id = "New Channel"
        manager.create(channel_id)
        channel = manager.get(channel_id)
        self.assertDictEqual(channel, dict(), "A created channel must be empty dict")

    def test_delete(self):
        pass

    def test_has_message(self):
        manager = ChannelManager()
        channel_id = "New Channel"
        user_id = "mock_user_id"
        text = "lorem ipsum text"

        # 유저가 없을 땐 메세지가 적재 되지 않는다.
        manager.create(channel_id)
        manager.append_message(
            Message(channel_id=channel_id, user_id=user_id, text=text, is_broadcast=False)
        )
        self.assertFalse(manager.has_message(user_id, channel_id))

        # 유저가 있을 땐 메세지가 적재 된다.
        manager.join(user_id, channel_id)
        manager.append_message(
            Message(channel_id=channel_id, user_id=user_id, text=text, is_broadcast=False)
        )
        self.assertTrue(manager.has_message(user_id, channel_id))

    def test_has(self):
        manager = ChannelManager()
        channel_id = "New Channel"

        self.assertFalse(manager.has(channel_id))

        manager.create(channel_id)
        self.assertTrue(manager.has(channel_id))

    def test_list(self):
        manager = ChannelManager()
        manager.create("Channel_1")
        manager.create("Channel_2")
        channels = manager.list()
        self.assertEqual(len(channels), 2)

    def test_get(self):
        manager = ChannelManager()
        channel_id = "New Channel"
        manager.create(channel_id)
        channel = manager.get(channel_id)
        self.assertDictEqual(channel, dict(), "A created channel must be empty dict")

    def test_join(self):
        manager = ChannelManager()
        manager.create("channel_1")
        manager.join("user_1", "channel_1")
        channel_1 = manager.get("channel_1")

        self.assertTrue("user_1" in channel_1)
        self.assertEqual(len(channel_1.keys()), 1)

        manager.join("user_2", "channel_1")
        self.assertTrue("user_2" in channel_1)
        self.assertEqual(len(channel_1.keys()), 2)

        manager.create("channel_2")
        channel_2 = manager.get("channel_2")
        manager.join("user_3", "channel_2")
        manager.join("user_4", "channel_2")

        self.assertTrue("user_3" in channel_2)
        self.assertTrue("user_4" in channel_2)
        self.assertEqual(len(channel_2.keys()), 2)

        # channel_2는 기존에 존재하고 있던 channel_1 에 영향을 주지 않아야 한다.
        self.assertTrue("user_1" in channel_1)
        self.assertTrue("user_2" in channel_1)
        self.assertEqual(len(channel_1.keys()), 2)

    def test_append_message(self):
        manager = ChannelManager()
        manager.create("channel_1")
        manager.join("user_1", "channel_1")
        manager.append_message(Message(
            channel_id="channel_1", user_id="user_1",
            text="Dummy ipsum lorem 1", is_broadcast=False)
        )
        manager.append_message(Message(
            channel_id="channel_1", user_id="user_1",
            text="Dummy ipsum lorem 2", is_broadcast=False)
        )

        channel_1 = manager.get("channel_1")
        messages = channel_1["user_1"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].text, "Dummy ipsum lorem 1")
        self.assertEqual(messages[1].text, "Dummy ipsum lorem 2")

    def test_pop_message(self):
        manager = ChannelManager()

        manager.create("channel_1")
        manager.join("user_1", "channel_1")
        manager.append_message(Message(
            channel_id="channel_1", user_id="user_1",
            text="Dummy ipsum lorem 1", is_broadcast=False)
        )
        manager.append_message(Message(
            channel_id="channel_1", user_id="user_1",
            text="Dummy ipsum lorem 2", is_broadcast=False)
        )
        manager.append_message(Message(
            channel_id="channel_1", user_id="user_1",
            text="Dummy ipsum lorem 3", is_broadcast=False)
        )

        message1 = manager.pop_message("user_1", "channel_1")
        message2 = manager.pop_message("user_1", "channel_1")
        message3 = manager.pop_message("user_1", "channel_1")

        self.assertEqual(message1.text, "Dummy ipsum lorem 1")
        self.assertEqual(message2.text, "Dummy ipsum lorem 2")
        self.assertEqual(message3.text, "Dummy ipsum lorem 3")

    def test_broadcast_message(self):
        manager = ChannelManager()

        manager.create("channel_1")
        manager.join("user_1", "channel_1")
        manager.join("user_2", "channel_1")

        manager.create("channel_2")
        manager.join("user_3", "channel_2")
        manager.join("user_4", "channel_2")

        manager.broadcast_message(Message(
            channel_id="not existing channel", user_id="someone",
            text="Dummy broadcast message", is_broadcast=True))

        channel_1 = manager.get("channel_1")
        channel_2 = manager.get("channel_2")

        # all of 2 channels with 4 users must be received to a broadcast message
        self.assertEqual(len(channel_1["user_1"]), 1)
        self.assertEqual(len(channel_1["user_2"]), 1)
        self.assertEqual(len(channel_2["user_3"]), 1)
        self.assertEqual(len(channel_2["user_4"]), 1)


if __name__ == '__main__':
    unittest.main()
