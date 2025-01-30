from datetime import datetime
from src.models.base_model import BaseEntity
import math
from pydantic import BaseModel


class Entity(BaseEntity):
    def __init__(self, entity_type: str, max_capacity: int) -> None:
        super().__init__()
        self.entity_type = entity_type.lower()
        self.max_capacity = max_capacity
        self.used_capacity = 0

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

    x: float
    y: float
    health: float = 100.0  # Default health value for an entity

    def take_damage(self, damage_amount: float):
        """
        Applies damage to the entity, reducing its health by 'damage_amount'.
        
        If health goes below 0, it is set to 0 to indicate the entity is effectively 'destroyed' or 'dead'.
        """
        self.health -= damage_amount
        if self.health < 0:
            self.health = 0

    def calculate_distance(self, epicenter: tuple) -> float:
        """
        Calculates the distance between the entity's position (x, y) and the provided epicenter (ex, ey).
        
        This method could be useful if we want each entity to handle its own distance calculation.
        """
        ex, ey = epicenter
        return math.dist((self.x, self.y), (ex, ey))


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
