import logging

from aiohttp import web

logger = logging.getLogger(__name__)


async def api_get_tracking(request: web.Request):
    user_id = request.query.get("user_id")

    use_case = request.app["get_status_use_case"]

    lat, lon = await use_case.execute(user_id)

    data = {"status": "ok", "current": {"lat": lat, "lon": lon}}

    headers = {
        "Access-Control-Allow-Origin": "*",
    }
    return web.json_response(data, headers=headers)
