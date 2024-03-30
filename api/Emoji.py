from api.BaseDiscordObject import BaseDiscordObject
from api.Snowflake import Snowflake
from api.User import User
from api.Role import Role


class Emoji(BaseDiscordObject):

    def __init__(self):
        super().__init__()

        self.id = None
        self.name = None
        self.roles = []
        self.user = None
        self.require_colons = False
        self.managed = False
        self.animated = False
        self.available = False

    def _post_process(self):
        self.id = Snowflake(self.id)

        for i, role in enumerate(self.roles):
            self.roles[i] = Role.from_json(role)

        self.user = User.from_json(self.user)
