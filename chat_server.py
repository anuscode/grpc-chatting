import asyncio
import chat_pb2
import chat_pb2_grpc
import grpc
import time

from concurrent import futures
from channel_manager import AbstractChannel, ChannelManager
from google.protobuf.empty_pb2 import Empty


class ChatServicer(chat_pb2_grpc.ChatServicer):

    def __init__(self, channel_manager: AbstractChannel):
        assert isinstance(channel_manager, AbstractChannel)
        self.channel_manager = channel_manager

    async def CreateChannel(self, request, context: grpc.aio.ServicerContext):
        channel = request.channel
        channel.created_at = int(time.time())
        self.channel_manager.create(channel.id)
        return Empty()

    async def ListChannels(self, request, context: grpc.aio.ServicerContext):
        channel_ids = self.channel_manager.list()
        response = chat_pb2.ListChannelsResponse(channel_ids=channel_ids)
        return response

    async def SendMessage(self, request, context: grpc.aio.ServicerContext):
        """Appends into Channels by channel_id -> Channel by user_id -> Messages. """
        message = request.message
        is_broadcast = message.is_broadcast
        if is_broadcast:
            self.channel_manager.broadcast_message(message)
        else:
            self.channel_manager.append_message(message)
        return Empty()

    def Stream(self, request, context: grpc.aio.ServicerContext):
        """Reads Messages by user_id in Channel by channel_id in Channels if exists."""
        user_id = request.user_id
        channel_id = request.channel.id

        self.channel_manager.join(user_id, channel_id)

        while True:
            if not self.channel_manager.has_message(user_id, channel_id):
                time.sleep(0.1)
                continue
            message = self.channel_manager.pop_message(user_id, channel_id)
            yield chat_pb2.StreamResponse(message=message)


async def serve() -> None:
    servicer = ChatServicer(ChannelManager())
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(servicer, server)

    server.add_insecure_port('[::]:50051')
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


if __name__ == '__main__':
    asyncio.run(serve())
