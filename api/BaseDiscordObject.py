class BaseDiscordObject:

    def __init__(self):
        self.__can_set_attributes = True

    def __setattr__(self, key, value):
        try:
            if self.__can_set_attributes:
                super().__setattr__(key, value)
        except AttributeError:
            super().__setattr__(key, value)

    @classmethod
    def from_json(cls, obj: dict):
        bc = cls()

        for i in obj:
            cls.__setattr__(bc, i, obj[i])

        print("calling post process")
        bc._post_process()
        print("done calling post process")

        bc.__can_set_attributes = False

        return bc

    def _post_process(self):
        return
