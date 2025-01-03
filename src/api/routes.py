from src.models.world_model import WorldModel
from src.models.entity import Entity, EntityAttributeValue
from src.api.schemas import RegisterBody, AcceptPersonBody, ServiceDoneBody, UpdateSelfBody, PersonDeathBody, PersonInjuryBody

from fastapi import APIRouter, Request

world_model = WorldModel(100)
world_model.populate_worldModel(12)
world_model.fill_store_line(5)
router = APIRouter()


@router.post('/api/register')
async def register(req: Request, body: RegisterBody):
    entity = Entity.from_dict(body.model_dump())
    eavs = []
    for name, value in body.eav.items():
        eav = EntityAttributeValue(entity_id=entity.id, name=str(name), value=value)
        eavs.append(eav)

    response = world_model.register(entity.entity_type, entity.max_capacity, eavs)
    return response


@router.get('/api/snapshot/{entity_id}')
def snapshot(entity_id: int):
    response = world_model.snapshot(entity_id=entity_id)
    return response


@router.post('/api/accept-person')
def accept_person(body: AcceptPersonBody):
    response = world_model.accept_person(body.entity_id, body.persons_id)
    return response


@router.post('/api/service-done')
def service_done(body: ServiceDoneBody):
    response = world_model.service_done(body.entity_id, body.persons_id)
    return response


@router.put('/api/update-self')
def update_self(body: UpdateSelfBody):
    eavs = []
    for name, value in body.eav.items():
        eav = EntityAttributeValue(entity_id=body.entity_id, name=str(name), value=value)
        eavs.append(eav)
    response = world_model.update_self(body.entity_id, body.max_capacity, eavs)
    return response


@router.post('/api/person-injury')
def person_injury(body: PersonInjuryBody):
    response = world_model.person_injury(body.entity_id, body.persons_id)
    return response


@router.post('/api/person-death')
def person_death(body: PersonDeathBody):
    response = world_model.person_death(body.entity_id, body.persons_id)
    return response
