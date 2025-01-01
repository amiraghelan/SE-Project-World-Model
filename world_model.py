import datetime
from person import *
from snapshot import Snapshot
from entity import Entity, EntityAttributeValue


class WorldModel:

    def __init__(self, time_rate: int) -> None:
        self.time_rate = time_rate
        self.earthquake_status = False
        self.entities = dict()
        self.eavs = dict()
        self.persons = dict()

    def register(self, type: str, queue_capacity: int, max_capacity: int, eavs: dict) -> int:
        entity = Entity(type, queue_capacity, max_capacity)
        entity_id = entity.get_id()

        self.entities[entity_id] = entity

        self.eavs[entity_id] = [
            EntityAttributeValue(entity_id, key, value) for key, value in eavs.items()
        ]

        return entity_id

    def sanpshot(self, entity_id: int) -> list:
        if not self.entity_exists(entity_id):
            return Snapshot(entity_id, [], self.earthquake)

        return Snapshot(entity_id, self.match_persons(entity_id), self.earthquake)

    def accept_person(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) and not self.validate_persons_for_entity(entity_id, person_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].changeEntityStatus(EntityStatus.SERVICE)

        return True

    def service_done(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) and not self.validate_persons_for_entity(entity_id, person_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].changeEntityStatus(EntityStatus.IDLE)

        return True

    def update_self(self, entity_id: int, queue_capacity: int, max_capacity: int, eavs: dict) -> bool:
        if not self.entity_exists(entity_id):
            return False

        entity = self.entities.get(entity_id)
        eav = self.eavs.get(entity_id)

        if not eav:
            return False

        entity.update_queue_capacity(queue_capacity)
        entity.update_max_capacity(max_capacity)

        eav = [EntityAttributeValue(entity_id, key, value)
               for key, value in eavs.items()]

        return True

    def person_injery(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) and not self.validate_persons_for_entity(entity_id, person_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].injured()

        return True

    def person_death(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) and not self.validate_persons_for_entity(entity_id, person_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].die()

        return True

    def earthquake(self) -> None:
        self.earthquake_status = True

    def validate_persons_for_entity(self, entity_id: int, persons_id: list):
        entity = self.entities.get(entity_id)

        for person_id in persons_id:
            person = self.persons.get(person_id)
            if not person or person.current_entity != entity.type:
                return False

        return True

    def entity_exists(self, entity_id):
        entity = self.entities.get(entity_id, False)

        if not entity:
            return False

    def match_persons(self, entity_id: int) -> list:
        entity = self.entities.get(entity_id)

        return [person for person in self.persons.values()
                if person.current_entity == entity.type]

    def personLog(self):
        pass

    def entityLog(self):
        pass

    def log(self):
        pass
