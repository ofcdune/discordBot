from random import random
from time import sleep
from datetime import datetime

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

        self.__heartbeat_interval = 0

        self.__session_id = None
        self.__resume_url = None

        self.__event.set()

    @property
    def last_message(self):
        return self.__last_message

    def register(self, arg, callback):
        self.__watchmen[arg] = callback

    def thread_with_teardown(self, target, *args, **kwargs):
        def startwithtd(*arg, **kwarg):
            result = target(*arg, **kwarg)
            if not result:
                # this neat feature allows me to specify certain teardown conditions
                # instead of just tearing down the entire process at once
                print(f"{datetime.now()} Tearing down processes due to function", target.__name__, flush=True)
                self.teardown()

        thread = Thread(target=startwithtd, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def teardown(self):
        self.__event.clear()
        self.__state = 0
        self.__s = None
        self.__event.set()
        self.start()

    def __wait_for_opcode(self, opcode):
        while self.__last_message["op"] != opcode:
            sleep(.1)

    def send_message(self, message: dict):
        if not isinstance(message, dict):
            return

        print(f"{datetime.now()} TX <<< {message}", flush=True)

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

                print(f"{datetime.now()} RX >>> {self.__last_message}", flush=True)

            except ConnectionClosedError:
                self.__mutex.release()
                self.__event.clear()
                return True

            except ConnectionClosedOK as e:
                self.__mutex.release()
                print(datetime.now(), e, flush=True)
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

    def __secsleep(self, seconds):
        counter = 0
        while self.__event.is_set() and counter < seconds:
            sleep(1)
            counter += 1

        return counter == seconds

    def set_heartbeat_interval(self, ctx):
        # OP code 10
        if not (self.__state == 1 or self.__state == 5):
            print(f"{datetime.now()} State failure, cannot grab heartbeat, tearing down", flush=True)
            return False

        self.__heartbeat_interval = ctx["heartbeat_interval"] // 1000
        if not self.__secsleep(int(random() * self.__heartbeat_interval)):
            return False
        if not self.__secsleep(self.__heartbeat_interval):
            return False

        self.send_message({
                "op": 1,
                "d": self.__s
            })

        return True

    def heartbeat_response(self, ctx):
        # OP code 11
        if not self.__secsleep(self.__heartbeat_interval):
            return False

        self.send_message({
            "op": 1,
            "d": self.__s
        })

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
        # discord sends OP code 10 to indicate setting a new heartbeat interval
        self.register(10, self.set_heartbeat_interval)

        # discord responds with OP code 11 to indicate a heartbeat acknowledgement, this starts a new countdown
        self.register(11, self.heartbeat_response)

        # discord responds with OP code 0 "Ready" to indicate that events can be received
        self.register("READY", self.grab_session)

        self.register(9, self.opcode9)

        print(f"{datetime.now()} Starting gateway handshake", flush=True)

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
