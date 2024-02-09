import event


class ReactionEvent(event.HandlerBase):

    def __init__(self):
        super().__init__()
        self.__reaction_add_cb = []
        self.__reaction_remove_cb = []

    def handle_reaction_add(self, ctx):
        for callback in self.__reaction_add_cb:
            callback(ctx)

    def handle_reaction_remove(self, ctx):
        for callback in self.__reaction_remove_cb:
            callback(ctx)

    def reaction_add(self):
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

            self.__reaction_add_cb.append(funcnotd)

        return decorator

    def reaction_remove(self):
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

            self.__reaction_remove_cb.append(funcnotd)

        return decorator


reactions = ReactionEvent()
