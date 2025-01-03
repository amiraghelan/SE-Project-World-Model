from pydantic import BaseModel


class RegisterBody(BaseModel):
    entity_type:str
    max_capacity:int
    eav: dict[str, str|int|dict|list]
    
class AcceptPersonBody(BaseModel):
    entity_id:int
    persons_id:list[int]

class ServiceDoneBody(AcceptPersonBody):
    pass

class PersonInjuryBody(AcceptPersonBody):
    pass

class PersonDeathBody(AcceptPersonBody):
    pass

class UpdateSelfBody(BaseModel):
    entity_id:int
    max_capacity:int
    eav: dict[str, str|int]