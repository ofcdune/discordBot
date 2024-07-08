class Context:

    def __init__(self, bot, d):
        self.__bot = bot
        self.__d = d

    def __str__(self):
        return str(self.__d)

    def __getitem__(self, item):
        return self.__d[item]

    @property
    def bot(self):
        return self.__bot

    @property
    def d(self):
        return self.__d
