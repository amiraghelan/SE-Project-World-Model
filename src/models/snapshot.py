from src.models.base_model import BaseEntity
from src.models.person import Person


class Snapshot(BaseEntity):
    def __init__(self, entity_id: int, persons: list[Person], earthquake_status: bool) -> None:
        super().__init__()
        self.entity_id: int = entity_id
        self.persons: list[Person] = persons
        self.earthquake_status: bool = earthquake_status

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "persons": self.persons,
            "earthquake_status": self.earthquake_status,
        }
