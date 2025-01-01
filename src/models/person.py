from enum import Enum
from datetime import datetime
from src.utils.random_id_generator import UniqueIDGenerator


class PersonStatus(Enum):
    ALIVE = 1
    INJURED = 2
    DEAD = 3


class EntityStatus(Enum):
    INLINE = 1
    SERVICE = 2
    IDLE = 3


class Person:
    def __init__(self, name: str, gender: str, national_code: str, status: PersonStatus, current_entity: str, entity_status: EntityStatus, daeth_date=None) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.name = name
        self.gender = gender
        self.national_code = national_code
        self.status = status
        self.current_entity = current_entity
        self.entity_status = entity_status
        self.creation_date = datetime.now()
        self.daeth_date = daeth_date

    def heal(self) -> None:
        self.status = PersonStatus.ALIVE

    def injured(self) -> None:
        self.status = PersonStatus.INJURED

    def die(self) -> None:
        self.status = PersonStatus.DEAD
        self.daeth_date = datetime.now()

    def changeEntity(self, destination: str) -> None:
        self.current_entity = destination

    def changeEntityStatus(self, status: EntityStatus) -> None:
        self.entity_status = status


class PersonLog:
    pass
