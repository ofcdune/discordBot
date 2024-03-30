from time import sleep
from datetime import datetime

from websockets import ConnectionClosedError, ConnectionClosedOK
from websockets.sync.client import connect

from threading import Thread, Condition as Mutex, Event
from json import loads, dumps
from os.path import exists

from gateway import Bot

import ssl

# todo: please remove in production
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class DiscordGateway:

    def __init__(self):
        self.__token = None
        self.__url = ""
        self.__bot = None

        self.__websocket = None
        self.__mutex = Mutex()
        self.__event = Event()
        self.__watchmen = {}
        self.__bot = None

        self.__last_message = {"op": -1}
        self.__s = None

        self.__heartbeat_interval = 0
        self.__heartbeat_started = False
        self.__heartbeat_thread_active = False
        self.__logged_in = False

        self.__session_id = None
        self.__resume_url = None
        self.__unfixable = False

        self.__threads = []

    @property
    def unfixable(self):
        return self.__unfixable

    def register(self, arg, callback):
        self.__watchmen[arg] = callback

    def set_token(self, token: str):
        self.__token = token

    def set_bot(self, bot: Bot):
        self.__bot = bot

    def __thread_with_teardown(self, target, *args, **kwargs):
        def startwithtd(*arg, **kwarg):
            result = target(*arg, **kwarg)

            if result == False and self.__event.is_set():
                # this neat feature allows me to specify certain teardown conditions
                # instead of just tearing down the entire process at once
                print(f"{datetime.now()} Tearing down processes due to function", target.__name__, flush=True)
                self.__teardown()

        thread = Thread(target=startwithtd, args=args, kwargs=kwargs)
        thread.start()
        self.__threads.append(thread)

        return thread

    def __teardown(self):
        self.__event.clear()
        self.__websocket.close()

        self.__heartbeat_started = False
        self.__heartbeat_thread_active = False
        self.__logged_in = False

        self.__s = None

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
                if self.__last_message['s'] is not None:
                    self.__s = self.__last_message['s']
                self.__mutex.release()

                callbacks = self.__watchmen.get(self.__last_message["op"], None)
                if callbacks is not None:
                    self.__thread_with_teardown(callbacks, self.__last_message['d'])

                callbacks = self.__watchmen.get(self.__last_message["t"], None)
                if callbacks is not None:
                    self.__thread_with_teardown(callbacks, self.__last_message['d'])

            except ConnectionClosedError as e:
                self.__mutex.release()
                print(datetime.now(), e, flush=True)
                # self.__unfixable = True
                return False

            except ConnectionClosedOK as e:
                self.__mutex.release()
                print(datetime.now(), e, flush=True)
                match e.code:
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4005 | 4007 | 4008:
                        self.__resume(None)
                    case _:
                        return False

        return False

    def __resume(self, ctx):
        self.__mutex.acquire()
        self.__websocket = connect(self.__resume_url, ssl_context=ssl_context)
        self.send_message({
            "op": 6,
            'd': {
                "token": self.__token,
                "session_id": self.__session_id,
                "seq": self.__s
            }
        })
        self.__mutex.release()
        return True

    def __secsleep(self, seconds):
        counter = 0
        while self.__event.is_set() and counter < seconds:
            sleep(1)
            counter += 1

        return counter == seconds

    def __set_heartbeat_interval(self, ctx):
        # OP code 10

        self.__heartbeat_interval = ctx["heartbeat_interval"] // 1000

        if not self.__heartbeat_started:
            self.__heartbeat_started = True

        self.send_message({
            "op": 1,
            "d": self.__s
        })

        if not self.__logged_in:
            self.__logged_in = True

            # we send the register message with the bot token and our initial presence
            activities = []
            if exists(r"assets/status.txt"):
                content = open("assets/status.txt", 'r').read().split('\n')
                for line in content:
                    activities.append({
                        "name": line,
                        "type": 2
                    })
            else:
                activities.append({
                    "name": "Version 2.0",
                    "type": 2,
                })

            self.send_message({
                "op": 2,
                'd': {
                    "token": self.__token,
                    "presence": {
                        "activities": activities,
                        "status": "afk",
                        "since": None,
                        "afk": True
                    },
                    "properties": {
                        "os": "linux",
                        "browser": "Chrome",
                        "device": "Phone"
                    },
                    "intents": 34306
                }
            })

        return True

    def __heartbeat_response(self, ctx):

        if not self.__heartbeat_started:
            return False

        if self.__heartbeat_thread_active:
            return True

        self.__heartbeat_thread_active = True
        # OP code 11
        if not self.__secsleep(self.__heartbeat_interval):
            return True

        self.__heartbeat_thread_active = False
        self.send_message({
            "op": 1,
            "d": self.__s
        })

        return True

    def __grab_session(self, ctx):
        self.__session_id = ctx["session_id"]
        self.__resume_url = ctx["resume_gateway_url"]
        return True

    def __opcode9(self, ctx):
        if ctx:
            self.__resume(ctx)
            return ctx
        return ctx

    def run(self, url, bot):

        self.__url = url

        for t in self.__threads:
            t.join()

        self.__event.set()
        self.__threads.clear()

        if self.__token is None:
            return

        # discord sends OP code 7 to request an immediate resume
        self.register(7, self.__resume)

        # discord sends OP code 10 to indicate setting a new heartbeat interval
        self.register(10, self.__set_heartbeat_interval)

        # discord responds with OP code 11 to indicate a heartbeat acknowledgement, this starts a new countdown
        self.register(11, self.__heartbeat_response)

        # discord responds with OP code 0 "Ready" to indicate that events can be received
        self.register("READY", self.__grab_session)

        self.register(9, self.__opcode9)

        print(f"{datetime.now()} Starting gateway handshake", flush=True)

        # establish a connection with the discord websocket
        recv = self.__thread_with_teardown(self.__receive_from_discord)

        recv.join()
