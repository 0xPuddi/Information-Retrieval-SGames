
from abc import ABC, abstractmethod
import hashlib
import json
from pathlib import Path

from httpx import Client, HTTPError
from collection.models.document import Document, Metadata, Source

import random


class SourceWebsite(ABC):
    # required
    COLLECTION_PATH: str
    COLLECTION_NAME: str
    BASE_URL: str
    client: Client

    warmed: bool = False
    disallow_paths: list[str] = []

    stiemap: bool = False
    stiemap_url: str

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]

    ACCEPT_LANGUAGES = [
        'en-US,en;q=0.9',
        'en-GB,en;q=0.9',
        'en-US,en;q=0.9,es;q=0.8',
        'en-CA,en;q=0.9',
    ]

    REFERERS = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://duckduckgo.com/',
        'https://www.reddit.com/',
    ]

    def __init__(self,  client: Client, COLLECTION_PATH: str, COLLECTION_NAME: str):
        self.client = client
        self.COLLECTION_PATH = COLLECTION_PATH
        self.COLLECTION_NAME = COLLECTION_NAME

    # rotate headers
    def get_headers(self) -> dict:
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(self.ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': random.choice(self.REFERERS),
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    # rotate proxies
    def get_proxy(self, for_playwright: bool = True) -> str:
        try:
            # fetch proxy list
            response = self.client.get(
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all'
            )
            response.raise_for_status()

            # parse proxies
            proxies = [p.strip()
                       for p in response.text.split('\n') if p.strip()]

            if not proxies:
                raise ValueError("No proxies available")

            # choose random proxy
            proxy = random.choice(proxies)

            # Format based on target
            if for_playwright:
                # Playwright format: "http://ip:port"
                if not proxy.startswith('http'):
                    proxy = f"http://{proxy}"
                return proxy
            else:
                # httpx format: dict with scheme
                if not proxy.startswith('http'):
                    proxy = f"http://{proxy}"
                return proxy

        except Exception as e:
            print(f"[get_proxy] Failed to fetch proxy: {e}")
            return None

    def parse_robots_txt(self) -> bool:
        """
        Fetch and collect robots.txt information
        """

        robots_url = self.BASE_URL + "/robots.txt"

        try:
            response = self.client.get(robots_url)
            response.raise_for_status()

            new_disallow_paths = []
            for line in response.text.splitlines():
                line = line.strip()

                prefix = "Sitemap:"
                if line.startswith(prefix):
                    path = line[len(prefix):].strip()
                    if path:
                        self.sitemap = True
                        self.stiemap_url = path

                prefix = "Disallow:"
                if line.startswith(prefix):
                    path = line[len(prefix):].strip()
                    if path:
                        new_disallow_paths.append(path)
            self.disallow_paths = new_disallow_paths
            self.warmed = True

            return True
        except HTTPError as e:
            print(
                f"Error occurred when reading robots.txt for {self.BASE_URL}, error: {e}")
            return False

    def save_metadata_to_collection(
            self,
            metadata: Metadata,
            game_url: str,
            collection_path: str,
            collection_name: str
    ):
        """
        Create a Document and append it to a collection JSON file.
        """
        # ensure folder exists
        path = Path(collection_path)
        path.mkdir(parents=True, exist_ok=True)

        # prepare file
        collection_file = path / f"{collection_name}.json"

        # compute deterministic id
        unique_str = f"{collection_name}-{game_url}-{metadata.title}"
        id_hash = hashlib.sha256(unique_str.encode("utf-8")).hexdigest()

        # create the document
        document = Document(
            id=id_hash,
            source=Source(name=collection_name, url=game_url),
            metadata=metadata
        )

        # load existing data if present
        if collection_file.exists():
            try:
                with open(collection_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        # append only if not already there
        if not any(d["id"] == document.id for d in data):
            data.append(document.model_dump(mode="json"))
            with open(collection_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(
                f"[save_metadata_to_collection] Added document '{metadata.title}' to {collection_file}")
        else:
            print(
                f"[save_metadata_to_collection] Document '{metadata.title}' already exists in {collection_file}")

    @abstractmethod
    async def scrape_documents(self):
        """
        Scrape and return a list of document data
        """
        pass
