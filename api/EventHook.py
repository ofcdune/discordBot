def create_wrapper(event_name):
    """
    Creates a python decorator for an event
    :param event_name: The event name
    :return:
    """

    def inside(gateway):
        """
        This is a custom decorator taking the event name from its constructor function.
        It could also be a standalone function, but is not, for redundancy reasons
        :param gateway: The gateway
        :return:
        """
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

            gateway.register(event_name, funcnotd)

        return decorator

    return inside


on_message = create_wrapper("MESSAGE_CREATE")
on_message_update = create_wrapper("MESSAGE_UPDATE")
on_message_delete = create_wrapper("MESSAGE_DELETE")

on_reaction = create_wrapper("MESSAGE_REACTION_ADD")
on_reaction_remove = create_wrapper("MESSAGE_REACTION_REMOVE")
