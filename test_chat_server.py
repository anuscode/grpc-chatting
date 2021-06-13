import asyncio
import chat_pb2
import grpc_testing
import unittest
import unittest.mock as mock

from chat_server import ChatServicer
from chat_pb2 import Channel, Message, CreateChannelRequest, ListChannelsRequest, SendMessageRequest, StreamRequest
from channel_manager import ChannelManager
from google.protobuf.empty_pb2 import Empty


def async_test(coroutine):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coroutine(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


class TestChat(unittest.TestCase):
    def setUp(self):
        servicers = {
            chat_pb2.DESCRIPTOR.services_by_name['Chat']: ChatServicer(ChannelManager())
        }
        self.test_server = grpc_testing.server_from_dictionary(
            servicers, grpc_testing.strict_real_time())

    @asyncio.coroutine
    @mock.patch('channel_manager.ChannelManager.create')
    def test_create_channel(self, mock_create):
        """CreateChannel 호출 시 channel_manager.create 함수를 호출 하는지 확인 한다."""

        channel = Channel(id="mock_channel_id")
        request = CreateChannelRequest(channel=channel)

        create_channel = self.test_server.invoke_unary_unary(
            method_descriptor=(chat_pb2.DESCRIPTOR
                .services_by_name['Chat']
                .methods_by_name['CreateChannel']),
            invocation_metadata={},
            request=request, timeout=1)

        response, _, code, _ = create_channel.termination()
        self.assertEqual(response, Empty())
        self.assertEqual(code.name, "OK")
        self.assertEqual(mock_create.call_args_list, [mock.call("mock_channel_id")])

    @asyncio.coroutine
    @mock.patch('channel_manager.ChannelManager.list')
    def test_list_channels(self, mock_list):
        """ListChannels 호출 시 channels를 리턴 하는지 확인 한다."""

        request = ListChannelsRequest()
        mock_list.return_value = [
            "mock_user_1", "mock_user_2"
        ]
        list_channels = self.test_server.invoke_unary_unary(
            method_descriptor=(chat_pb2.DESCRIPTOR
                .services_by_name['Chat']
                .methods_by_name['ListChannels']),
            invocation_metadata={},
            request=request, timeout=1)

        response, _, code, _ = list_channels.termination()
        self.assertEqual(code.name, "OK")
        self.assertEqual(response.channel_ids, ['mock_user_1', 'mock_user_2'])
        self.assertEqual(mock_list.call_args_list, [mock.call()])

    @asyncio.coroutine
    @mock.patch('channel_manager.ChannelManager.append_message')
    def test_send_message(self, mock_append_message):
        """SendMessage 호출 시 ChannelManager.append_message 를 정상적으로 호출 하는지 확인 한다."""

        message = Message(user_id="mock_user_id", channel_id="Hot channel",
                          text="Hi, there.", is_broadcast=False)
        request = SendMessageRequest(message=message)

        send_message = self.test_server.invoke_unary_unary(
            method_descriptor=(chat_pb2.DESCRIPTOR
                .services_by_name['Chat']
                .methods_by_name['SendMessage']),
            invocation_metadata={},
            request=request, timeout=1)

        response, _, code, _ = send_message.termination()
        self.assertEqual(code.name, "OK")
        self.assertEqual(response, Empty())
        self.assertEqual(mock_append_message.call_args_list, [mock.call(message)])

    @asyncio.coroutine
    @mock.patch('channel_manager.ChannelManager.broadcast_message')
    def test_send_message_broadcast(self, mock_broadcast_message):
        """SendMessage 호출 시 ChannelManager.broadcast_message 를 정상적으로 호출 하는지 확인 한다."""

        message = Message(user_id="mock_user_id", channel_id="Hot channel",
                          text="Hi, there.", is_broadcast=True)
        request = SendMessageRequest(message=message)

        send_message = self.test_server.invoke_unary_unary(
            method_descriptor=(chat_pb2.DESCRIPTOR
                .services_by_name['Chat']
                .methods_by_name['SendMessage']),
            invocation_metadata={},
            request=request, timeout=1)

        response, _, code, _ = send_message.termination()
        self.assertEqual(code.name, "OK")
        self.assertEqual(response, Empty())
        self.assertEqual(mock_broadcast_message.call_args_list, [mock.call(message)])

    @asyncio.coroutine
    @mock.patch('channel_manager.ChannelManager.join')
    def test_stream(self, mock_join):
        """SendMessage 호출 시 ChannelManager.join을 정상적으로 호출 하는지 확인 한다."""

        channel = Channel(id="Great Channel")
        request = StreamRequest(user_id="yongwoo", channel=channel)

        send_message = self.test_server.invoke_unary_stream(
            method_descriptor=(chat_pb2.DESCRIPTOR
                .services_by_name['Chat']
                .methods_by_name['Stream']),
            invocation_metadata={},
            request=request, timeout=0.5)

        send_message.termination()
        self.assertEqual(mock_join.call_args_list, [mock.call("yongwoo", "Great Channel")])


if __name__ == '__main__':
    unittest.main()
