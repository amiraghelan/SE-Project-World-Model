from typing import Annotated, cast
from src.models.world_model import WorldModel
from src.api.schemas import (
    RegisterBody,
    AcceptPersonBody,
    RegisterResponse,
    ServiceDoneBody,
    UpdateSelfBody,
    PersonDeathBody,
    PersonInjuryBody,
)
from src.utils.logger import get_logger


from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

logger = get_logger(__name__)

router = APIRouter()


def get_world_model(request: Request) -> WorldModel:
    return cast(WorldModel, request.state.world_model)


# we should migrate all logic to business service
# create entity and entity attribute value here is not good practice


@router.post("/api/register", response_model=RegisterResponse)
def register(
    world_model: Annotated[WorldModel, Depends(get_world_model)], body: RegisterBody
):
    logger.info(f"new register request - entity_type: {body.entity_type}")
    response = world_model.register(body.entity_type, body.max_capacity, body.eav)

    return response


@router.get("/api/snapshot/{entity_id}")
def snapshot(
    world_model: Annotated[WorldModel, Depends(get_world_model)], entity_id: int
):  
    logger.info(f"new snapshot request - entity_id: {entity_id}")
    response = world_model.snapshot(entity_id=entity_id)
    if not response:
        logger.error(f"in snapshot api: entity_id was not found - id:{entity_id}")
        return JSONResponse({"message": "entity does not exist in the worldmodel"}, 404)

    return response


@router.post("/api/accept-person")
def accept_person(
    world_model: Annotated[WorldModel, Depends(get_world_model)], body: AcceptPersonBody
):
    logger.info(f"new accpet-person request - entity_id: {body.entity_id} - persons_id: {body.persons_id}")
    response = world_model.accept_person(body.entity_id, body.persons_id)
    return response


@router.post("/api/service-done")
def service_done(
    world_model: Annotated[WorldModel, Depends(get_world_model)], body: ServiceDoneBody
):
    response = world_model.service_done(body.entity_id, body.persons_id)
    return response


@router.put("/api/update-self")
def update_self(
    world_model: Annotated[WorldModel, Depends(get_world_model)], body: UpdateSelfBody
):
    response = world_model.update_self(body.entity_id, body.max_capacity, body.eav)
    return response


@router.post("/api/person-injury")
def person_injury(
    world_model: Annotated[WorldModel, Depends(get_world_model)], body: PersonInjuryBody
):
    response = world_model.person_injury(body.entity_id, body.persons_id)
    return response


@router.post("/api/person-death")
def person_death(
    world_model: Annotated[WorldModel, Depends(get_world_model)], body: PersonDeathBody
):
    response = world_model.person_death(body.entity_id, body.persons_id)
    return response
