from asyncpg import ConnectionDoesNotExistError
from loguru import logger
from tortoise import Tortoise

__all__ = (
    "init_db",
    "models",
    "utils"
)

from tortoise.exceptions import DBConnectionError

from project.crying.config import Database, config, MODELS_DIR, TIME_ZONE


async def init_db(db: Database):
    logger.debug(f"Initializing Database {db.database}[{db.host}]...")
    data = {
        "db_url": db.url,
        "modules": {"models": [MODELS_DIR]},
        "timezone": str(TIME_ZONE),
    }
    try:
        await Tortoise.init(**data)
        await Tortoise.generate_schemas()
    except (ConnectionDoesNotExistError, DBConnectionError) as e:
        logger.warning(e)
        logger.info("Creating a new database ...")
        await Tortoise.init(**data, _create_db=True)
        await Tortoise.generate_schemas()
        logger.success(f"New database {db.database} created")

    logger.debug(f"Database {db.database}[{db.host}] initialized")
