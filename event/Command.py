import event


class CommandEvent(event.HandlerBase):

    def __init__(self):
        super().__init__()
        self.__handler = {}

    def handle(self, ctx):
        content = ctx["content"].split(' ')

        if len(content) == 0:
            return

        if len(content[0]) < 2:
            return

        prefix = content[0][0]
        function_name = content[0][1:]

        callback = self.__handler.get(function_name)
        if callback is None:
            return

        if callback["prefix"] != prefix:
            return

        # todo: check the owner
        # todo: check roles
        # todo: now that we added a layer of abstraction, we could also add custom arguments

        try:
            return callback["function"](ctx)
        except Exception as e:
            return False

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

            self.__handler[func.__name__] = {
                "function": funcnotd,
                "prefix": prefix,
                "owner": owner
            }

        return decorator


commands = CommandEvent()
