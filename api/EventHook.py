from functools import wraps


def on_message(gateway):
    def decorator_on_event(func):
        @wraps(func)
        def registered_wrapper():
            gateway.register("MESSAGE_CREATE", func)
        return registered_wrapper
    return decorator_on_event


def on_reaction(gateway):
    def decorator_on_event(func):
        @wraps(func)
        def registered_wrapper():
            gateway.register("MESSAGE_REACTION_ADD", func)
        return registered_wrapper
    return decorator_on_event
