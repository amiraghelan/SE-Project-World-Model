from datetime import datetime

from src.models.person import Person
from src.models.snapshot import Snapshot
from src.models.entity import Entity, EntityAttributeValue
from src.models.enums import EntityStatus, PersonStatus



class WorldModel:

    def __init__(self, time_rate: int) -> None:
        self.time_rate = time_rate
        self.earthquake_status = False
        #added type to dicts
        self.entities: dict[int, Entity] = dict()
        self.eavs: dict[int, list[EntityAttributeValue]] = dict()
        self.persons: dict[int, Person] = dict()
        self.start_date = datetime.now()

    # removed queue_capacity
    def register(self, entity_type: str, max_capacity: int, eavs: dict) -> dict:
        entity = Entity(entity_type, max_capacity)
        entity_id = entity.get_id()

        self.entities[entity_id] = entity

        self.eavs[entity_id] = [
            EntityAttributeValue(entity_id, key, value) for key, value in eavs.items()
        ]
        #changed return type to dict
        return {"entity_id": entity_id, "time_rate": self.time_rate}

    #changed return type to snapshot
    def sanpshot(self, entity_id: int) -> Snapshot:
        
        entity = self.entity_exists(entity_id)
        
        if not entity:
            return Snapshot(entity_id, [], self.earthquake_status)
        
        return Snapshot(entity_id, self.match_snapshot_persons(entity), self.earthquake_status)

    def accept_person(self, entity_id: int, persons_id: list) -> bool:
        # i think the and should be replaced with or
        if not self.entity_exists(entity_id) or not self.validate_persons_for_entity(entity_id, persons_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].changeEntityStatus(EntityStatus.SERVICE)

        return True

    def service_done(self, entity_id: int, persons_id: list) -> bool:
        entity = self.entity_exists(entity_id)
        if not entity or not self.validate_persons_for_entity(entity_id, persons_id):
            return False
        
        #changed service done based on the entity type
        for person_id in persons_id:
            person = self.persons[person_id]
            match entity.entity_type:
                case 'ecu':
                    person.changeEntityStatus(EntityStatus.INLINE)
                    person.changeEntity('hospital')
                case 'hospital':
                    person.changeEntityStatus(EntityStatus.IDLE)
                    person.changeEntity('city')
                case 'store':
                    person.changeEntityStatus(EntityStatus.IDLE)
                    person.changeEntity('city')
                    
        return True

    def update_self(self, entity_id: int, max_capacity: int, eavs: dict) -> bool:
        entity = self.entity_exists(entity_id)
        if not entity:
            return False
        
        eav = self.eavs.get(entity_id)

        if not eav:
            return False

        entity.update_max_capacity(max_capacity)

        eav = [EntityAttributeValue(entity_id, key, value)
               for key, value in eavs.items()]

        return True

    def person_injery(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) or not self.validate_persons_for_entity(entity_id, persons_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].injured()

        return True

    def person_death(self, entity_id: int, persons_id: list) -> bool:
        if not self.entity_exists(entity_id) or not self.validate_persons_for_entity(entity_id, persons_id):
            return False

        for person_id in persons_id:
            self.persons[person_id].die()

        return True

    def start_earthquake(self) -> None:
        self.earthquake_status = True
    #added method to stop the workmodel
    def stop_earthquake(self) -> None:
        self.earthquake_status = False

    # TODO what one person is valid or one is not?
    def validate_persons_for_entity(self, entity_id: int, persons_id: list):
        entity = self.entities.get(entity_id)
        
        if entity is None:
            return False
        
        for person_id in persons_id:
            person = self.persons.get(person_id)
            if not person or person.current_entity != entity.entity_type:
                return False

        return True

    def entity_exists(self, entity_id):
        entity = self.entities.get(entity_id)

        if not entity:
            return False
        
        return entity

    def match_snapshot_persons(self, entity: Entity) -> list:
        entity_type = entity.entity_type
        #changed persons based on the entity type
        match entity_type:
            case 'store':
                return [person for person in self.persons.values() if person.current_entity == 'store' and person.entity_status == EntityStatus.INLINE ]
            case 'hospital':
                return [person for person in self.persons.values() if person.current_entity == 'hospital' and person.entity_status == EntityStatus.INLINE ]
            case 'ecu':
                return [person for person in self.persons.values() if person.status == PersonStatus.INJURED and person.current_entity != 'hospital' ]
            case _:
                return [] 
            
    def personLog(self):
        pass

    def entityLog(self):
        pass

    def log(self):
        pass
