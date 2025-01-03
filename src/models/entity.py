from datetime import datetime
from src.utils.random_id_generator import UniqueIDGenerator


class Entity:
    def __init__(self, entity_type: str, max_capacity: int) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.entity_type = entity_type.lower()
        self.max_capacity = max_capacity
        self.used_capacity = 0
        self.creation_date = datetime.now()
        self.last_modified_date = self.creation_date

    def change_used_capacity(self, change: int = 1) -> None:
        self.used_capacity += change
        self.last_modified_date = datetime.now()

    def update_max_capacity(self, new_value) -> None:
        self.max_capacity = new_value
        self.last_modified_date = datetime.now()

    @classmethod
    def from_dict(cls, data):
        return cls(data['entity_type'], data['max_capacity'])

    def __str__(self) -> str:
        return (
            f"Entity Type: {self.entity_type}\n"
            f"Entity ID: {self.id}\n"
            f"Max Capacity: {self.max_capacity}\n"
            f"Used Capacity: {self.used_capacity}\n"
            f"Creation Date: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Last Modified Date: {self.last_modified_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )


class EntityAttributeValue:
    def __init__(self, entity_id: int, name: str, value):
        self.id = UniqueIDGenerator.generate_id()
        self.entity_id = entity_id
        self.name = name.lower()
        self.value = value

    def update_value(self, value) -> None:
        self.value = value

    @classmethod
    def from_dict(cls, data):
        return cls(data['entity_id'], data['name'], data['value'])

    def __str__(self) -> str:
        return (
            f"Attribute ID: {self.id}\n"
            f"Entity ID: {self.entity_id}\n"
            f"Name: {self.name}\n"
            f"Value: {self.value}"
        )
