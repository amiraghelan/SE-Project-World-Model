from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict
from fastapi import FastAPI
from src.api.routes import router
from src.models.enums import EntityEnum
from src.models.world_model import WorldModel
from src.utils.logger import get_logger
import src.config as config

# Configure the root logge


logger = get_logger(__name__)


class State(TypedDict):
    world_model: WorldModel


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    logger.info("Setting up application dependencies...")

    # create world model
    world_model = WorldModel(config.TIME_RATE)
    world_model.populate_worldModel(config.INITIAL_POPULATION)
    world_model.fill_entity_line(EntityEnum.HOSPITAL, config.INITIAL_HOSPITAL_LINE)
    world_model.fill_entity_line(EntityEnum.ECU, config.INITIAL_ECU_LINE)
    world_model.fill_entity_line(EntityEnum.STORE, config.INITIAL_STORE_LINE)

    # return dependencies
    yield {"world_model": world_model}

    del world_model


# setup fastapi app

app = FastAPI(lifespan=lifespan)
app.include_router(router=router)
