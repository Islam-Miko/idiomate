import logging

from core.settings import Settings


def setup_logging(settings: Settings):
    logging.basicConfig(
        level=logging.DEBUG if settings.ENVIRONMENT.is_debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
