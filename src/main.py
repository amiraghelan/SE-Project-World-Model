from configparser import ConfigParser
from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict
from fastapi import FastAPI
from src.api.routes import router
from src.models.world_model import WorldModel
from src.utils.logger import get_logger


logger = get_logger(__name__)


class State(TypedDict):
    world_model: WorldModel


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    logger.info("Setting up application dependencies...")

    config = ConfigParser()
    config.read('config.ini')

    # create world model
    time_rate = 1
    world_model = WorldModel(time_rate)
    logger.info(f"world created with time rate of {time_rate}")

    population = config.getint('world-model', 'population', fallback=12)
    world_model.populate_world_model(population)
    logger.info(f"world populated with {population} persons")

    numbers_of_persons_in_store_line = 5
    world_model.fill_store_line(numbers_of_persons_in_store_line)
    logger.info(f"{numbers_of_persons_in_store_line} persons were sent to store line")

    numbers_of_persons_in_hospital_line = 2
    world_model.fill_hospital_line(numbers_of_persons_in_hospital_line)
    logger.info(f"{numbers_of_persons_in_hospital_line} persons were sent to hospital line")

    # return dependencies
    yield {"world_model": world_model}

    del world_model


# setup fastapi app
app = FastAPI(lifespan)
app.include_router(router)
app.include_router(router=router)
