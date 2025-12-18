import asyncio
from pathlib import Path
import httpx

from scraper.sources.source import SourceWebsite
from scraper.sources.itch import SourceItch
from scraper.sources.steam import SourceSteam
from scraper.sources.gamejolt import SourceGamejolt

from utils.env import get_env
from utils.logger import LOGGER

# synchronous client
client = httpx.Client(follow_redirects=True, timeout=30.0)
base_path = get_env("COLLECTION_BASE_PATH")
collection_dir = Path(base_path) / "collection"

sources: list[SourceWebsite] = [
    SourceSteam(client, collection_dir, "steam"),
    SourceGamejolt(client, collection_dir, "gamejolt"),
    SourceItch(client, collection_dir, "itch"),
]

shutdown = asyncio.Event()


async def listen_for_quit():
    loop = asyncio.get_event_loop()
    # we read q from keyboard
    import sys

    while True:
        char = await loop.run_in_executor(None, sys.stdin.read, 1)
        if char.lower() == 'q':
            shutdown.set()
            return


async def _main():
    # create collection folder if not yet there
    collection_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.info("[_main] Press 'q' + Enter to stop gracefully...\n\n")

    tasks = [asyncio.create_task(listen_for_quit())]
    for source in sources:
        LOGGER.info(f"[_main] Scraping: {source.BASE_URL}")
        source.parse_robots_txt()
        tasks.append(asyncio.create_task(source.scrape_documents()))

    # run all scrapers concurrently
    _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    if shutdown.is_set():
        LOGGER.info("[_main] Stopping scrapers...")
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        LOGGER.ok("[_main] Shutdown completed")
    LOGGER.ok("[_main] Scrapers routines completed")


def main():
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        LOGGER.error("[main] Forced shutdown")
