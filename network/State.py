from network.Websocket import DiscordWebsocket
from threading import Thread, Condition as Mutex, Event

from random import random
from time import sleep


class Watchman:

    def __init__(self, websocket_controller: DiscordWebsocket,
                 global_mutex: Mutex, global_event: Event):

        self.__opcode = None
        self.__t = None
        self.__callback = None
        self.__args = None
        self.__kwargs = None

        self.__state = 0

        self.__mutex = global_mutex
        self.__event = global_event
        self.__websocket = websocket_controller
        self.__last_message = {}

    def set_opcode(self, opcode: int):
        self.__opcode = opcode
        self.__state = 1
        return self

    def set_t(self, t: str):
        self.__t = t
        self.__state = 1
        return self

    def set_callback(self, callback, *args, **kwargs):
        self.__callback = callback
        self.__args = args
        self.__kwargs = kwargs
        return self

    def watch(self):

        if self.__state != 1 or self.__callback is None:
            self.__event.clear()
            raise SystemError(
                "Please provide either OP code or T value and a callback"
            )

        while self.__event.is_set():
            self.__mutex.acquire()
            if (not (self.__websocket.last_message["op"] == self.__opcode or
                     self.__websocket.last_message['t'] == self.__t) or
                    self.__websocket.last_message == self.__last_message):
                self.__mutex.release()
                continue

            self.__last_message = self.__websocket.last_message
            message = self.__callback(self.__websocket.last_message['d'], *self.__args, **self.__kwargs)
            if message is not None:
                self.__websocket.send_message(message)
            self.__mutex.release()


class State:

    def __init__(self, token: str, websocket_controller: DiscordWebsocket, global_mutex: Mutex, global_event: Event,
                 watchmen: list[Watchman]):
        self.__token = token
        self.__controller = websocket_controller
        self.__mutex = global_mutex
        self.__event = global_event
        self.__watchmen = watchmen
        self.__state = 0

        self.__threads = {"watchmen": []}

        self.__session_id = None
        self.__resume_url = None

        self.__event.set()

    @property
    def state(self):
        return self.__state

    @property
    def controller(self):
        return self.__controller

    def thread_with_teardown(self, target, *args, **kwargs):
        def startwithtd(*arg, **kwarg):
            target(*arg, **kwarg)
            self.teardown()

        thread = Thread(target=startwithtd, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def wait_for_opcode(self, opcode, blocking=True):
        if blocking:
            self.__mutex.acquire()
        while self.__controller.last_message["op"] != opcode:
            pass
        if blocking:
            self.__mutex.release()

    def get_last_message(self):
        self.__mutex.acquire()
        msg = self.__controller.last_message
        self.__mutex.release()
        return msg

    def enter(self):
        self.__threads["receive"] = self.thread_with_teardown(self.__controller.receive_from_discord)
        self.__state = 1

        self.wait_for_opcode(10)
        self.__state = 2

        last_message = self.get_last_message()
        interval = last_message['d']["heartbeat_interval"]

        hbt = HeartbeatThread(
            interval,
            self.__controller,
            self.__mutex,
            self.__event
        )

        self.__threads["heartbeat"] = self.thread_with_teardown(hbt.heartbeat)
        self.__threads["heartbeat_ack"] = self.thread_with_teardown(hbt.ack_heartbeat)

        self.__controller.send_message({
            "op": 2,
            'd': {
                "token": self.__token,
                "presence": {
                    "activities": [{
                        "name": "Version 2.0",
                        "type": 1,
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

        self.wait_for_opcode(0)
        last_message = self.get_last_message()

        self.__session_id = last_message['d']["session_id"]
        self.__resume_url = last_message['d']["resume_gateway_url"]
        self.__state = 4

        for wm in self.__watchmen:
            self.__threads["watchmen"].append(self.thread_with_teardown(wm.watch))

        self.__threads["resume_checked"] = self.thread_with_teardown(self.resume)
        self.wait_for_opcode(7, False)

    def teardown(self):
        self.__event.clear()
        self.__state = 0
        self.__threads = {"watchmen": []}
        self.__event.set()
        self.enter()

    def resume(self):
        while self.__event.is_set():
            while not self.__controller.resume_needed:
                pass
            message = {
                "op": 6,
                'd': {
                    "token": self.__token,
                    "session_id": self.__session_id,
                    "seq": self.__controller.s
                }
            }
            self.__controller.resume(self.__resume_url, message)


class HeartbeatThread:

    def __init__(self, interval: int, websocket_controller: DiscordWebsocket, mutex: Mutex, event: Event):
        self.__state = 1
        self.__interval = (interval / 1000) - 1
        self.__controller = websocket_controller
        self.__mutex = mutex
        self.__event = event

        sleep(random() * (interval / 1000))

    def heartbeat(self):

        while self.__event.is_set():
            if self.__state != 1:
                # since this thread was called with the teardown function,
                # we can just fuck off and let the system reconnect
                self.__event.clear()
                return

            self.__controller.send_message({
                "op": 1,
                "d": self.__controller.s
            })
            self.__state = 2

            sleep(self.__interval)

    def ack_heartbeat(self):
        while self.__event.is_set():
            if self.__controller.last_message["op"] == 11:
                self.__state = 1
