import event


class MessageEvent(event.HandlerBase):

    def __init__(self):
        super().__init__()
        self.__message_create_cb = []
        self.__message_update_cb = []
        self.__message_delete_cb = []

    def handle_message_create(self, ctx):
        for callback in self.__message_create_cb:
            callback(ctx)

    def handle_message_update(self, ctx):
        for callback in self.__message_update_cb:
            callback(ctx)

    def handle_message_delete(self, ctx):
        for callback in self.__message_delete_cb:
            callback(ctx)

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
