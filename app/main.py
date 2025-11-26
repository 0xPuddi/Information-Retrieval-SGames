from app.engine.bm25 import BM25
from app.engine.parser import Parser
from app.engine.indexer import Indexer

from flask import Flask, render_template, request

from utils.logger import LOGGER

# global initialization
LOGGER.info("Initializing app...")
# flask app
app = Flask(__name__,
            static_folder='public',
            template_folder='templates')

# parser
parser = Parser()

# indexer
indexer = Indexer(parser)

# BM25
bm25 = BM25(indexer)
LOGGER.info("App Initialized")


@app.route('/')
def index():
    return render_template('index.html', items=[])


@app.route('/query', methods=["POST"])
def query():
    body = request.get_json()

    if not isinstance(body["query"], str):
        return "Missing \"query\" field", 400

    items = bm25.query_sources_documents(
        body["query"], body["documents"] if ("documents" in body and isinstance(body["documents"], int)) else 10)
    return render_template('components/card.html', documents=[doc.model_dump() for doc in items])


# Starting routine
def main():
    LOGGER.info("Running app..")
    app.run(debug=False, port=3000)


if __name__ == '__main__':
    main()
