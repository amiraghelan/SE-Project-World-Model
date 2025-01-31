from datetime import datetime
from src.models.base_model import BaseEntity
from src.models.enums import EntityEnum


class Entity(BaseEntity):
    def __init__(self, entity_type: EntityEnum, max_capacity: int) -> None:
        super().__init__()
        self.entity_type: EntityEnum = entity_type
        self.max_capacity: int = max_capacity
        self.used_capacity: int = 0

    def change_used_capacity(self, change: int = 1) -> None:
        self.used_capacity += change
        self.modified_date = datetime.now()

    def update_max_capacity(self, new_value) -> None:
        self.max_capacity = new_value
        self.modified_date = datetime.now()

    def __str__(self) -> str:
        return (
            f"Entity Type: {self.entity_type}\n"
            f"Entity ID: {self.id}\n"
            f"Max Capacity: {self.max_capacity}\n"
            f"Used Capacity: {self.used_capacity}\n"
            f"Creation Date: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Modified Date: {self.modified_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )


class EntityAttributeValue(BaseEntity):
    def __init__(self, entity_id: int, name: str, value: int | str | list | dict):
        super().__init__()
        self.entity_id = entity_id
        self.name = name.lower()
        self.value = value

    def update_value(self, value) -> None:
        self.value = value
        self.modified_date = datetime.now()

    def __str__(self) -> str:
        return (
            f"Attribute ID: {self.id}\n"
            f"Entity ID: {self.entity_id}\n"
            f"Name: {self.name}\n"
            f"Value: {self.value}"
        )
