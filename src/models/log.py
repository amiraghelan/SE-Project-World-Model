from datetime import datetime
from src.utils.random_id_generator import UniqueIDGenerator


class Log:
    def __init__(self, entity_id: int, description: str) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.entity_id = entity_id
        self.creation_date = datetime.now()
        self.description = description

    def __str__(self):
        return (
            f"[{self.creation_date}] Entity ID: {self.entity_id}\n"
            f"Description: {self.description}"
        )


class EntityLog(Log):
    def __init__(self, entity_id: int, changed_attribute: str, description: str) -> None:
        super().__init__(entity_id, description)
        self.changed_attribute = changed_attribute

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
