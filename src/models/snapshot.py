from random_id_generator import RandomIdGenerator


class Snapshot:
    def __init__(self, entity_id: int, persons: list, earthquake_status: bool) -> None:
        self.id = RandomIdGenerator.generate()
        self.entity_id = entity_id
        self.persons = persons
        self.earthquake_status = earthquake_status

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "persons": self.persons,
            "earthquake_status": self.earthquake_status,
        }
