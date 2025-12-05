from asyncio import sleep
import re
from typing import Optional
import xml.etree.ElementTree as ET

from httpx import Response

from playwright.async_api import async_playwright, Browser

from parsel import Selector

from scraper.sources.source import SourceWebsite
from collection.models.document import Metadata
from utils.logger import LOGGER


class SourceItch(SourceWebsite):
    BASE_URL = "https://itch.io"
    browser: Browser = None

    # skip until this one game url is found and start fron the next one
    last_seen = "https://kingbobski.itch.io/flappy-man"

    # Set a limit on number of entries fetched
    limit = False
    times = 2

    def scrape_metadata_from_response(self, response: Selector) -> Optional[Metadata]:
        """
        Parse a single game's HTML and extract metadata safely.
        """
        try:
            # title
            title = response.css('.game_title::text').get()
            if not title:
                raise ValueError("Title not found")

            # author
            author = response.xpath(
                "//tr[td[text()='Author']]/td/a/text()").get() or "Unknown"

            # description
            desc_elem = response.css(".formatted_description.user_formatted")
            inner_html_list = desc_elem.xpath('./node()').getall()
            description_html = ''.join(inner_html_list).strip()

            # video
            videos = []
            for v in response.css(".video_embed"):
                src = v.css("iframe::attr(src), video::attr(src)").get()
                if src:
                    src = src.strip()
                    if src.startswith("//") and not src.startswith("http"):
                        src = "https:" + src
                    videos.append(src)

            # screenshots URLs
            images = [img.strip() for img in response.css(
                ".screenshot_list img::attr(src)").getall() if img.strip()]

            # price
            price = None
            button = response.css(".button_message")
            if button:
                price_span = button.css("span[itemprop='price']::text").get()
                if price_span:
                    # looks for first number
                    m = re.search(r"(\d+(?:\.\d+)?)", price_span)
                    if m:
                        price = float(m.group(1))
                else:
                    sub_text = button.css("span.sub::text").get()
                    if sub_text:
                        price = sub_text.strip()

            # optional info panel
            info_rows = response.css(".game_info_panel_widget table tr")
            status = genre = rating = tags = platforms = category = published = None
            extra_data = {}

            for row in info_rows:
                key = row.css("td:first-child::text").get()
                if not key:
                    continue
                key = key.strip().lower()
                values = [v.strip() for v in row.css(
                    "td:last-child ::text").getall() if v.strip()]

                if key == "status":
                    status = ', '.join(values)
                    if status == "":
                        status = None
                elif key == "genre":
                    genre = [v for v in values if v != ","]
                elif key == "rating":
                    rating_str = row.css(
                        "[itemprop='ratingValue']::attr(content)").get()
                    if rating_str:
                        try:
                            rating = float(rating_str)
                        except ValueError:
                            pass
                elif key == "tags":
                    tags = [v for v in values if v != ","]
                elif key == "platforms":
                    platforms = [v for v in values if v != ","]
                elif key in ("category"):
                    category = ' '.join(values)
                elif key == "published":
                    published = [v for v in values if v != ","]
                elif key == "author":
                    continue
                else:
                    extra_data[key.replace(
                        " ", "-")] = [v for v in values if v != ","]

            # text
            readable_elements = response.css(
                "p, h1, h2, h3, h4, h5, h6, li, td, th")
            text_nodes = [
                t.strip()
                for el in readable_elements
                for t in el.xpath(".//text()").getall()
                if t.strip()
            ]
            desc_text = Selector(text=description_html).xpath(
                "string()").get().strip()
            text = (" ".join(text_nodes) + desc_text).strip()

            return Metadata(
                title=title.strip(),
                description=description_html.strip(),
                videos=videos,
                images=images,
                price=price,
                status=status,
                author=author.strip(),
                category=category,
                genre=genre,
                rating=rating,
                tags=tags,
                platforms=platforms,
                published=published,
                extra_data=extra_data,
                text=text,
            )

        except Exception as e:
            LOGGER.error(
                f"[SourceItch.scrape_metadata_from_response] Error parsing metadata: {e}")
            return None

    async def parse_sitemap(self):
        try:
            response: Response = self.client.get(self.sitemap_url)
            response.raise_for_status()

            # get XML root and load namespace
            root = ET.fromstring(response.text)
            # we look for: the first {http:// ...}, which is the root url { * } in the root tag (the namespace)
            m = re.match(r"\{(.*)\}", root.tag)
            namespace = {"ns": m.group(1)} if m else {}
            # we get all loc
            locs = [loc.text for loc in root.findall(".//ns:loc", namespace)]

            # filter URLs for game XML pages that have game or game_* where *: [0, 9]
            game_urls_pages = [loc for loc in locs if re.search(
                r"/games(_\d+)?\.xml$", loc)]

            # fetch games urls
            for page_url in game_urls_pages:
                if self.limit:
                    if self.times == 0:
                        return
                    else:
                        self.times -= 1

                # behave
                await sleep(10)
                await self.parse_game_urls_page(page_url)
        except Exception as e:
            LOGGER.error(
                f"[SourceItch.parse_sitemap] Failed to parse sitemap: {e}")

    async def parse_game_urls_page(self, url: str):
        try:
            response: Response = self.client.get(url)
            response.raise_for_status()

            # get XML root and load namespace
            root = ET.fromstring(response.text)
            m = re.match(r"\{(.*)\}", root.tag)
            namespace = {"ns": m.group(1)} if m else {}

            # read all <loc> entries
            game_urls = [loc.text for loc in root.findall(
                ".//ns:loc", namespace)]

            found = False
            for game_url in game_urls:
                if self.limit:
                    if self.times == 0:
                        return
                    else:
                        self.times -= 1

                if self.last_seen:
                    if not found and game_url != self.last_seen:
                        LOGGER.warn(
                            f"[SourceItch.parse_game_urls_page] skipping game: {game_url}")
                        continue
                    elif not found and game_url == self.last_seen:
                        found = True
                        continue

                # behave
                await sleep(1.5)
                await self.parse_game_page(game_url)

        except Exception as e:
            LOGGER.error(
                f"[SourceItch.parse_game_urls_page] Failed to parse XML page: {e}")

    async def parse_game_page(self, url: str):
        try:
            if self.browser == None:
                raise Exception("No browser available")

            # use playwright to go and load page
            page = await self.browser.new_page(
                # proxy={"server": self.get_proxy()},
                extra_http_headers=self.get_headers()
            )
            await page.goto(url, wait_until="networkidle")

            html = await page.content()
            selector = Selector(text=html)

            await page.close()

            metadata = self.scrape_metadata_from_response(selector)
            if metadata:
                # save document
                self.save_metadata_to_collection(
                    metadata=metadata,
                    game_url=url,
                    collection_path=self.COLLECTION_PATH,
                    collection_name=self.COLLECTION_NAME
                )
            else:
                LOGGER.warn(
                    f"[SourceItch.parse_game_page] Skipped game due to missing metadata: {url}")
        except Exception as e:
            LOGGER.error(f"[SourceItch.parse_game_page] Failed: {e}")

    async def scrape_documents(self):
        if not self.sitemap:
            LOGGER.error("[SourceItch.start_requests] Expected sitemap URL")
            return
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            await self.parse_sitemap()
            await self.browser.close()
