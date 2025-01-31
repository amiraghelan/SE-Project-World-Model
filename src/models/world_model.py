from datetime import datetime
import random

from src.models.person import Person
from src.models.snapshot import Snapshot
from src.models.entity import Entity, EntityAttributeValue
from src.models.enums import EntityStatus, EntityEnum
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WorldModel:
    def __init__(self, time_rate: int = 1) -> None:
        self.time_rate = time_rate
        self.earthquake_status = False
        self.entities: dict[int, Entity] = dict()
        self.eavs: dict[int, list[EntityAttributeValue]] = dict()
        self.persons: dict[int, Person] = dict()
        self.start_date = datetime.now()

    # ==register====================================================================
    def register(
        self,
        entity_type: str,
        max_capacity: int,
        eav: dict[str, str | int | dict | list],
    ) -> dict:
        entity = Entity(EntityEnum(entity_type), max_capacity)
        entity_id = entity.id

        self.entities[entity_id] = entity
        self.eavs[entity_id] = [
            EntityAttributeValue(entity.id, name, value) for name, value in eav.items()
        ]

        logger.info(
            f"new entity regitered - entity_type: {entity_type} - max-cap: {max_capacity} - id: {entity_id}"
        )

        return {
            "entity_id": entity_id,
            "time_rate": self.time_rate,
            "start_date": self.start_date,
            "current_clock": self.clock(),
        }

    # ==snapshot====================================================================
    def match_snapshot_persons(self, entity: Entity) -> list:
        entity_type = entity.entity_type
        res = [
                    person
                    for person in self.persons.values()
                    if person.current_entity == entity_type
                    and person.entity_status == EntityStatus.INLINE
                ]
        return res

    def snapshot(self, entity_id: int) -> Snapshot | bool:
        entity = self.entity_exists(entity_id)

        if not entity:
            return False

        return Snapshot(
            entity_id, self.match_snapshot_persons(entity), self.earthquake_status
        )

    # ==accpet persons=============================================================
    def validate_person_to_accept(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person:
            return False

        if (
            person.current_entity != entity.entity_type
            or person.entity_status != EntityStatus.INLINE
        ):
            return False

        return True

    def accept_person(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id=entity_id)
        if not entity:
            logger.error(f"in accept-person: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_id}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_id:
            if self.validate_person_to_accept(entity, person_id):
                person = self.persons.get(person_id)
                if person:
                    person.changeEntity(entity.entity_type)
                    person.changeEntityStatus(EntityStatus.SERVICE)
                    accepted_persons.append(person_id)
            else:
                rejected_persons.append(person_id)

        entity.change_used_capacity(len(accepted_persons))
        logger.info(
            f"in accept-person: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
        )
        return {"accepted": accepted_persons, "rejected": rejected_persons}

    # =============================================================================

    # ==service done===============================================================
    def validate_person_for_service_done(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person:
            return False

        if (
            person.current_entity != entity.entity_type
            or person.entity_status != EntityStatus.SERVICE
        ):
            return False

        return True

    def service_done(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"in service_done: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_id}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_id:
            if self.validate_person_for_service_done(entity, person_id):
                person = self.persons[person_id]
                accepted_persons.append(person_id)
                match entity.entity_type:
                    case "ecu":
                        person.changeEntityStatus(EntityStatus.INLINE)
                        person.changeEntity("hospital")
                    case "hospital":
                        person.changeEntityStatus(EntityStatus.IDLE)
                        person.changeEntity("city")
                    case "store":
                        person.changeEntityStatus(EntityStatus.IDLE)
                        person.changeEntity("city")
            else:
                rejected_persons.append(person_id)

        entity.change_used_capacity(-1 * len(accepted_persons))
        logger.info(
            f"in service_done: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
        )

        return {"accepted": accepted_persons, "rejected": rejected_persons}
    # =============================================================================

    def update_self(
        self, entity_id: int, max_capacity: int, eav: dict[str, str | int | dict | list]
    ) -> bool:
        entity = self.entity_exists(entity_id)
        if not entity:
            return False

        if not self.eavs.get(entity_id):
            return False

        entity.update_max_capacity(max_capacity)

        self.eavs[entity_id] = [
            EntityAttributeValue(entity.id, name, value) for name, value in eav.items()
        ]

        return True

    # should check if only store or world model call can happen
    def person_injury(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) or not self.validate_persons_for_entity(
            entity_id, persons_id
        ):
            return False

        for person_id in persons_id:
            person = self.persons[person_id]
            person.injure()
            person.changeEntity(EntityEnum.ECU)
            person.changeEntityStatus(EntityStatus.INLINE)

        entity = self.entities.get(entity_id)
        if entity is not None:
            entity.change_used_capacity(-1 * len(persons_id))

        return True

    def validate_person_for_person_death(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person:
            return False

        if person.current_entity != entity.entity_type:
            return False

        return True

    # should check if only hospital or police call can happen
    def person_death(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"in person_death: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_id}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_id:
            if self.validate_person_for_person_death(entity, person_id):
                person = self.persons[person_id]
                accepted_persons.append(person_id)
                person.die()
            else:
                rejected_persons.append(person_id)

        entity.change_used_capacity(-1 * len(accepted_persons))
        logger.info(
            f"in person_death: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
        )

        return {"accepted": accepted_persons, "rejected": rejected_persons}

    def start_earthquake(self) -> None:
        self.earthquake_status = True

    def stop_earthquake(self) -> None:
        self.earthquake_status = False

    def entity_exists(self, entity_id) -> Entity | None:
        entity = self.entities.get(entity_id)

        if not entity:
            return None

        return entity

    def populate_worldModel(self, persons_count: int = 1):
        for _ in range(persons_count):
            person = Person.generateRandomPerson()
            self.persons[person.id] = person

    def fill_entity_line(self, entity: EntityEnum, count: int = 1):
        persons = list(self.persons.values())
        idle_persons = list(
            filter(
                lambda x: x.entity_status == EntityStatus.IDLE
                and x.current_entity == EntityEnum.CITY,
                persons,
            )
        )
        idle_persons_count = len(idle_persons)

        for _ in range(min(count, idle_persons_count)):
            person = random.choice(idle_persons)
            person.changeEntity(entity)
            person.changeEntityStatus(EntityStatus.INLINE)

    def clock(self):
        now = datetime.now()
        delta = now - self.start_date
        return (delta.total_seconds() * self.time_rate) // 1
