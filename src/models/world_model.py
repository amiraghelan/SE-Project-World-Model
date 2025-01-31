from datetime import datetime
import random
from time import sleep
import threading

from src.models.person import Person
from src.models.snapshot import Snapshot
from src.models.entity import Entity, EntityAttributeValue
from src.models.enums import EntityStatus, EntityEnum, PersonStatus
from src.utils.logger import get_logger
import src.config as config

logger = get_logger(__name__)


class WorldModel:
    _last_eq_clock = 0
    _last_refill_clock = 0
    _last_populate_clock = 0

    def __init__(self, time_rate: int = 1) -> None:
        self.time_rate = time_rate
        self.earthquake_status = False
        self.entities: dict[int, Entity] = dict()
        self.eavs: dict[int, list[EntityAttributeValue]] = dict()
        self.persons: dict[int, Person] = dict()
        self.start_date = datetime.now()
        self.automate_thread = threading.Thread(target=self.automate)
        self.automate_thread.daemon = True
        self.automate_thread.start()
        logger.info(
            f"world_model created at {self.start_date} with time_rate = {self.time_rate}"
        )

    # ==register====================================================================
    def register(
        self,
        entity_type: str,
        max_capacity: int,
        eav: dict[str, str | int | dict | list],
    ) -> dict:
        entity = Entity(EntityEnum(entity_type.lower()), max_capacity)
        entity_id = entity.id

        self.entities[entity_id] = entity
        self.eavs[entity_id] = [
            EntityAttributeValue(entity.id, name, value) for name, value in eav.items()
        ]

        logger.info(
            f"register - new entity regitered - entity_type: {entity_type} - max-cap: {max_capacity} - id: {entity_id}"
        )

        return {
            "entity_id": entity_id,
            "time_rate": self.time_rate,
            "start_date": self.start_date,
            "current_clock": self.clock(),
        }

    # ==snapshot====================================================================
    def match_snapshot_persons(self, entity: Entity) -> list[Person]:
        entity_type = entity.entity_type
        res = [
            person
            for person in self.persons.values()
            if person.current_entity == entity_type
            and person.entity_status == EntityStatus.INLINE
            and person.status != PersonStatus.DEAD
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

        if not person  or person.status == PersonStatus.DEAD:
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
            logger.error(f"accept-person - entity not found - entity_id: {entity_id}")
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
            f"accept-person - entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
        )
        return {"accepted": accepted_persons, "rejected": rejected_persons}

    # =============================================================================

    # ==service done===============================================================
    def validate_person_for_service_done(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person  or person.status == PersonStatus.DEAD:
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
            logger.error(f"service_done: entity not found - entity_id: {entity_id}")
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
                        person.changeEntity(EntityEnum.HOSPITAL)
                    case "hospital":
                        person.changeEntityStatus(EntityStatus.IDLE)
                        person.changeEntity(EntityEnum.CITY)
                    case "store":
                        person.changeEntityStatus(EntityStatus.IDLE)
                        person.changeEntity(EntityEnum.CITY)
            else:
                rejected_persons.append(person_id)

        entity.change_used_capacity(-1 * len(accepted_persons))
        logger.info(
            f"service_done: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
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

    # ==person injury==============================================================
    def person_injury(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"person_injury: entity not found - entity_id: {entity_id}")
            return {"accepted": [], "rejected": persons_id}
        
        accepted_persons = []
        rejected_persons = []
        for person_id in persons_id:
            if self.validate_person_for_service_done(entity, person_id):
                person = self.persons[person_id]
                accepted_persons.append(person_id)
                person.changeEntityStatus(EntityStatus.INLINE)
                person.changeEntity(EntityEnum.ECU)
            else:
                rejected_persons.append(person_id)
        
        entity.change_used_capacity(-1 * len(accepted_persons))
        logger.info(
            f"person_injury: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
        )
        return {"accepted": accepted_persons, "rejected": rejected_persons}
    #==============================================================================
    
    #== person death===============================================================
    def validate_person_for_person_death(self, entity: Entity, person_id: int) -> bool:
        person = self.persons.get(person_id)

        if not person or person.status == PersonStatus.DEAD:
            return False

        if person.current_entity != entity.entity_type:
            return False

        return True

    def person_death(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
            logger.error(f"person_death: entity not found - entity_id: {entity_id}")
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
            f"person_death: entity_id: {entity_id} - accepteds: {accepted_persons} - rejecteds: {rejected_persons}"
        )

        return {"accepted": accepted_persons, "rejected": rejected_persons}

    def start_earthquake(self) -> None:
        self.earthquake_status = True
        logger.info(f"earthquake started at clock={ self.clock()} ")

    def stop_earthquake(self) -> None:
        self.earthquake_status = False
        logger.info(f"earthquake stopped at clock={ self.clock()} ")
        

    def entity_exists(self, entity_id) -> Entity | None:
        entity = self.entities.get(entity_id)

        if not entity:
            return None

        return entity

    def populate_worldModel(self, persons_count: int = 1):
        for _ in range(persons_count):
            person = Person.generateRandomPerson()
            self.persons[person.id] = person
        logger.info(
            f"world_model populated with {persons_count} persons at clock = {self.clock()}"
        )

    def fill_entity_line(self, entity: EntityEnum, count: int = 1):
        logger.info(f"trying to fill {entity.value} line with {count} persons")
        persons = list(self.persons.values())
        idle_persons = list(
            filter(
                lambda x: x.entity_status == EntityStatus.IDLE
                and x.current_entity == EntityEnum.CITY,
                persons,
            )
        )
        idle_persons_count = len(idle_persons)
        c = 0
        for _ in range(min(count, idle_persons_count)):
            person = random.choice(idle_persons)
            person.changeEntity(entity)
            person.changeEntityStatus(EntityStatus.INLINE)
            c += 1
        logger.info(
            f"{entity.value} line filled with {c} persons at clock={self.clock()}"
        )

    def clock(self):
        now = datetime.now()
        delta = now - self.start_date
        return int(delta.total_seconds() * self.time_rate)

    def automate(self):
        while True:
            clock = self.clock()

            if clock - WorldModel._last_eq_clock >= config.EQ_INTERVAL:
                self.start_earthquake()
                WorldModel._last_eq_clock = clock

            if self.earthquake_status and (
                clock - WorldModel._last_eq_clock >= config.EQ_DURATION
            ):
                self.stop_earthquake()

            if clock - WorldModel._last_refill_clock >= config.REFILL_INTERVAL:
                self.fill_entity_line(EntityEnum.STORE, config.STORE_REFILL_COUNT)
                self.fill_entity_line(EntityEnum.HOSPITAL, config.HOSPITAL_REFILL_COUNT)
                self.fill_entity_line(EntityEnum.ECU, config.ECU_REFILL_COUNT)
                WorldModel._last_refill_clock = clock
                
            if clock - WorldModel._last_populate_clock >= config.REP_INTERVAL:
                self.populate_worldModel(config.REP_COUNT)
                WorldModel._last_populate_clock = clock
            
            sleep(1 / self.time_rate)