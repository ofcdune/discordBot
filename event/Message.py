import event
from api.Message import Message


def message_preprocessor(ctx):
    return Message.from_json(ctx.d | {"bot": ctx.bot})


class MessageEvent(event.HandlerBase):

    def __init__(self):
        super().__init__()
        self.__command_cb = {}
        self.__message_create_cb = []
        self.__message_update_cb = []
        self.__message_delete_cb = []

    def handle_message_create(self, ctx):

        message = message_preprocessor(ctx)
        content = message.content.split(' ')

        if len(content) == 0:
            for callback in self.__message_create_cb:
                callback(message)
            return

        if len(content[0]) < 2:
            for callback in self.__message_create_cb:
                callback(message)
            return

        prefix = content[0][0]
        function_name = content[0][1:]

        callback = self.__command_cb.get(function_name)
        if callback is None:
            # there is no command registered with the specified function name
            for callback in self.__message_create_cb:
                callback(message)
            return

        if callback["prefix"] != prefix:
            for callback in self.__message_create_cb:
                callback(message)
            return

        # todo: check the owner
        # todo: check roles
        # todo: now that we added a layer of abstraction, we could also add custom arguments

        try:
            return callback["function"](message)
        except Exception as e:
            print(">>> ", e)
            return False

    def handle_message_update(self, ctx):
        message = message_preprocessor(ctx)
        for callback in self.__message_update_cb:
            callback(message)

    def handle_message_delete(self, ctx):
        message = message_preprocessor(ctx)
        for callback in self.__message_delete_cb:
            callback(message)

    def command(self, prefix: str, owner: bool = False):
        def decorator(func):
            """
            Inside the actual decorator body, the function gets registered,
            :param func:
            :return:
            """

            def funcnotd(*args, **kwargs):
                """
                To avoid accidentally crashing the bot by returning 'False', our desired function gets wrapped once
                :param args:
                :param kwargs:
                :return:
                """
                func(*args, **kwargs)
                return True

            self.__command_cb[func.__name__] = {
                "function": funcnotd,
                "prefix": prefix,
                "owner": owner
            }

        return decorator

    def message_create(self):
        def decorator(func):
            """
            Inside the actual decorator body, the function gets registered,
            :param func:
            :return:
            """

            def funcnotd(*args, **kwargs):
                """
                To avoid accidentally crashing the bot by returning 'False', our desired function gets wrapped once
                :param args:
                :param kwargs:
                :return:
                """
                func(*args, **kwargs)
                return True

            self.__message_create_cb.append(funcnotd)

        return decorator

    def message_update(self):
        def decorator(func):
            """
            Inside the actual decorator body, the function gets registered,
            :param func:
            :return:
            """

            def funcnotd(*args, **kwargs):
                """
                To avoid accidentally crashing the bot by returning 'False', our desired function gets wrapped once
                :param args:
                :param kwargs:
                :return:
                """
                func(*args, **kwargs)
                return True

            self.__message_update_cb.append(funcnotd)

        return decorator

    def message_delete(self):
        def decorator(func):
            """
            Inside the actual decorator body, the function gets registered,
            :param func:
            :return:
            """

            def funcnotd(*args, **kwargs):
                """
                To avoid accidentally crashing the bot by returning 'False', our desired function gets wrapped once
                :param args:
                :param kwargs:
                :return:
                """
                func(*args, **kwargs)
                return True

            self.__message_delete_cb.append(funcnotd)

        return decorator


messages = MessageEvent()
