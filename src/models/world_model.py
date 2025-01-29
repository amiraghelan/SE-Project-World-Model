import asyncio
import random

from typing import Union
from configparser import ConfigParser
from datetime import datetime, timedelta

from src.models.person import Person
from src.models.snapshot import Snapshot
from src.models.entity import Entity, EntityAttributeValue
from src.models.enums import EntityStatus, PersonStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = ConfigParser()
config.read('config.ini')


class WorldModel:
    def __init__(self, time_rate: int = 1) -> None:
        self.time_rate = time_rate
        self.earthquake_status = False
        self.entities: dict[int, Entity] = dict()
        self.eavs: dict[int, list[EntityAttributeValue]] = dict()
        self.persons: dict[int, Person] = dict()
        self.start_date = datetime.now()

        # read config
        self.injury_probability = config.getfloat('world-model', 'injury_probability', fallback=0.1)
        self.store_probability = config.getfloat('world-model', 'store_probability', fallback=0.2)
        self.action_interval = timedelta(seconds=config.getint('world-model', 'action_interval', fallback=10))

        asyncio.create_task(self.random_actions())

    async def random_actions(self):
        while True:
            await asyncio.sleep(self.action_interval.total_seconds())
            self.perform_random_actions()

    def perform_random_actions(self):
        for person in self.persons.values():
            if person.current_entity == "city":
                if random.random() < self.injury_probability:
                    self.__person_injury_from_world_model([person.id])
                elif random.random() < self.store_probability:
                    self.fill_store_line(1)

    # ==register====================================================================

    def register(
        self,
        entity_type: str,
        max_capacity: int,
        eav: dict[str, str | int | dict | list],
    ) -> dict:
        entity = Entity(entity_type, max_capacity)
        entity_id = entity.id

        self.entities[entity_id] = entity
        self.eavs[entity_id] = [
            EntityAttributeValue(entity.id, name, value) for name, value in eav.items()
        ]

        logger.info(f"new entity registered - entity_type: {entity_type} - max-cap: {max_capacity} - id: {entity_id}")

        return {"entity_id": entity_id, "time_rate": self.time_rate}

    # ==snapshot====================================================================

    def match_snapshot_persons(self, entity: Entity) -> list:
        entity_type = entity.entity_type
        match entity_type:
            case "store":
                return [
                    person
                    for person in self.persons.values()
                    if person.current_entity == "store"
                    and person.entity_status == EntityStatus.INLINE
                ]
            case "hospital":
                return [
                    person
                    for person in self.persons.values()
                    if person.current_entity == "hospital"
                    and person.entity_status == EntityStatus.INLINE
                ]
            case "ecu":
                return [
                    person
                    for person in self.persons.values()
                    if person.current_entity == "ecu"
                    and person.entity_status == EntityStatus.INLINE
                ]
            case _:
                return []

    def snapshot(self, entity_id: int) -> Union[Snapshot, bool]:
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

        if person.current_entity != entity.entity_type or person.entity_status != EntityStatus.INLINE:
            return False

        return True

    def accept_person(self, entity_id: int, persons_ids: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id=entity_id)
        if not entity:
            logger.error(f"in accept-person: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_ids}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_ids:
            if self.validate_person_to_accept(entity, person_id):
                person = self.persons.get(person_id)
                if person:
                    person.changeEntity(entity.entity_type)
                    person.changeEntityStatus(EntityStatus.SERVICE)
                    accepted_persons.append(person_id)
            else:
                rejected_persons.append(person_id)

        entity.change_used_capacity(len(accepted_persons))
        logger.info(f"in accept-person: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}")
        return {"accepted": accepted_persons, "rejected": rejected_persons}
    # =============================================================================

    # ==service done===============================================================
    def validate_person_for_service_done(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person:
            return False

        if person.current_entity != entity.entity_type or person.entity_status != EntityStatus.SERVICE:
            return False

        return True

    def service_done(self, entity_id: int, persons_ids: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"in service_done: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_ids}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_ids:
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
        logger.info(f"in service_done: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}")

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

    def validate_persons_for_injury(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person:
            return False

        if person.current_entity != entity.entity_type or entity.entity_type != "store" or person.status != PersonStatus.INJURED:
            return False

        return True

    def __person_injury_from_world_model(self, persons_ids: list) -> bool:
        accepted_persons = []
        rejected_persons = []
        for person_id in persons_ids:
            person = self.persons[person_id]
            if person.status == PersonStatus.INJURED:
                accepted_persons.append(person_id)
                person.injure()
                person.changeEntity("ecu")
                person.changeEntityStatus(EntityStatus.INLINE)
            else:
                rejected_persons.append(person_id)

        logger.info(f"in person_injury_from_world_model: - accepteds: {accepted_persons} - rejecteds: {rejected_persons}")
        return {"accepted": accepted_persons, "rejected": rejected_persons}

    # should check if only store or world model call can happen
    # handle above statement in validate_persons_for_injury and another method for world model call person injury
    def person_injury(self, entity_id: int, persons_ids: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"in person_injury: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_ids}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_ids:
            if self.validate_persons_for_injury(entity, person_id):
                person = self.persons[person_id]
                accepted_persons.append(person_id)
                person.injure()
                person.changeEntity("ecu")
                person.changeEntityStatus(EntityStatus.INLINE)
            else:
                rejected_persons.append(person_id)

        logger.info(f"in person_injury: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}")
        return {"accepted": accepted_persons, "rejected": rejected_persons}

    def validate_person_for_person_death(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person:
            return False

        if person.current_entity != entity.entity_type:
            return False

        return True

    # should check if only hospital or police call can happen
    def person_death(self, entity_id: int, persons_ids: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"in person_death: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_ids}

        accepted_persons = []
        rejected_persons = []
        for person_id in persons_ids:
            if self.validate_person_for_person_death(entity, person_id):
                person = self.persons[person_id]
                accepted_persons.append(person_id)
                person.die()
            else:
                rejected_persons.append(person_id)

        entity.change_used_capacity(-1 * len(accepted_persons))
        logger.info(f"in person_death: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}")

        return {"accepted": accepted_persons, "rejected": rejected_persons}

    def start_earthquake(self) -> None:
        self.earthquake_status = True

    def stop_earthquake(self) -> None:
        self.earthquake_status = False

    def entity_exists(self, entity_id: int) -> Entity | None:
        entity = self.entities.get(entity_id)

        if not entity:
            return None

        return entity

    def populate_world_model(self, persons_count: int = 1):
        for _ in range(persons_count):
            person = Person.generateRandomPerson()
            self.persons[person.id] = person

    def fill_store_line(self, count: int = 1):
        persons = list(self.persons.values())
        idle_persons = list(
            filter(
                lambda x: x.entity_status == EntityStatus.IDLE
                and x.current_entity == "city",
                persons,
            )
        )
        idle_persons_count = len(idle_persons)

        for _ in range(min(count, idle_persons_count)):
            person = random.choice(idle_persons)
            person.changeEntity("store")
            person.changeEntityStatus(EntityStatus.INLINE)

    def fill_hospital_line(self, count: int = 1):
        persons = list(self.persons.values())
        idle_persons = list(
            filter(
                lambda x: x.entity_status == EntityStatus.IDLE
                and x.current_entity == "city",
                persons,
            )
        )
        idle_persons_count = len(idle_persons)

        for _ in range(min(count, idle_persons_count)):
            person = random.choice(idle_persons)
            person.changeEntity("hospital")
            person.changeEntityStatus(EntityStatus.INLINE)

    def personLog(self):
        pass

    def entityLog(self):
        pass

    def log(self):
        pass
