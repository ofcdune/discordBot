from json import loads
from gateway.Bot import Bot, messages

from commands.vote import *
from commands.bot_system import *

config = loads(open("config.json", "r").read())
bot = Bot()

bot.set_token(config["token"])
bot.run_forever()
