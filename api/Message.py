from api.BaseDiscordObject import BaseDiscordObject
from api.Snowflake import Snowflake
from api.User import User

from datetime import datetime


class Message(BaseDiscordObject):

    def __init__(self):
        super().__init__()

        self.id = None
        self.channel_id = None
        self.author = None
        self.content = None
        self.timestamp = None
        self.edited_timestamp = None
        self.tts = False
        self.mention_everyone = False
        self.mentions = []
        self.mention_roles = []
        self.mention_channels = []
        self.attachments = []
        self.embeds = []
        self.reactions = []
        self.nonce = None
        self.pinned = None
        self.webhook_id = None
        self.type = None
        self.activity = None
        self.application = None
        self.application_id = None
        self.message_reference = None
        self.flags = None
        self.referenced_message = None
        self.interaction = None
        self.thread = None
        self.components = []
        self.sticker_items = []
        self.stickers = []
        self.position = None
        self.role_subscription_data = None
        self.resolved = None

    def _post_process(self):
        self.id = Snowflake(self.id)
        self.channel_id = Snowflake(self.id)

        self.author = User.from_json(self.author)

        self.timestamp = datetime.timestamp(self.timestamp)
        self.edited_timestamp = datetime.timestamp(self.edited_timestamp)

