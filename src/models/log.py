from datetime import datetime
from random_id_generator import RandomIdGenerator


class Log:
    def __init__(self, entity_id: int, description: str) -> None:
        self.id = RandomIdGenerator.generate()
        self.entity_id = entity_id
        self.creation_date = datetime.now()
        self.description = description

    def __str__(self):
        return (
            f"[{self.creation_date}] Entity ID: {self.entity_id}\n"
            f"Description: {self.description}"
        )


class EnitityLog(Log):
    def __init__(self, entity_id: int, changed_attribute: str, description: str) -> None:
        super().__init__(entity_id, description)
        self.changed_attribute = self.changed_attribute

    def __str__(self):
        return (
            f"[{self.creation_date}] Entity ID: {self.entity_id}\n"
            f"Changed Attribute: {self.changed_attribute}\n"
            f"Description: {self.description}"
        )


class PersonLog(Log):
    def __init__(self, person_id: int, description: str):
        super().__init__(person_id, description)

    def __str__(self):
        return (
            f"[{self.creation_date}] Entity ID: {self.entity_id}\n"
            f"Description: {self.description}"
        )
