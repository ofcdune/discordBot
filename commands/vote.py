from gateway.Bot import messages, reactions
from api.Message import Message


@messages.command('!')
def vote(ctx: Message):
    ctx.bot.send_message(ctx.channel_id, "No!")
    return


@reactions.reaction_add()
def on_vote(ctx):
    return
