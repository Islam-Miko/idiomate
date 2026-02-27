import logging

from aiohttp import web

from src.infrastructure.database.setup import db_helper
from src.tracking.application.use_cases import GetUserStatusUseCase2
from src.tracking.infrastructure.database.repositories import TrackingRepo
from src.tracking.presentation.api.handlers import api_get_tracking

logger = logging.getLogger(__name__)


async def start_web_server(app: web.Application, host: str, port: int):
    app.router.add_get("/idiomate/api/tracking", api_get_tracking)
    async with db_helper.session_factory() as s:
        app["get_status_use_case"] = GetUserStatusUseCase2(TrackingRepo(s))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"Web server started at http://{host}:{port}")
    return runner
