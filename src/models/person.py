from datetime import datetime, timedelta
import random
import names
from src.models.base_model import BaseEntity
from src.models.enums import Gender, EntityStatus, PersonStatus, EntityEnum
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Person(BaseEntity):
    def __init__(
        self,
        name: str,
        gender: Gender,
        birth_date: datetime,
        national_code: str,
        status: PersonStatus,
        current_entity: EntityEnum,
        entity_status: EntityStatus,
        death_date=None,
    ) -> None:
        super().__init__()
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
        self.national_code = national_code
        self.status = status
        self.current_entity = current_entity
        self.entity_status = entity_status
        self.death_date = death_date
        logger.info(f"new person created: id={self.id} creation_date={self.creation_date} name={self.name}")     

    def heal(self) -> None:
        self.status = PersonStatus.ALIVE
        self.modified_date = datetime.now()
        logger.info(f"person status changed to alive: id={self.id} name={self.name}")

    def injure(self) -> None:
        self.status = PersonStatus.INJURED
        self.modified_date = datetime.now()
        logger.info(f"person status changed to injured: id={self.id} name={self.name}")        

    def die(self) -> None:
        self.status = PersonStatus.DEAD
        self.death_date = datetime.now()
        self.modified_date = datetime.now()
        logger.info(f"person status changed to dead: id={self.id} name={self.name}")    

    def changeEntity(self, destination: EntityEnum) -> None:
        self.current_entity = destination
        self.modified_date = datetime.now()
        logger.info(f"person entity changed to {destination.value}: id={self.id} name={self.name}")     

    def changeEntityStatus(self, status: EntityStatus) -> None:
        self.entity_status = status
        self.modified_date = datetime.now()
        logger.info(f"person entity_status changed to {status.value}: id={self.id} name={self.name}")    

    @staticmethod
    def generateRandomPerson():
        genders = list(Gender)
        gender = random.choice(genders)
        name = names.get_full_name(gender="male" if gender == "Male" else "female")
        national_code = str(random.randint(1000000000, 9999999999))

        start_date = datetime(1960, 1, 1)
        end_date = datetime(2005, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_birth_date = start_date + timedelta(days=random_number_of_days)

        return Person(
            name,
            gender,
            random_birth_date,
            national_code,
            PersonStatus.ALIVE,
            EntityEnum.CITY,
            EntityStatus.IDLE,
        )

    def __str__(self) -> str:
        return (
            f"Person ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Gender: {self.gender.name}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d')}\n"
            f"National Code: {self.national_code}\n"
            f"Status: {self.status.name}\n"
            f"Current Entity: {self.current_entity}\n"
            f"Entity Status: {self.entity_status.name}\n"
            f"Creation Date: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Modified Date: {self.modified_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Death Date: {self.death_date.strftime('%Y-%m-%d %H:%M:%S') if self.death_date else 'N/A'}"
        )
