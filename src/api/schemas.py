from pydantic import BaseModel


class RegisterBody(BaseModel):
    entity_type: str
    max_capacity: int
    eav: dict[str, str | int | dict | list]


class AcceptPersonBody(BaseModel):
    entity_id: int
    persons_id: list[int]


class ServiceDoneBody(AcceptPersonBody):
    pass


class PersonInjuryBody(AcceptPersonBody):
    pass


class PersonDeathBody(AcceptPersonBody):
    pass


class UpdateSelfBody(BaseModel):
    entity_id: int
    max_capacity: int
    eav: dict[str, str | int]

class EarthquakeSchema(BaseModel):
    """
    This schema holds the parameters used to simulate an earthquake in the World Model.
    """

    intensity: float
    # Intensity or magnitude of the earthquake

    duration: float
    # Duration of the quake in seconds

    epicenter_x: float
    # X coordinate of the quake's epicenter

    epicenter_y: float
    # Y coordinate of the quake's epicenter

