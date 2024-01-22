from json import loads
from api.Bot import Bot
from network.State import State, Watchman
from network.Websocket import DiscordWebsocket

from threading import Condition, Event


def on_message(ctx):
    print("New message", ctx)


config = loads(open("config.json", "r").read())
bot = Bot(config["token"])

mutex = Condition()
event = Event()

ws = DiscordWebsocket(event)

wm = Watchman(ws, mutex, event).set_opcode(0).set_t("MESSAGE_CREATE").set_callback(on_message)

s = State(config["token"], ws, mutex, event, [wm])

s.enter()
