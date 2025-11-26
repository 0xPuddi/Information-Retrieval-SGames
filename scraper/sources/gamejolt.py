from httpx import HTTPError

from collection.models.document import Document
from scraper.sources.source import SourceWebsite


class SourceGamejolt(SourceWebsite):
    BASE_URL = "https://gamejolt.com"

    async def scrape_documents(self) -> list[Document]:
        return
