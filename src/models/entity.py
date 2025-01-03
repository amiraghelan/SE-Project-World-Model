from datetime import datetime
from src.utils.random_id_generator import UniqueIDGenerator


class Entity:
    def __init__(self, type: str, queue_capacity: int, max_capacity: int) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.type = type.lower()
        self.queue_capacity = queue_capacity
        self.max_capacity = max_capacity
        self.used_capacity = 0
        self.creation_date = datetime.now()
        self.last_modified_date = self.creation_date

    def get_id(self) -> int:
        return self.id

    def increase_used_capacity(self) -> None:
        self.used_capacity += 1
        self.last_modified_date = datetime.now()

    def update_queue_capacity(self, value) -> None:
        self.queue_capacity = value
        self.last_modified_date = datetime.now()

    def update_max_capacity(self, new_value) -> None:
        self.max_capacity = new_value
        self.last_modified_date = datetime.now()


class EntityAttributeValue:
    def __init__(self, entity_id: int, name: str, value):
        self.id = UniqueIDGenerator.generate_id()
        self.entity_id = entity_id
        self.name = name.lower()
        self.value = value

    def update_value(self, value) -> None:
        self.value = value
