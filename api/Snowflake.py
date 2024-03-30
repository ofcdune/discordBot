class Snowflake:

    def __init__(self, value):
        if value is None:
            return
        self.__value = int(value)

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return f"Snowflake({self.__value})"

    def unix_timestamp(self):
        return (self.__value >> 22) + 1420070400000

    def internal_worker_id(self):
        return (self.__value & 0x3E0000) >> 17

    def internal_process_id(self):
        return (self.__value & 0x1F000) >> 12

    def increment(self):
        return self.__value & 0xFFF
