from random import random
from time import sleep

from websockets import ConnectionClosedError, ConnectionClosedOK
from websockets.sync.client import connect

from threading import Thread, Condition as Mutex, Event
from json import loads, dumps

import ssl

# todo: please remove in production
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class DiscordGateway:

    def __init__(self, token: str, url: str, global_mutex: Mutex, global_event: Event):
        self.__token = token
        self.__url = url

        self.__websocket = None
        self.__mutex = global_mutex
        self.__event = global_event
        self.__watchmen = {7: self.resume}
        self.__state = 0

        self.__last_message = {"op": -1}
        self.__s = None

        self.__session_id = None
        self.__resume_url = None

        self.__event.set()

    @property
    def mutex(self):
        return self.__mutex

    @property
    def event(self):
        return self.__event

    @property
    def last_message(self):
        return self.__last_message

    @property
    def s(self):
        return self.__s

    def register(self, arg, callback):
        self.__watchmen[arg] = callback

    def thread_with_teardown(self, target, *args, **kwargs):
        def startwithtd(*arg, **kwarg):
            target(*arg, **kwarg)
            self.teardown()

        thread = Thread(target=startwithtd, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def teardown(self):
        self.__event.clear()
        self.__state = 0
        self.__event.set()
        self.start()

    def __wait_for_opcode(self, opcode):
        self.__mutex.acquire()
        while self.__last_message["op"] != opcode:
            sleep(.1)
        self.__mutex.release()

    def send_message(self, message: dict):
        if not isinstance(message, dict):
            return

        self.__websocket.send(dumps(message))

    def __receive_from_discord(self):
        self.__websocket = connect(self.__url, ssl_context=ssl_context)
        while self.__event.is_set():
            try:
                self.__mutex.acquire()
                self.__last_message = loads(self.__websocket.recv())
                self.__s = self.__last_message['s']
                self.__mutex.release()

            except ConnectionClosedError as e:
                self.__mutex.release()
                print(e)
                match e.code:
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4005 | 4007 | 4008:
                        self.resume()
                    case _:
                        self.__event.clear()
                        return

            except ConnectionClosedOK as e:
                self.__mutex.release()
                print(e)
                match e.code:
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4005 | 4007 | 4008:
                        self.resume()
                    case _:
                        self.__event.clear()
                        return

            callback = self.__watchmen.get(self.__last_message["op"])
            if callback is not None:
                self.thread_with_teardown(callback, self.__last_message['d'])

            callback = self.__watchmen.get(self.__last_message["t"])
            if callback is not None:
                self.thread_with_teardown(callback, self.__last_message['d'])

    def resume(self):
        message = {
                "op": 6,
                'd': {
                    "token": self.__token,
                    "session_id": self.__session_id,
                    "seq": self.__s
                }
            }

        self.__mutex.acquire()
        self.__websocket = connect(self.__resume_url, ssl_context=ssl_context)
        self.send_message(message)
        self.__mutex.release()

    def start(self):

        # establish a connection with the discord websocket
        self.thread_with_teardown(self.__receive_from_discord)
        self.__state = 1

        # discord responds with OP code 10
        self.__wait_for_opcode(10)
        self.__state = 2

        self.__mutex.acquire()
        interval = self.__last_message['d']["heartbeat_interval"]
        self.__mutex.release()

        hbt = HeartbeatThread(
            interval,
            self,
        )

        # we start sending heartbeats to the websocket
        self.thread_with_teardown(hbt.heartbeat)
        self.register(11, hbt.ack_heartbeat)

        # we send the register message with the bot token and our initial presence
        self.__websocket.send_message({
            "op": 2,
            'd': {
                "token": self.__token,
                "presence": {
                    "activities": [{
                        "name": "to Version 2.0",
                        "type": 2,
                    }],
                    "status": "online",
                    "since": None,
                    "afk": False
                },
                "properties": {
                    "os": "linux",
                    "browser": "Cleisthenes of Athens",
                    "device": "Cleisthenes of Athens"
                },
                "intents": 34306
            }
        })
        self.__state = 3

        # discord responds with OP code 0 "Ready"
        self.__wait_for_opcode(0)
        self.__session_id = self.__last_message['d']["session_id"]
        self.__resume_url = self.__last_message['d']["resume_gateway_url"]
        self.__state = 4


class HeartbeatThread:

    def __init__(self, interval: int, gateway: DiscordGateway):
        self.__state = 1
        self.__interval = (interval / 1000) - 1
        self.__gateway = gateway
        self.__mutex = gateway.mutex
        self.__event = gateway.event

        sleep(random() * self.__interval)

    def heartbeat(self):

        while self.__event.is_set():
            if self.__state != 1:
                # since this thread was called with the teardown function,
                # we can just fuck off and let the system reconnect
                self.__event.clear()
                return

            self.__gateway.send_message({
                "op": 1,
                "d": self.__gateway.s
            })
            self.__state = 2

            sleep(self.__interval)

    def ack_heartbeat(self):
        self.__state = 1
