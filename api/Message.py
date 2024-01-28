from api.Snowflake import Snowflake


class Message:

    def __init__(self):
        self.__id = None
        self.__channel_id = None
        self.__author = None
        self.__content = None
        self.__timestamp = None
        self.__edited_timestamp = None
        self.__tts = False
        self.__mention_everyone = False
        self.__mentions = []
        self.__mention_roles = []
        self.__mention_channels = []
        self.__attachments = []
        self.__embeds = []
        self.__reactions = []
        self.__nonce = None
        self.__pinned = None
        self.__webhook_id = None
        self.__type = None
        self.__activity = None
        self.__application = None
        self.__application_id = None
        self.__message_reference = None
        self.__flags = None
        self.__referenced_message = None
        self.__interaction = None
        self.__thread = None
        self.__components = []
        self.__sticker_items = []
        self.__stickers = []
        self.__position = None
        self.__role_subscription_data = None
        self.__resolved = None

    def __from_json(self, message_dict: dict):
        if not isinstance(message_dict, dict):
            raise TypeError(
                f"Expected <dict>, got {type(message_dict)}"
            )

        self.__id = Snowflake(message_dict["id"])
        # todo: MORE

