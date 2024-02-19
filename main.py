from json import loads
from api.Bot import Bot, messages, reactions

from datetime import datetime

config = loads(open("config.json", "r").read())
bot = Bot()

bot.set_token(config["token"])


@messages.command('!')
def uptime(ctx):
    delta = datetime.now() - bot.uptime
    conv = datetime(1970, 1, 1, 0, 0) + delta

    bot.send_dm(ctx["author"]["id"], f"Online since {conv.month - 1} months, {conv.day - 1} days, "
                                     f"{conv.hour - 1} hours, {conv.minute} minutes and {conv.second} seconds")


bot.run_forever()
