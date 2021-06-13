# Requirement

1. install

```
$ conda create -n grpc
$ conda activate grpc
$ pip install -r requirements.txt
```

# 실행 방법

```
서버 실행:
$ python chat_server.py

클라이언트 실행:
$ python chat_client.py 
```

# 사용자 가이드

1. 서버를 실행 하세요.

```
$ python chat_server.py
```

2. 다음 클라이언트를 실행 하세요.
```
"입장 하실 아이디를 입력 하세요." 라는 메세지를 만날 수 있습니다.
이때 원하는 아이디를 입력 후 접속하세요. ex) anuscode -> Enter
```

3. 아이디 입력 후 하단과 같은 메뉴 지침을 볼 수 있습니다.
```
하단의 메뉴를 보고 명령을 입력 하세요.
1. 채널 생성
2. 채널 리스트 보기
3. 채널 입장
```

4. 메뉴 상태에서 1 을 누르면
   "생성 하실 채널을 입력 하세요." 라는 메세지가 뜹니다.
   이 때 생성 하고 싶은 채널명을 입력.
```
ex) New channel name -> Enter
```

5. 이후 다시 메뉴로 돌아오면 2 를 입력 합니다. 그럼 다음과 같은 메세지가 뜹니다.
```
현재 생성 된 채널들..
New channel name, New channel name 2, New channel name 3
```

6. 마지막으로 3을 입력 후 채팅방명을 입력 하면 원하는 채팅방에 입장 할 수 있습니다.
   만약 생성 된 채팅방이 없다면 자동으로 생성 후 입장 합니다.
   메세지는 같은 채널에 있는 사람들만 공유 됩니다.
```
*단* /all 안녕하세요. 같은 식으로 입력 하면 채널에 상관 없이 모두에게 전파 됩니다.
```

# 소스코드 설명

1. chat_server.py

```
server endpoint 입니다.
channel 관리를 위해 channel_manager.ChannelManager 클래스를 주입 받습니다.
모든 채널 관리는 ChannelManager에게 위임 합니다.
```

2. channel_manager.py

```
AbstractChannel과 ChannelManager를 가지고 있는 모듈 입니다.
ChannelManager는 메모리상에서 채널들을 저장하고 관리합니다.
물론 입력 된 메세지 또한 이곳에서 관리 됩니다.

하단은 채널 자료구조 입니다.

channels {
    channel_1: {
        user_1: [Message, Message, Message],
        user_2: [Message, Message, Message]
    }
    channel_2: {
        user_3: [Message, Message],
        user_4: [Message]
    }
    
    ...
    
    channel_n: {
        user_n-1: [],
        user_n: [Message]
    }
}
새로운 메세지는 append() 되므로 끝자리에 위치 됩니다.
메세지를 읽는 경우 pop(0) 하므로 선입 선출 구조로 읽습니다.
일반 메세지가 오는 경우 해당되는 채널에 모든 유저에게 append 됩니다.
브로드캐스트 메세지가 오는 경우 모든 채널에 모든 유저에게 append 됩니다.

```

3. chat_client.py

```
클라이언트 모듈 입니다.
사용법은 상단의 사용법을 읽어 보세요.
```

4. test_channel_manager.py, test_chat_server.py

```
테스트 case들 입니다.
test_chat_server.py 의 경우 모든 테스트케이스에서 mock 처리 된 ChannelManager를 받습니다.
따라서 test_channel_manager.py 를 작성하여 별도의 검증을 하였습니다.
```

