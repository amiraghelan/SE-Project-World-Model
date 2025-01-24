from src.models.base_model import BaseEntity
from src.models.person import Person
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Snapshot(BaseEntity):
    def __init__(self, entity_id: int, persons: list[Person], earthquake_status: bool) -> None:
        super().__init__()
        self.entity_id: int = entity_id
        self.persons: list[Person] = persons
        self.earthquake_status: bool = earthquake_status
        logger.info(f"snapshot with id:{self.id} was created for entity with id:{entity_id}")
    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "persons": self.persons,
            "earthquake_status": self.earthquake_status,
        }
