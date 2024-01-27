from json import loads
from api.Bot import Bot
from gateway.Gateway import DiscordGateway
from threading import Condition, Event
from api.EventHook import *


config = loads(open("config.json", "r").read())
bot = Bot(config["token"])

mutex = Condition()
event = Event()

gw = DiscordGateway(config["token"], "wss://gateway.discord.gg/?v=10&encoding=json", mutex, event)


@on_message(gw)
def message(ctx):
    content = ctx["content"]
    if not content.startswith('!'):
        return
    command = content[1:]

    if command == "uptime":
        bot.send_dm(ctx["member"], "It works")


@on_reaction(gw)
def reaction(ctx):

    bot.send_dm(ctx["user_id"], "You reacted to a message :smirk:")


gw.start()
