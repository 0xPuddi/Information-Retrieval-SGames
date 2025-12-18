from asyncio import sleep
import json
import re
from typing import Optional
from scraper.sources.source import SourceWebsite

from playwright.async_api import async_playwright, Browser

from parsel import Selector

from scraper.sources.source import SourceWebsite
from collection.models.document import Metadata
from utils.logger import LOGGER


class SourceSteam(SourceWebsite):
    BASE_URL = "https://store.steampowered.com"
    browser: Browser = None

    ITERATIONS: None | int = None

    def scrape_metadata_from_response(self, response: Selector) -> Optional[Metadata]:
        """
        Parse a single game's HTML and extract metadata safely.
        """
        try:
            # block containint: title, author, genres and published date
            block = response.css('#genresAndManufacturer')

            # title
            title = block.xpath(
                './/b[text()="Title:"]/following-sibling::text()[1]').get()
            if not title:
                raise ValueError("Title not found")
            else:
                title.strip()

            # author
            author = block.xpath(
                './/div[@class="dev_row"][b/text()="Developer:"]//a/text()').get() or "Unknown"
            if author:
                author = author.strip()

            # genres
            genre = block.xpath(
                './/b[text()="Genre:"]/following-sibling::span//a/text()').getall()

            # published
            published = block.xpath(
                './/b[text()="Release Date:"]/following-sibling::text()[1]').get()
            if published:
                published = published.strip()

            # description
            desc_elem = response.css("#game_area_description")
            html = desc_elem.get()
            # remove only <h2>About This Game</h2>
            description_html = re.sub(
                r'<h2[^>]*>About This Game<\/h2>', '', html, count=1).strip()

            # videos
            videos = []
            # images
            images = []

            # get json from data-props
            raw = response.css(
                '.gamehighlight_desktopcarousel::attr(data-props)').get()
            data = json.loads(raw)

            for trailer in data.get('trailers', []):
                video_url = trailer.get('hlsManifest', None)
                if video_url:
                    videos.append(video_url)

            for screenshot in data.get('screenshots', []):
                image_url = screenshot.get('standard', None)
                if image_url:
                    images.append(image_url)

            # prices and platforms
            platforms = []
            prices = []
            for wrapper in response.css('.game_area_purchase_game_wrapper'):
                # cost title
                cost_title = wrapper.css(
                    '.game_area_purchase_game .title::text').get()
                if cost_title:
                    cost_title = cost_title.replace("Buy", '', 1).strip()
                else:
                    # skip for no title
                    continue

                # cost
                price_block = wrapper.css('.game_purchase_action_bg')
                cost = None

                # discounted price (normal + bundle)
                discount = price_block.css('.discount_block')
                if discount:
                    original = discount.css(
                        '.discount_original_price::text').get()
                    if original:
                        # extract number using regex
                        match = re.search(r'[\d,.]+', original)
                        if match:
                            # convert to float
                            cost = float(match.group(0))

                # normal price
                if cost is None:
                    normal_price = price_block.css(
                        '.game_purchase_price.price::text').get()
                    if normal_price:
                        match = re.search(r'[\d,.]+', normal_price)
                        if match:
                            cost = float(match.group(0))

                # Free to Play
                if cost is None:
                    free_price = price_block.xpath(
                        './/div[contains(@class,"game_purchase_price") and contains(text(),"Free")]//text()'
                    ).get()
                    if free_price:
                        cost = free_price.strip()

                # bundle not discounted
                if cost is None:
                    bundle_price = price_block.css(
                        '.discount_final_price .your_price_label + div::text').get()
                    if bundle_price:
                        match = re.search(r'[\d,.]+', bundle_price)
                        if match:
                            cost = float(match.group(0).replace(',', ''))

                # nothing found
                if cost is None:
                    cost = "Unknown"

                # Store final price dictionary
                prices.append({
                    cost_title: cost
                })

                # platforms
                plat_elems = wrapper.css(
                    '.game_area_purchase_platform span.platform_img')
                for p in plat_elems:
                    classes = p.attrib.get('class', '')
                    if 'win' in classes and "windows" not in platforms:
                        platforms.append("windows")
                    elif 'mac' in classes and "macos" not in platforms:
                        platforms.append("macos")
                    elif 'linux' in classes and "linux" not in platforms:
                        platforms.append("linux")

            # tags
            tags = []
            tags = [
                tag.get().strip()
                for tag in response.css('.glance_tags.popular_tags a.app_tag::text')
            ]

            # category
            category = tags[0] if len(tags) > 0 else None

            # rating
            rating = response.css(
                '.summary_text .game_review_summary::text').get()
            rating = rating.strip() if rating else None

            # status
            status = None
            coming_soon = response.css('.game_area_comingsoon')
            if coming_soon:
                status = "To be Released"
            else:
                status = "Published"

            # text
            readable_elements = response.css(
                "p, h1, h2, h3, h4, h5, h6, li, td, th")
            text_nodes = [
                t.strip()
                for el in readable_elements
                for t in el.xpath(".//text()").getall()
                if t.strip()
            ]
            # extract text from description_html
            desc_text = Selector(text=description_html).xpath(
                "string()").get().strip()
            text = (" ".join(text_nodes) + desc_text).strip()

            return Metadata(
                title=title.strip(),
                description=description_html,
                videos=videos,
                images=images,
                price=prices,
                status=status,
                author=author.strip(),
                category=category,
                genre=genre,
                rating=rating,
                tags=tags,
                platforms=platforms,
                published=published,
                extra_data={},
                text=text,
            )

        except Exception as e:
            LOGGER.error(
                f"[SourceSteam.scrape_metadata_from_response] Error parsing metadata: {e}")
            return None

    async def scrape_page(self, url: str, thumbnail_link: str):
        LOGGER.info(f"[SourceSteam.scrape_page] scraping: {url}")

        page = await self.browser.new_page(
            extra_http_headers=self.get_headers()
        )
        try:
            await page.goto(url,  wait_until="networkidle")
        except Exception as e:
            LOGGER.warn(f"Could not wait for networkidle for url: {url}")
            return []
        await sleep(0.5)

        # check if blocked by sensitive content
        age_gate = await page.query_selector("div.age_gate")
        if age_gate:
            # do gate and wait loading
            await sleep(0.5)
            await page.select_option("#ageYear", value="1995")
            await sleep(1)
            await page.click("#view_product_page_btn")
            await page.wait_for_load_state("networkidle")

        # try get new games from carouselle
        try:
            await page.wait_for_selector('[data-featuretarget="storeitems-carousel"]', timeout=15000)

            carousel = await page.query_selector('[data-featuretarget="storeitems-carousel"]')

            # get next games
            items = await carousel.query_selector_all('.ImpressionTrackedElement')
            games = []
            for item in items:
                # first anchor has page url
                link = await item.query_selector("a")
                new_url = None
                if link:
                    new_url = await link.get_attribute("href")

                # img has thumbnail
                img = await item.query_selector("img")
                img_src = None
                if img:
                    img_src = await img.get_attribute("src")

                if new_url and img_src:
                    games.append({
                        "url": new_url,
                        "image": img_src
                    })
        except Exception as _:
            LOGGER.warn(
                f"[SourceSteam.scrape_page] Could not find item carouselle for: {url}")
            html = await page.content()
            LOGGER.warn(f"[SourceSteam.scrape_page] {url} html: \n{html}")
            return games

        try:
            html = await page.content()
            selector = Selector(text=html)

            await page.close()
            metadata = self.scrape_metadata_from_response(selector)
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
                LOGGER.warn(
                    f"[SourceGamejolt.parse_game_page] Skipped game due to missing metadata: {url}")
        except Exception as e:
            LOGGER.warn(
                f"[SourceGamejolt.parse_game_page] Unable to get html parse to metadata: {url}, error: {e}")

        return games

    async def routine(self):
        page = await self.browser.new_page(
            extra_http_headers=self.get_headers()
        )
        try:
            await page.goto(self.BASE_URL,  wait_until="networkidle")

            items = await page.query_selector_all('#tab_topsellers_content .tab_content_items a')
        except Exception as e:
            LOGGER.error(f"Could not start routine: {e}")

        items_parsed = []
        for a in items:
            # find page link
            href = await a.get_attribute("href")

            # find thumbnail image
            img = await a.query_selector("img")
            img_src = None
            if img:
                img_src = await img.get_attribute("data-delayed-image") or await img.get_attribute("src")

            items_parsed.append({
                "url": href,
                "image": img_src
            })
        await page.close()

        # scrape each page
        games = items_parsed
        while (not self.ITERATIONS or self.ITERATIONS > 0) and len(games) > 0:
            new_games = []
            for game in games:
                new_games.extend(await self.scrape_page(game["url"], game["image"]))
                await sleep(2)

            if self.ITERATIONS:
                self.ITERATIONS -= 1
            games = new_games
            LOGGER.info(
                f"[SourceGamejolt.routine] found {len(new_games)} new games")

    async def scrape_documents(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            await self.routine()
            await self.browser.close()
