class Snowflake:

    def __init__(self, value):
        self.__value = int(value)

    def unix_timestamp(self):
        return (self.__value >> 22) + 1420070400000

    def internal_worker_id(self):
        return (self.__value & 0x3E0000) >> 17

    def internal_process_id(self):
        return (self.__value & 0x1F000) >> 12

    def increment(self):
        return self.__value & 0xFFF
