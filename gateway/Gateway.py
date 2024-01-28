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

        self.__heartbeat_class = None
        self.__heartbeat_thread = None
        self.__local_event = Event()
        self.__local_event.set()

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

    @property
    def local_event(self):
        return self.__local_event

    def register(self, arg, callback):
        self.__watchmen[arg] = callback

    def thread_with_teardown(self, target, *args, **kwargs):
        def startwithtd(*arg, **kwarg):
            result = target(*arg, **kwarg)
            if not result:
                # this neat feature allows me to specify certain teardown conditions
                # instead of just tearing down the entire process at once
                print("Tearing down processes due to function", target.__name__)
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
        while self.__last_message["op"] != opcode:
            sleep(.1)

    def send_message(self, message: dict):
        if not isinstance(message, dict):
            return

        print(f"TX <<< {message}")

        self.__websocket.send(dumps(message))

    def __receive_from_discord(self):
        self.__websocket = connect(self.__url, ssl_context=ssl_context)
        while self.__event.is_set():
            try:
                self.__mutex.acquire()
                self.__last_message = loads(self.__websocket.recv())
                if self.__last_message['s'] is not None:
                    self.__s = self.__last_message['s']
                self.__mutex.release()

                print(f"RX >>> {self.__last_message}")

            except ConnectionClosedError:
                self.__mutex.release()
                self.__event.clear()
                return True

            except ConnectionClosedOK as e:
                self.__mutex.release()
                print(e)
                match e.code:
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4005 | 4007 | 4008:
                        self.resume(None)
                    case _:
                        self.__event.clear()
                        return

            callback = self.__watchmen.get(self.__last_message["op"])
            if callback is not None:
                self.thread_with_teardown(callback, self.__last_message['d'])

            callback = self.__watchmen.get(self.__last_message["t"])
            if callback is not None:
                self.thread_with_teardown(callback, self.__last_message['d'])

    def resume(self, ctx):
        self.__state = 5
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
        return True

    def grab_heartbeat(self, ctx):
        if not (self.__state == 1 or self.__state == 5):
            print("State failure, cannot grab heartbeat, tearing down")
            return False

        interval = ctx["heartbeat_interval"]

        # kill any other active thread (when a clean reconnect occurs)
        if self.__heartbeat_class is None:
            self.__heartbeat_class = HeartbeatThread(interval, self)

        if self.__state == 1:
            self.__state = 2
            if self.__heartbeat_thread is not None:
                self.__local_event.clear()
                self.__heartbeat_thread.join()
                self.__local_event.set()
                self.__heartbeat_class.ack_heartbeat(None)

                # we start sending heartbeats to the websocket
                self.__heartbeat_thread = self.thread_with_teardown(self.__heartbeat_class.heartbeat)
                self.register(11, self.__heartbeat_class.ack_heartbeat)
        else:
            self.__state = 4

        return True

    def grab_session(self, ctx):
        self.__state = 4
        self.__session_id = ctx["session_id"]
        self.__resume_url = ctx["resume_gateway_url"]
        return True

    def opcode9(self, ctx):
        if ctx:
            self.resume(ctx)
            return True
        return False

    def start(self):
        # discord responds with OP code 10
        self.register(10, self.grab_heartbeat)

        # discord responds with OP code 0 "Ready"
        self.register("READY", self.grab_session)

        self.register(9, self.opcode9)

        print("Starting gateway handshake")

        # establish a connection with the discord websocket
        self.__state = 1
        self.thread_with_teardown(self.__receive_from_discord)

        while self.__state != 2:
            sleep(.1)

        # we send the register message with the bot token and our initial presence
        self.send_message({
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


class HeartbeatThread:

    def __init__(self, interval: int, gateway: DiscordGateway):
        self.__state = 1
        self.__interval = (interval / 1000) - 1
        self.__gateway = gateway

        sleep(random() * self.__interval)

    def heartbeat(self, *args, **kwargs):

        while self.__gateway.event.is_set() and self.__gateway.local_event.is_set():
            if self.__state != 1:
                # since this thread was called with the teardown function,
                # we can just fuck off and let the system reconnect
                self.__gateway.event.clear()
                return False

            self.__gateway.send_message({
                "op": 1,
                "d": self.__gateway.s
            })
            self.__state = 2

            sleep(self.__interval)

        return True

    def ack_heartbeat(self, ctx):
        self.__state = 1
        return True
