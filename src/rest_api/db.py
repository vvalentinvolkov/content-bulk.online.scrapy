import asyncio
import logging

logger = logging.getLogger(__name__)


async def init_mongo(host: str, port: int, db: str) -> AsyncIOMotorDatabase:
    logger.info(f'init mongo')
    loop = asyncio.get_event_loop()
    conn = AsyncIOMotorClient(host=host, port=port, io_loop=loop)
    return conn[db]


async def setup_mongo(app: web.Application) -> None:
    config = app['config']
    app['db'] = await init_mongo(app, config.MONGODB_URI)

    async def close_mongo(app: web.Application) -> None:
        logger.info('close mongo')
        app['db'].client.close()

    app.on_cleanup.append(close_mongo)