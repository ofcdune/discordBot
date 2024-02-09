from abc import ABC


class HandlerBase(ABC):

    def __init__(self):
        super().__init__()

    def handle(self, ctx):
        pass
