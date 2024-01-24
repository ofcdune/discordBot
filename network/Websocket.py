from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.sync.client import connect
from json import loads, dumps
from threading import Event, Condition

import ssl

# todo: please remove in production
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class DiscordWebsocket:

    def __init__(self, global_event: Event):
        self.__url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.__websocket = None

        self.__last_message = {"op": -1}
        self.__s = None

        self.__resume_needed = False

        self.__event = global_event
        self.__local_mutex = Condition()

    @property
    def last_message(self):
        return self.__last_message

    @property
    def s(self):
        return self.__s

    @property
    def resume_needed(self):
        return self.__resume_needed

    def set_url(self, new_url):
        self.__url = new_url

    def send_message(self, message: dict):
        if not isinstance(message, dict):
            return

        self.__websocket.send(dumps(message))

    def receive_from_discord(self):
        self.__websocket = connect(self.__url, ssl_context=ssl_context)
        while self.__event.is_set():
            try:
                self.__local_mutex.acquire()
                self.__last_message = loads(self.__websocket.recv())
                self.__s = self.__last_message['s']
                self.__local_mutex.release()

            # todo: change the exception types to either resume or reconnect
            except ConnectionClosedError as e:
                self.__local_mutex.release()
                print(e)
                match e.code:
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4005 | 4007 | 4008:
                        self.__resume_needed = True
                        continue
                    case _:
                        self.__event.clear()
                        return
            except ConnectionClosedOK as e:
                self.__local_mutex.release()
                print(e)
                match e.code:
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4005 | 4007 | 4008:
                        self.__resume_needed = True
                        continue
                    case _:
                        self.__event.clear()
                        return

    def resume(self, resume_url: str, resume_message):
        self.__local_mutex.acquire()
        self.__resume_needed = False
        self.__websocket = connect(resume_url, ssl_context=ssl_context)
        self.send_message(resume_message)
        self.__local_mutex.release()
