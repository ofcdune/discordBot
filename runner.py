from api.Snowflake import Snowflake


class User:

    test = 1

    def __init__(self, **kwargs):

        self.test = 2

        self.id = Snowflake(kwargs["id"])
        self.username = kwargs["username"]
        self.discriminator = kwargs["discriminator"]
        self.global_name = kwargs["global_name"]
        self.avatar = kwargs["avatar"]
        self.bot = kwargs.get("bot")
        self.system = kwargs.get("system")
        self.mfa_enabled = kwargs.get("mfa_enabled")
        self.banner = kwargs.get("banner")
        self.accent_color = kwargs.get("accent_color")
        self.locale = kwargs.get("locale")
        self.verified = kwargs.get("verified")
        self.email = kwargs.get("email")
        self.flags = kwargs.get("flags")
        self.premium_type = kwargs.get("premium_type")
        self.public_flags = kwargs.get("public_flags")
        self.avatar_decoration = kwargs.get("avatar_decoration")


if __name__ == '__main__':
    x = User(id="1", username="digga", discriminator=0, global_name="d", avatar=None)
