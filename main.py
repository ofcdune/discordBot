from json import loads
from api.Bot import Bot
from network.State import State, Watchman
from network.Websocket import DiscordWebsocket

from threading import Condition, Event


config = loads(open("config.json", "r").read())
bot = Bot(config["token"])

mutex = Condition()
event = Event()

ws = DiscordWebsocket(event)

s = State(config["token"], ws, mutex, event, [])

s.enter()
