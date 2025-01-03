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

    def get_id(self) -> int:
        return self.id

    def change_used_capacity(self, change: int = 1) -> None:
        self.used_capacity += change
        self.last_modified_date = datetime.now()

    def update_max_capacity(self, new_value) -> None:
        self.max_capacity = new_value
        self.last_modified_date = datetime.now()

    @classmethod
    def from_dict(cls, data):
        return cls(data['entity_type'], data['max_capacity'])
    
    def __str__(self):
        return f"entity_type: {self.entity_type} - entity_id: {self.id} - max_cap: {self.max_capacity}"
        


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
    
    def __str__(self):
        return str(vars(self))
        
