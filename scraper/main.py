import asyncio
from pathlib import Path
import httpx

from scraper.sources.source import SourceWebsite
from scraper.sources.itch import SourceItch
from scraper.sources.steam import SourceSteam
from scraper.sources.gamejolt import SourceGamejolt

from utils.env import get_env

# synchronous client
client = httpx.Client(follow_redirects=True, timeout=30.0)
base_path = get_env("COLLECTION_BASE_PATH")
collection_dir = Path(base_path) / "collection"

sources: list[SourceWebsite] = [
    SourceItch(client, collection_dir, "itch"),
    SourceSteam(client, collection_dir, "steam"),
    SourceGamejolt(client, collection_dir, "gamejolt")
]


async def _main():
    # create collection folder if not yet there
    collection_dir.mkdir(parents=True, exist_ok=True)

    for source in sources:
        print(f"\nScraping for source: {source.BASE_URL}")
        source.parse_robots_txt()

        print(source.warmed)
        print(source.disallow_paths)

        await source.scrape_documents()


def main():
    asyncio.run(_main())
