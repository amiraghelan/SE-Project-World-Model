from enum import Enum


class PersonStatus(Enum):
    ALIVE = 'alive'
    INJURED = 'injured'
    DEAD = 'dead'


class EntityStatus(Enum):
    INLINE = 'inline'
    SERVICE = 'service'
    IDLE = 'idle'


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
