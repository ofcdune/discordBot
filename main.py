from json import loads
from api.Bot import Bot
from gateway.Gateway import DiscordGateway
from api.EventHook import *


config = loads(open("config.json", "r").read())
bot = Bot(config["token"])

gw = DiscordGateway()
gw.set_token(config["token"])


@on_message(gw)
def message(ctx):
    content = ctx["content"]
    if not content.startswith('!'):
        return

    command = content[1:]

    if command == "uptime":
        bot.send_dm(ctx["author"]["id"], "It works")


gw.start()
