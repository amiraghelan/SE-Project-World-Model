import random


class RandomIdGenerator:
    @staticmethod
    def generate(min_value: int = 1, max_value: int = 1000000) -> int:
        return random.randint(min_value, max_value)
