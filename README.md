# Information Retrieval: SGames Project

This is the repository for the SGames Project for the lecture Information
Retrieval. The project consists of a search engine for games, which has two main
components: Scraper and Search Engine.

You need to first run the Scraper to collect data (scrape) from well known games
websites such as itchio, steam and gamejolt. You can also add a website of your
choice to the scraped websites and add a scraping path to collect necessary
informations. Before running the web app you should have some documents inside
`/collection`. Once you collected some data you can run the search engine, which
will use the collection provided by scrapers to create an inverted index, then
it will start the server and have ready all the necessary components for
querying and retrieve documents within the collection.

## Report

Here you can find the technical guide and how to run the app.

For a more in depth analysis of the achitecture, decision process and results
compile the Latex report found in `./report` using make tex then open
`report.pdf`.

## Environment and uv

I use python and [uv](https://docs.astral.sh/uv/) as python package and project
manager so that you can also easily install all required packages and run the
app flawlessly.

If you have homebrew I suggest you to install uv with:

```sh
brew install uv
```

otherwise follow uv's
[official documentation to install it](https://docs.astral.sh/uv/getting-started/installation/).
Once installed run:

```sh
uv sync
```

and it will automatically download and set up your environment. You are good to
go!

## Scraper

To use the scraper I require you to have playwright as we are going to open
browser pages to collect cookies which are necessary to get access to the html
page data. To do so after `uv sync` you will need to run:

```sh
uv run playwright install
```

Then you can start scrapers by running:

```sh
make scrapers
```

To stop scrapers from running, in the same terminal you runned them you can type
`q + ENTER`.

## Search Engine (App)

Once you collected enough data you can run the application. To run it use:

```sh
make
```

The first time you will run it it will take some more time to build the inverted
index. Once built you can find the app at `3000`, and if you will run it again
without modifying any collection file (any `*.json` in `/collection`) the app
will not rebuild the index and it will be immediately ready.

## Libraries

Libraries used are:

Environment

-   [uv](https://docs.astral.sh/uv/)
-   [python-dotenv](https://pypi.org/project/python-dotenv/)

Scraper

-   [scrapy](https://docs.scrapy.org/en/latest/)
-   [parsel](https://parsel.readthedocs.io/en/latest/usage.html)
-   [httpx](https://www.python-httpx.org/)
-   [playwright](https://playwright.dev/python/)
-   [playwright-stealth](https://pypi.org/project/playwright-stealth/)

Models

-   [pydantic](https://docs.pydantic.dev/latest/)

Search Engine

-   [flask](https://flask.palletsprojects.com/en/stable/)
-   [duckdb](https://duckdb.org/)
-   [tailwind](https://tailwindcss.com/)
-   [nltk](https://www.nltk.org/)
