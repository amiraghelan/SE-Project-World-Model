from datetime import datetime, timedelta
import random
import names
from src.utils.random_id_generator import UniqueIDGenerator
from src.models.enums import Gender, EntityStatus, PersonStatus





class Person:
    def __init__(self, name: str, gender: Gender, birth_date: datetime, national_code: str, status: PersonStatus, current_entity: str, entity_status: EntityStatus, daeth_date=None) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
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

    @staticmethod
    def generateRandomPerson():
        genders = list(Gender)
        gender = random.choice(genders)
        name = names.get_full_name(gender='male' if gender == 'Male' else 'female')
        national_code = str(random.randint(1000000000, 9999999999))

        start_date = datetime(1960, 1, 1) 
        end_date = datetime(2005, 12, 31) 
        time_between_dates = end_date - start_date 
        days_between_dates = time_between_dates.days 
        random_number_of_days = random.randrange(days_between_dates) 
        random_birth_date = start_date + timedelta(days=random_number_of_days)

        return Person(name, gender, random_birth_date, national_code, PersonStatus.ALIVE, 'city', EntityStatus.IDLE)

    def __str__(self):
        return f" name: {self.name} \n geneder: {self.gender.value} \n birth date: {self.birth_date} \n natioanl code: {self.national_code} \n status: {self.status.value} \n entity: {self.current_entity} \n entity status: {self.entity_status.value}"


class PersonLog:
    pass
