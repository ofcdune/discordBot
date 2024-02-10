from json import loads
from api.Bot import Bot, commands, messages, reactions

config = loads(open("config.json", "r").read())
bot = Bot()

bot.set_token(config["token"])


@commands.command('!')
def uptime(ctx):
    bot.send_dm(ctx["author"]["id"], f"Online since {bot.uptime}")


bot.run_forever()
