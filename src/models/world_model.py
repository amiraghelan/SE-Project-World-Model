from datetime import datetime
import random

from src.models.person import Person
from src.models.snapshot import Snapshot
from src.models.entity import Entity, EntityAttributeValue
from src.models.enums import EntityStatus, PersonStatus


class WorldModel:
    def __init__(self, time_rate: int = 1) -> None:
        self.time_rate = time_rate
        self.earthquake_status = False
        self.entities: dict[int, Entity] = dict()
        self.eavs: dict[int, list[EntityAttributeValue]] = dict()
        self.persons: dict[int, Person] = dict()
        self.start_date = datetime.now()
    
    
    #==register====================================================================
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

        # TODO log entity Registeration
        # print("Entity registered: ")
        # print(entity)
        # print("Entity Attribute Values: ")
        # for e in self.eavs[entity_id]:
        #     print(e)

        return {"entity_id": entity_id, "time_rate": self.time_rate}


    #==snapshot====================================================================
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
    
    def snapshot(self, entity_id: int) -> Snapshot | bool:
        entity = self.entity_exists(entity_id)

        if not entity:
            return False

        return Snapshot(
            entity_id, self.match_snapshot_persons(entity), self.earthquake_status
        )

    #==accpet persons=============================================================
    def validate_person_to_accept(self, entity: Entity, person_id: int)->bool:
        person = self.persons.get(person_id)
        
        if not person:
            return False
        
        if person.current_entity != entity.entity_type or person.entity_status != EntityStatus.INLINE:
            return False
        
        return True
    
    def accept_person(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id=entity_id)
        if not entity:
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

        return {"accepted": accepted_persons, "rejected": rejected_persons}
    #=============================================================================
    
    #==service done===============================================================
    def validate_person_for_service_done(self, entity: Entity, person_id: int)->bool:
        person = self.persons.get(person_id)
        
        if not person:
            return False
        
        if person.current_entity != entity.entity_type or person.entity_status != EntityStatus.SERVICE:
            return False
        
        return True
    
    def service_done(self, entity_id: int, persons_id: list) -> dict[str, list[int]]:
        entity = self.entity_exists(entity_id)
        if not entity:
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

        return {"accepted": accepted_persons, "rejected": rejected_persons}
    #=============================================================================

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
            person.changeEntity("ecu")
            person.changeEntityStatus(EntityStatus.INLINE)

        entity = self.entities.get(entity_id)
        if entity is not None:
            entity.change_used_capacity(-1 * len(persons_id))

        return True

    # should check if only hospital or police call can happen
    def person_death(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) or not self.validate_persons_for_entity(
            entity_id, persons_id
        ):
            return False

        for person_id in persons_id:
            self.persons[person_id].die()

        entity = self.entities.get(entity_id)
        if entity is not None:
            entity.change_used_capacity(-1 * len(persons_id))

        return True

    def start_earthquake(self) -> None:
        self.earthquake_status = True

    def stop_earthquake(self) -> None:
        self.earthquake_status = False

    def entity_exists(self, entity_id):
        entity = self.entities.get(entity_id)

        if not entity:
            return False

        return entity

    

    def populate_worldModel(self, persons_count: int = 1):
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
