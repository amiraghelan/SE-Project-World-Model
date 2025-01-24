from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict
from fastapi import FastAPI
from src.api.routes import router
from src.models.world_model import WorldModel
from src.utils.logger import get_logger

# Configure the root logge


logger = get_logger(__name__)


class State(TypedDict):
    world_model: WorldModel


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    logger.info("Setting up application dependencies...")

    # create world model
    world_model = WorldModel(1)
    logger.info("world created with time rate of 1")
    world_model.populate_worldModel(12)
    logger.info("world populated with 12 persons")
    world_model.fill_store_line(5)
    world_model.fill_hospital_line(2)
    logger.info("5 persons where sent to store line")
    logger.info("2 persons where sent to hospital line")

    # return dependencies
    yield {"world_model": world_model}

    del world_model


# setup fastapi app

app = FastAPI(lifespan=lifespan)
app.include_router(router=router)
