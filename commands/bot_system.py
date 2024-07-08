from datetime import datetime

from gateway.Bot import messages
from api.Message import Message


@messages.command('!')
def uptime(ctx: Message):
    delta = datetime.utcnow() - ctx.bot.uptime
    conv = datetime(1970, 1, 1, 0, 0) + delta

    ctx.bot.send_dm(
        ctx.author.id, f"Online since {conv.month - 1} months, {conv.day - 1} days, "
                       f"{conv.hour - 1} hours, {conv.minute} minutes and {conv.second} seconds"
    )
