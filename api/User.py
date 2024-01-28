from api.Snowflake import Snowflake


class User:

    def __init__(self):
        self.__id = None
        self.__username = None
        self.__discriminator = None
        self.__global_name = None
        self.__avatar = None
        self.__bot = False
        self.__system = False
        self.__mfa_enabled = False
        self.__banner = None
        self.__accent_color = None
        self.__locale = None
        self.__verified = False
        self.__email = None
        self.__flags = None
        self.__premium_type = None
        self.__public_flags = None
        self.__avatar_decoration = None

    def __from_json(self, user_dict: dict):
        if not isinstance(user_dict, dict):
            raise TypeError(
                f"Expected <dict>, got {type(user_dict)}"
            )

        self.__id = Snowflake(user_dict["id"])
        # todo: MORE
