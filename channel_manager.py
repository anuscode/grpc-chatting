from abc import ABC, abstractmethod
from chat_pb2 import Channel, Message


class AbstractChannel(ABC):

    @abstractmethod
    def create(self, channel_id: str):
        pass

    @abstractmethod
    def delete(self, channel_id: str):
        pass

    @abstractmethod
    def has_message(self, user_id, channel_id) -> bool:
        pass

    @abstractmethod
    def has(self, channel_id: str) -> bool:
        pass

    @abstractmethod
    def list(self) -> list:
        pass

    @abstractmethod
    def get(self, channel_id: str) -> Channel:
        pass

    @abstractmethod
    def join(self, user_id: str, channel_id: str):
        pass

    @abstractmethod
    def append_message(self, message: Message):
        pass

    @abstractmethod
    def broadcast_message(self, message: Message):
        pass

    @abstractmethod
    def pop_message(self, user_id: str, channel_id: str):
        pass


class ChannelManager(AbstractChannel):
    def __init__(self):
        self._channels = {}

    def create(self, channel_id: str):
        if self.has(channel_id):
            return

        self._channels[channel_id] = dict()

    def delete(self, channel_id: str):
        pass

    def has(self, channel_id: str) -> bool:
        return channel_id in self._channels

    def list(self) -> list:
        channel_ids = list(self._channels.keys())
        return channel_ids

    def get(self, channel_id: str) -> Channel:
        if not self.has(channel_id):
            return None

        return self._channels[channel_id]

    def join(self, user_id: str, channel_id: str):
        # 존재하지 않는 채널에 입장 시 생성 하고 조인.
        if not self.has(channel_id):
            self.create(channel_id)

        channel: dict = self.get(channel_id)
        channel[user_id] = []

    def broadcast_message(self, message: Message):
        for channel in self._channels.values():
            for user_id in channel.keys():
                messages = channel[user_id]
                messages.append(message)

    def append_message(self, message: Message):
        channel_id = message.channel_id
        channel: dict = self.get(channel_id)
        for user_id in channel.keys():
            channel[user_id].append(message)

    def has_message(self, user_id, channel_id) -> bool:
        channel = self.get(channel_id)
        if channel:
            messages = channel.get(user_id, [])
            return len(messages) > 0
        return False

    def pop_message(self, user_id: str, channel_id: str) -> Message:
        channel: dict = self.get(channel_id)
        messages = channel[user_id]
        message = messages.pop(0)
        return message
