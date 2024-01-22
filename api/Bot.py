from requests import post, put, get, patch, delete
from datetime import datetime

DISCORD_PRESENCE_MSG = 15
DISCORD_PRESENCE_GUILDMSG = 9
DISCORD_PRESENCE_GUILD = 1
DISCORD_GUILD_MESSAGE_REACTIONS = 10


class Bot:

    def __init__(self, token: str, presence: object = None):
        self.__token = token
        self.__presence = presence
        self.__base_url = "https://discord.com/api/v10"
        self.owner = "718832291274817567"
        self.own_id = "1167130660205510716"
        self.__uptime = datetime.utcnow()

        self.__post_header = {
            "authority": "discord.com",
            "accept": '/',
            "content-type": "application/json",
            "Authorization": f"Bot {token}"
            # "Authorization": "NzE4ODMyMjkxMjc0ODE3NTY3.GuLb2H.Yar7BbL3M4mE0EPVUs8_yPDzAy4hRU2tqTuYLw"
        }

        self.__dm_channels = {}
        self.__websocket_connection = None

    @staticmethod
    def get_intents(*shifts: int):
        nbr = 0
        for shift in shifts:
            nbr |= (1 << shift)
        return nbr

    @property
    def token(self):
        return self.__token

    @property
    def presence(self):
        return self.__presence

    @property
    def uptime(self):
        return self.__uptime

    def set_connection(self, new_connection):
        self.__websocket_connection = new_connection

    def set_presence(self, presence):
        self.__presence = presence

    def update_presence(self, new_presence: dict, activity_type=0):
        self.set_presence(new_presence)
        self.__websocket_connection.send({
            "op": 3,
            "d": {
                "token": self.token,
                "activities": [{
                    "name": f"{new_presence}",
                    "type": int(activity_type),
                }],
                "status": "online",
                "since": None,
                "afk": False
            }
        })

    def identify(self):

        obj = {
            "op": 2,
            'd': {
                "token": self.__token,
                "properties": {
                    "os": "linux",
                    "browser": "Cleisthenes of Athens",
                    "device": "Cleisthenes of Athens"
                },
                "intents": self.get_intents(DISCORD_PRESENCE_MSG, DISCORD_PRESENCE_GUILDMSG,
                                            DISCORD_PRESENCE_GUILD, DISCORD_GUILD_MESSAGE_REACTIONS)
            }
        }

        if self.__presence:
            obj['d']["presence"] = self.__presence

        return obj

    def get_url(self, url: str):
        return self.__base_url + url

    def post(self, url: str, body: dict):
        url = self.get_url(url)
        return post(url, headers=self.__post_header, json=body)

    def get(self, url: str):
        url = self.get_url(url)
        return get(url, headers=self.__post_header)

    def put(self, url: str):
        url = self.get_url(url)
        return put(url, headers=self.__post_header)

    def patch(self, url: str, body: dict):
        url = self.get_url(url)
        return patch(url, headers=self.__post_header, json=body)

    def delete(self, url: str):
        url = self.get_url(url)
        return delete(url, headers=self.__post_header)

    def send_websocket(self, obj: dict):
        self.__websocket_connection.send(obj)

    def get_message(self, channel_id: str, message_id: str):
        content = self.get(f"/channels/{channel_id}/messages/{message_id}")
        if content.status_code == 200:
            return content.json()
        else:
            return {}

    def send_message(self, channel_id: str, content: str):
        return self.post(f"/channels/{channel_id}/messages", {"content": content})

    def edit_message(self, channel_id: str, message_id: str, new_message_obj: dict):
        if not isinstance(new_message_obj, dict):
            return 404
        return self.patch(f"/channels/{channel_id}/messages/{message_id}", new_message_obj)

    def edit_message_content(self, channel_id: str, message_id: str, content: str):
        msg = self.get_message(channel_id, message_id)
        msg["content"] = content
        return self.edit_message(channel_id, message_id, msg)

    def delete_message(self, channel_id: str, message_id: str):
        return self.delete(f"/channels/{channel_id}/messages/{message_id}")

    def create_dm(self, user_id: str):
        channel_id_request = self.post("/users/@me/channels", {"recipient_id": user_id})
        self.__dm_channels[user_id] = channel_id_request

    def send_dm(self, user_id: str, content: str):
        if self.__dm_channels.get(user_id) is None:
            self.create_dm(user_id)

        if self.__dm_channels[user_id].status_code == 200 or self.__dm_channels[user_id].status_code == 201:
            channel_id = self.__dm_channels[user_id].json()["id"]
            return self.send_message(channel_id, content)
