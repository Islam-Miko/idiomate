import asyncio
import sys

import uvicorn

from app.server import app
from core.settings import get_settings
from core.utils.logger import setup_logging
from src.main import main as bot_main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [app|bot]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    settings = get_settings()
    setup_logging(settings)
    if mode == "app":
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            reload=False,
            workers=1,
        )
    elif mode == "bot":
        asyncio.run(bot_main())
    else:
        print("Unknown mode. Use 'app' or 'bot'.")
        sys.exit(1)
