from api.BaseDiscordObject import BaseDiscordObject
from api.Snowflake import Snowflake


class User(BaseDiscordObject):

    def __init__(self):
        super().__init__()
        
        self.id = None
        self.username = None
        self.discriminator = None
        self.global_name = None
        self.avatar = None
        self.bot = None
        self.system = None
        self.mfa_enabled = None
        self.banner = None
        self.accent_color = None
        self.locale = None
        self.verified = None
        self.email = None
        self.flags = None
        self.premium_type = None
        self.public_flags = None
        self.avatar_decoration = None

    def _post_process(self):
        self.id = Snowflake(self.id)
