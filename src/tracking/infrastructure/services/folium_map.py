from datetime import timezone
from io import BytesIO
from zoneinfo import ZoneInfo

import folium

from src.tracking.application.protocols import IMapGenerator
from src.tracking.domain.entities import Tracking

BISHKEK_TZ = ZoneInfo("Asia/Bishkek")


class FoliumMapService(IMapGenerator):
    def generate_map(self, trackings: list[Tracking]) -> BytesIO:
        if not trackings:
            return BytesIO()

        start_loc = trackings[0].location
        m = folium.Map(location=[start_loc.latitude, start_loc.longitude], zoom_start=15, tiles="OpenStreetMap")

        path_coords = [(t.location.latitude, t.location.longitude) for t in reversed(trackings)]

        folium.PolyLine(path_coords, color="blue", weight=4, opacity=0.7).add_to(m)

        for i, t in enumerate(trackings):
            lat = t.location.latitude
            lon = t.location.longitude
            t_utc = t.recorded_at.replace(tzinfo=timezone.utc)
            time_str = t_utc.astimezone(BISHKEK_TZ).strftime("%H:%M")

            if i == 0:
                icon = folium.Icon(color="red", icon="user", prefix="fa")
                popup = f"<b>Current</b><br>{time_str}"
            elif i == len(trackings) - 1:
                icon = folium.Icon(color="green", icon="play", prefix="fa")
                popup = f"Start<br>{time_str}"
            else:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=3,
                    color="blue",
                    fill=True,
                    popup=f"<b>{time_str}</b>",
                ).add_to(m)
                continue

            folium.Marker([lat, lon], icon=icon, popup=popup, tooltip=time_str).add_to(m)

        map_bytes = BytesIO()
        m.save(map_bytes, close_file=False)
        map_bytes.seek(0)

        return map_bytes
