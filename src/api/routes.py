from src.models.world_model import WorldModel
from src.api.schemas import RegisterBody, AcceptPersonBody, ServiceDoneBody, UpdateSelfBody, PersonDeathBody, PersonInjuryBody

from fastapi import APIRouter, Request

world_model = WorldModel(100)
world_model.populate_worldModel(12)
world_model.fill_store_line(5)
router = APIRouter()

# we should migrate all logic to business service
# create entity and entity attribute value here is not good practice


@router.post('/api/register')
async def register(body: RegisterBody):
    response = world_model.register(body.entity_type, body.max_capacity, body.eav)
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
    response = world_model.update_self(body.entity_id, body.max_capacity, body.eav)
    return response


@router.post('/api/person-injury')
def person_injury(body: PersonInjuryBody):
    response = world_model.person_injury(body.entity_id, body.persons_id)
    return response


@router.post('/api/person-death')
def person_death(body: PersonDeathBody):
    response = world_model.person_death(body.entity_id, body.persons_id)
    return response
