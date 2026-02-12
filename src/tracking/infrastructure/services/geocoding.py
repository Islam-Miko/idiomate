import asyncio
import logging

from geopy.geocoders import ArcGIS

from src.tracking.application.protocols import IGeoService

logger = logging.getLogger(__name__)


class ArcGISGeoService(IGeoService):
    def __init__(self):
        self.geolocator = ArcGIS()

        self._cache = {}  #! change to DATABASE or CACHE

    async def get_address(self, lat: float, lon: float) -> str:
        lat_rounded = round(lat, 4)
        lon_rounded = round(lon, 4)

        cache_key = (lat_rounded, lon_rounded)

        if cache_key in self._cache:
            logger.debug(f"Geo cache HIT for {cache_key}")
            return self._cache[cache_key]

        try:
            location = await asyncio.to_thread(self.geolocator.reverse, f"{lat}, {lon}", timeout=5)
            if location:
                address = location.address
                logger.debug(f"Geo API success: {address}")

                self._cache[cache_key] = address
                return address

            logger.warning(f"Geo API returned None for {lat}, {lon}")
            return "Not found"

        except Exception as e:
            logger.error(f"ArcGIS Error: {e}")
            return "Service error"
