from httpx import HTTPError

from collection.models.document import Document
from scraper.sources.source import SourceWebsite


class SourceSteam(SourceWebsite):
    BASE_URL = "https://store.steampowered.com"

    async def scrape_documents(self) -> list[Document]:
        return
