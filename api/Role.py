from api.BaseDiscordObject import BaseDiscordObject
from api.Snowflake import Snowflake


class Role(BaseDiscordObject):

    def __init__(self):
        super().__init__()

        self.id = None
        self.name = None
        self.color = None
        self.hoist = False
        self.icon = None
        self.unicode_emoji = None
        self.position = None
        self.permissions = None
        self.managed = False
        self.mentionable = False
        self.tags = None
        self.flags = None

    def _post_process(self):
        self.id = Snowflake(self.id)

        if self.tags is not None:
            self.tags = RoleTags.from_json(self.tags)


class RoleTags(BaseDiscordObject):

    def __init__(self):
        super().__init__()

        self.bot_id = None
        self.integration_id = None
        self.premium_subscriber = None
        self.subscription_listing_id = None
        self.available_for_purchase = None
        self.guild_connections = None

    def _post_process(self):
        self.bot_id = Snowflake(self.bot_id)
        self.integration_id = Snowflake(self.integration_id)
        self.subscription_listing_id = Snowflake(self.subscription_listing_id)
