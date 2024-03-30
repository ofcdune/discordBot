from api.BaseDiscordObject import BaseDiscordObject


class Reaction(BaseDiscordObject):

    def __init__(self):
        super().__init__()

        self.count = None
        self.count_details = None
        self.me = False
        self.me_burst = False
        self.emoji = None
        self.burst_colors = []


class ReactionCountDetails(BaseDiscordObject):

    def __init__(self):
        super().__init__()

        self.__burst = None
        self.__normal = None

