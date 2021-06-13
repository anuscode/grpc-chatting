from __future__ import print_function

import grpc

from chat_pb2 import ListChannelsRequest, CreateChannelRequest, SendMessageRequest, StreamRequest, Channel, Message
import chat_pb2_grpc
import threading


class Client:
    def __init__(self, user_id):
        self.grpc_channel = grpc.insecure_channel("localhost:50051")
        # create new listening thread for when new message streams come in
        self.listener = threading.Thread(target=self._listen_for_messages, daemon=True)
        self.channel_id = None
        self.user_id = user_id

    def _listen_for_messages(self):
        channel = Channel(id=self.channel_id)
        stub = chat_pb2_grpc.ChatStub(self.grpc_channel)
        for response in stub.Stream(StreamRequest(user_id=self.user_id, channel=channel)):
            message = response.message
            print("{0}: {1}".format(message.user_id, message.text))

    def join_channel(self):
        print("입장 하실 채널을 입력 하세요.")
        self.channel_id = str(input()).strip()
        self.listener.start()
        print("{0} 채널에 입장 하였습니다.".format(self.channel_id))
        print("\n")

        while True:
            text = str(input()).strip()
            self.send_message(text)

    def exit_channel(self):
        pass

    def create_channel(self):
        print("생성 하실 채널을 입력 하세요.")
        channel_id = str(input()).strip()
        stub = chat_pb2_grpc.ChatStub(self.grpc_channel)
        channel_to_join = Channel(id=channel_id)
        request = CreateChannelRequest(channel=channel_to_join)
        stub.CreateChannel(request)
        print("{0} 채널을 생성 하였습니다.".format(channel_id))
        print("\n")

    def list_channels(self):
        stub = chat_pb2_grpc.ChatStub(self.grpc_channel)
        request = ListChannelsRequest()
        response = stub.ListChannels(request)
        print("현재 생성 된 채널들..")
        print(", ".join(response.channel_ids))
        print("\n")

    def send_message(self, text):
        is_broadcast = False
        if text[:4] == "/all":
            text = text[5:]
            is_broadcast = True

        message = Message(channel_id=self.channel_id, user_id=self.user_id, text=text, is_broadcast=is_broadcast)
        stub = chat_pb2_grpc.ChatStub(self.grpc_channel)
        stub.SendMessage(SendMessageRequest(message=message))


def run():
    print("입장 하실 아이디를 입력 하세요.")
    user_id = str(input()).strip()
    print("\n")
    client = Client(user_id)
    while True:
        print("하단의 메뉴를 보고 명령을 입력 하세요.")
        print("1. 채널 생성")
        print("2. 채널 리스트 보기")
        print("3. 채널 입장")
        selection = int(input())
        print("\n")

        if selection == 1:
            client.create_channel()

        if selection == 2:
            client.list_channels()

        if selection == 3:
            client.join_channel()


if __name__ == '__main__':
    run()
