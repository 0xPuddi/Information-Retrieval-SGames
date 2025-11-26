# Information Retrieval: SGames Project

This is the repository for the SGames Project for the lecture Information
Retrieval. The project consists of a search engine for games. The project has
two main components: Scraper and Search Engine.

You need to first run the Scraper to collect data (scrape) from well known games
websites such as itchio, steam and gdeck. You can also add a website of your
choice to the scraped websites and add a scraping path to collect necessary
informations. Before running the app you should have some documents inside
`/collection`. You can then run the search engine, which will use the data
provided by the scraper to create and inverted index before starting the web
server, then it will start the server ans have ready all the necessary
components for querying, retrieve and give feedback about your search interests.

## Environment and uv

I use python and [uv](https://docs.astral.sh/uv/) as python package and project
manager so that you can also easily install all required packages and run the
app flawlessly.

If you have homebrew I suggest you to install uv:

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
browsers pages and load them with their Javascript to get the full html page
data. To do so after `uv sync` you will need to run:

```sh
uv run playwright install
```

Then run:

```sh
uv run scraper
```

## Search Engine (App)

To run the app run:

```sh
uv run app
```

## Libraries

Libraries used are:

-   [uv](https://docs.astral.sh/uv/)
-   [scrapy](https://docs.scrapy.org/en/latest/)
-   [parsel](https://parsel.readthedocs.io/en/latest/usage.html)
-   [httpx](https://www.python-httpx.org/)
-   [pydantic](https://docs.pydantic.dev/latest/)

## TODO

-   Add users questionnaires before and after feedback
-   Give artificial tassk to user that use your platform for you to evaluate
