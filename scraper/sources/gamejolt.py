from http.cookiejar import Cookie
import re
from typing import List, Optional
from parsel import Selector

from collection.models.document import Document, Metadata
from scraper.sources.source import SourceWebsite

from playwright.async_api import async_playwright, Browser
from playwright_stealth import Stealth

from asyncio import sleep

from utils.logger import LOGGER


class SourceGamejolt(SourceWebsite):
    # extremely inefficient search
    BASE_URL = "https://gamejolt.com"
    browser: Browser = None

    ITERATIONS: None | int = None

    def scrape_metadata_from_response(self, response: Selector, videos: list[str]) -> Optional[Metadata]:
        """
        Parse a single game's HTML and extract metadata safely.
        """
        try:
            # title
            title = response.css('.page-header-content h1 a::text').get()
            if not title:
                raise ValueError("Title not found")
            title = title.strip()

            # author
            author = response.css(
                '.page-header-content a[href^="/@"]::text').get()
            if not author:
                author = "Unknown"
            else:
                author = author.strip()

            # description
            desc_elem = response.css(
                ".content-viewer.game-description-content")
            inner_html_list = desc_elem.xpath('./node()').getall()
            description_html = ''.join(inner_html_list).strip()

            # video is done through parameter passed in because we need a click

            # screenshots URLs
            images = []
            media_items = response.css(
                '.scroll-scroller.media-bar .media-bar-item')
            for item in media_items:
                # check play icon
                if not item.css('.jolticon-play'):
                    # it's an image
                    img_src = item.css('img.img-responsive::attr(src)').get()
                    if img_src and 'game-screenshot' in img_src:
                        img_src = img_src.strip()
                        if img_src.startswith("//"):
                            img_src = "https:" + img_src
                        images.append(img_src)

            # cards: prices and platforms
            prices = []
            platforms = []
            cards = response.css(".game-package-card")

            for card in cards:
                # ctitle
                card_title = card.css(".card-title h4::text").get()
                card_title = card_title.strip() if card_title else None

                # price
                price = None
                pricing_card = card.css(".game-package-card-pricing")

                if pricing_card:
                    # old price exists
                    old_price_text = pricing_card.css(
                        ".game-package-card-pricing-amount-old::text"
                    ).get()

                    if old_price_text:
                        # get number
                        m = re.search(r"(\d+(?:\.\d+)?)", old_price_text)
                        if m:
                            price = float(m.group(1))

                    else:
                        # otherwise get current price
                        price_text_amount = pricing_card.css(
                            ".game-package-card-pricing-amount span::text"
                        ).get()
                        price_text_amount_itself = pricing_card.css(
                            ".game-package-card-pricing-amount::text"
                        ).get()
                        price_text_tag = pricing_card.css(
                            ".game-package-card-pricing-tag::text"
                        ).get()

                        price_text = None
                        if price_text_tag:
                            price_text = price_text_tag
                        if price_text_amount_itself:
                            price_text = price_text_amount_itself
                        if price_text_amount:
                            price_text = price_text_amount

                        if price_text:
                            txt = price_text.strip().lower()
                            if "free" in txt:
                                price = "Free"
                            elif "name" in txt:
                                price = "Name Your Price"
                            else:
                                # get number
                                m = re.search(r"(\d+(?:\.\d+)?)", price_text)
                                price = float(
                                    m.group(1)) if m else price_text.strip()

                # add prices
                prices.append({
                    card_title: price
                })

                # platforms
                platform_icons = card.css(".card-meta .jolticon")
                for icon in platform_icons:
                    cls = icon.attrib.get("class", "")

                    if "jolticon-windows" in cls:
                        if "windows" not in platforms:
                            platforms.append("windows")
                    if "jolticon-mac" in cls:
                        if "mac" not in platforms:
                            platforms.append("mac")
                    if "jolticon-linux" in cls:
                        if "linux" not in platforms:
                            platforms.append("linux")
                    if "jolticon-html5" in cls:
                        if "html5" not in platforms:
                            platforms.append("html5")

            # status, published
            status = published = None
            # status container
            status_metadata = response.css(
                '.-metadata:contains("Development Stage")').get()
            if status_metadata:
                status_selector = Selector(text=status_metadata)
                status = status_selector.css(
                    '.-metadata-value span::text').get()

            # published container
            published_metadata = response.css(
                '.-metadata:contains("Published On")').get()
            if published_metadata:
                published_selector = Selector(text=published_metadata)
                published = published_selector.css(
                    '.-metadata-value::text').get()

            # extra data: views + likes
            extra_data = {}
            views = likes = None
            metrics = response.css(".-statbar .-metric strong::text")

            # expect both
            if len(metrics) >= 2:
                # views
                v = metrics[0].get().strip()
                if v:
                    views = v

                # likes
                l = metrics[1].get().strip()
                if l:
                    likes = l
            extra_data["views"] = views
            extra_data["likes"] = likes

            # there is no exact rating, we'll use likes
            rating = None

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

            # we sue a dict to remove duplicates and maintain order
            tags = list(dict.fromkeys(h[1:]
                                      for h in re.findall(r"#\S+", text)))
            genre = []
            for i in range(3):
                if len(tags) > i:
                    genre.append(tags[i])
            category = tags[0] if len(tags) > 0 else None

            return Metadata(
                title=title,
                description=description_html,
                videos=videos,
                images=images,
                price=prices,
                status=status,
                author=author,
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
                f"[SourceGamejolt.scrape_metadata_from_response] Error parsing metadata: {e}")
            return None

    async def parse_game_page(self, url: str, thumbnail_link: str, cookies: List[Cookie]):
        LOGGER.info(f"[SourceGamejolt.parse_game_page]: scraping game {url}")
        # used to collect next games
        games = []
        page = None
        try:
            if self.browser == None:
                raise Exception("No browser available")

            # add cookies to page
            context = await self.browser.new_context()
            await context.add_cookies(cookies)

            page = await context.new_page()
            await page.goto(url, wait_until='load')

            await sleep(1)

            # skip mature audience button if there
            try:
                LOGGER.info(
                    "[SourceGamejolt.parse_game_page]: Check if 'Proceed to Game' button happears...")
                await page.click("button:has-text('Proceed to Game')", timeout=3000)
                LOGGER.ok(
                    "[SourceGamejolt.parse_game_page]: Clicked 'Proceed to Game' button")
            except:
                LOGGER.info(
                    "[SourceGamejolt.parse_game_page]: 'Proceed to Game' button not found, continuing")

            # open the show more description to load it all
            try:
                LOGGER.info(
                    "[SourceGamejolt.parse_game_page]: Opening show more")
                button = page.get_by_role("button", name="Show more")
                await sleep(1)
                await button.click()
                await sleep(1)
                LOGGER.ok(
                    "[SourceGamejolt.parse_game_page]: Opened show more")
            except Exception as e:
                LOGGER.info(
                    f"[SourceGamejolt.parse_game_page]: Unable to open button: {e}")

            html = await page.content()
            selector = Selector(text=html)

            # collect games
            game_items = selector.css('.game-list-item')
            for item in game_items:
                # game page link
                game_url = item.css('a.-title::attr(href)').get()
                if not game_url:
                    continue
                if game_url.startswith('/'):
                    game_url = f"https://gamejolt.com{game_url}"

                # thumbnail image link
                thumbnail_link = item.css(
                    'img.img-responsive.-img::attr(src)').get()
                if not thumbnail_link:
                    continue

                games.append({
                    'url': game_url,
                    'thumbnail': thumbnail_link
                })

            # videos links need a button to be cicked before they show up
            # get all videos media-bar-items
            video_items = []
            try:
                video_items = page.locator(
                    ".media-bar-item:has(img[src*='video-thumbnail'])",)
            except Exception as _:
                video_items = []
            count = await video_items.count()

            videos = []

            # collect url
            for i in range(count):
                item = video_items.nth(i)

                await item.scroll_into_view_if_needed()
                await item.click()

                # get iframe
                iframe_handle = await page.query_selector(".media-bar-lightbox-item.active iframe[src]")

                if iframe_handle:
                    # extract video URL
                    video_url = await iframe_handle.get_attribute("src")
                    videos.append(video_url)
                else:
                    LOGGER.warn(
                        f"iframe not found even with video thumbnail for: {url}")

                # close the video lightbox
                await page.click("button:has-text('Close')")

            await page.close()

            metadata = self.scrape_metadata_from_response(selector, videos)
            if metadata:
                # cast
                metadata: Metadata

                # add thumbnail
                if thumbnail_link:
                    metadata.images.insert(0, thumbnail_link)

                # save document
                self.save_metadata_to_collection(
                    metadata=metadata,
                    game_url=url,
                    collection_path=self.COLLECTION_PATH,
                    collection_name=self.COLLECTION_NAME
                )
            else:
                LOGGER.info(
                    f"[SourceGamejolt.parse_game_page] Skipped game due to missing metadata: {url}")
        except Exception as e:
            if page:
                await page.close()
            LOGGER.error(f"[SourceGamejolt.parse_game_page] Failed: {e}")
        return games

    async def routine(self):
        LOGGER.info("[SourceGamejolt.routine] starting routine")
        context = await self.browser.new_context()
        page = await context.new_page()
        await page.goto(self.BASE_URL,  wait_until="load")

        await sleep(5)

        LOGGER.info(
            "[SourceGamejolt.routine] Moving to store and processing games in the page")
        # we traverse to store
        await page.click("a[href='/games']")
        await page.wait_for_load_state('load')

        # trying to accept and collect cookies
        await sleep(1)
        try:
            LOGGER.info(
                "[SourceGamejolt.routine] Checking consent button...")
            consent_button = await page.wait_for_selector(
                "button:has-text('Consent')", timeout=10_000
            )
            # button showed up we simulate click
            await sleep(3)
            if consent_button:
                await consent_button.click()
                LOGGER.info(
                    "[SourceGamejolt.routine] Consent button clicked")
        except:
            LOGGER.info(
                "[SourceGamejolt.routine] Consent button not found, skipping...")

        await sleep(2)
        LOGGER.info(
            "[SourceGamejolt.routine] collecting cookies")
        cookies = await context.cookies()

        # wait for elements
        await page.wait_for_selector('._game-grid-items', timeout=10000)
        games_data = []
        # get grid items
        game_items = await page.query_selector_all('._game-grid-item')

        # process games up until last loaded thumbnail
        for item in game_items:
            try:
                # game page link
                game_url = await item.query_selector('.game-thumbnail')
                if not game_url:
                    continue

                game_url = await game_url.get_attribute('href')
                if not game_url:
                    continue
                # realtive url
                if game_url.startswith('/'):
                    game_url = f"https://gamejolt.com{game_url}"

                # thumbnail image link
                thumbnail_link = await item.query_selector('.img-responsive.-img')
                if thumbnail_link:
                    thumbnail_link = await thumbnail_link.get_attribute('src')

                if not thumbnail_link:
                    # not loaded because of lazy loading
                    break

                games_data.append({
                    'url': game_url,
                    'thumbnail': thumbnail_link
                })

            except Exception as e:
                LOGGER.error(
                    f"[SourceGamejolt.routine] Error processing item: {e}")
                continue

        # we dont need this page anymore
        await page.close()

        # try and switch to headless
        await self.browser.close()
        async with Stealth().use_async(async_playwright()) as p:
            self.browser = await p.chromium.launch(headless=True)

            # we traverse to each and for each we collected recommended games
            while (not self.ITERATIONS or self.ITERATIONS > 0) and len(games_data) > 0:
                new_games_data = []
                for i in range(len(games_data)):
                    new_games_data.extend(await self.parse_game_page(games_data[i]['url'], games_data[i]['thumbnail'], cookies))
                    await sleep(3.5)

                if self.ITERATIONS:
                    self.ITERATIONS -= 1
                games_data = new_games_data
                LOGGER.info(
                    f"[SourceGamejolt.routine] moving to collected recommendations found: {len(new_games_data)} games")
                await sleep(5)

    async def scrape_documents(self) -> list[Document]:
        async with Stealth().use_async(async_playwright()) as p:
            self.browser = await p.chromium.launch(headless=False)
            await self.routine()
