from requests import post, put, get, patch, delete
from datetime import datetime
from gateway.Gateway import DiscordGateway

from event.Message import messages
from event.Reaction import reactions


class Bot:

    def __init__(self, presence: object = None):
        self.__token = None
        self.__presence = presence
        self.__base_url = "https://discord.com/api/v10"
        self.owner = "718832291274817567"
        self.own_id = "1167130660205510716"
        self.__uptime = datetime.utcnow()

        self.__post_header = {
            "authority": "discord.com",
            "accept": '/',
            "content-type": "application/json",
            # "Authorization": "NzE4ODMyMjkxMjc0ODE3NTY3.GuLb2H.Yar7BbL3M4mE0EPVUs8_yPDzAy4hRU2tqTuYLw"
        }

        self.__gateway = DiscordGateway()

        self.__dm_channels = {}

        self.__gateway.register("MESSAGE_CREATE", messages.handle_message_create)
        self.__gateway.register("MESSAGE_UPDATE", messages.handle_message_update)
        self.__gateway.register("MESSAGE_DELETE", messages.handle_message_delete)

        self.__gateway.register("MESSAGE_REACTION_ADD", reactions.handle_reaction_add)
        self.__gateway.register("MESSAGE_REACTION_REMOVE", reactions.handle_reaction_remove)

        self.__cached_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.__retries = 1000

    @property
    def presence(self):
        return self.__presence

    @property
    def uptime(self):
        return self.__uptime

    def run_forever(self):

        resp = self.get("/gateway/bot")
        if resp.status_code != 200:
            print("Fatal network error")
            return

        resp = resp.json()
        self.__cached_url = resp["url"]
        self.__retries = resp["session_start_limit"]["remaining"]

        while self.__retries:
            self.__gateway.run(self.__cached_url)

            resp = self.get("/gateway/bot")
            if resp.status_code != 200:
                print("Fatal network error")
                return

            resp = resp.json()
            self.__cached_url = resp["url"]
            self.__retries = resp["session_start_limit"]["remaining"]

        print("Exceeded max retries for the day, quitting")

    def set_token(self, token):
        self.__post_header["Authorization"] = f"Bot {token}"
        self.__gateway.set_token(token)

    def set_presence(self, new_presence: dict):
        self.__presence = new_presence
        self.__gateway.send_message({"op": 3, 'd': new_presence})

    def __get_url(self, url: str):
        return self.__base_url + url

    def post(self, url: str, body: dict):
        url = self.__get_url(url)
        return post(url, headers=self.__post_header, json=body)

    def get(self, url: str):
        url = self.__get_url(url)
        return get(url, headers=self.__post_header)

    def put(self, url: str):
        url = self.__get_url(url)
        return put(url, headers=self.__post_header)

    def patch(self, url: str, body: dict):
        url = self.__get_url(url)
        return patch(url, headers=self.__post_header, json=body)

    def delete(self, url: str):
        url = self.__get_url(url)
        return delete(url, headers=self.__post_header)

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
