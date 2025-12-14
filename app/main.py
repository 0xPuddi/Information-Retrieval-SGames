from pydantic import ValidationError
from app.engine.bm25 import BM25
from app.engine.parser import Parser
from app.engine.indexer import Indexer

from flask import Flask, render_template, request

from app.engine.session import Session, UserFeedback
from collection.models.document import Document
from utils.logger import LOGGER

# global initialization
LOGGER.info("Initializing app...")
# flask app
app = Flask(__name__,
            static_folder='public',
            template_folder='templates')

# session
session = Session()

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

    LOGGER.info(f"body: {body}")

    n = body["documents"] if (
        "documents" in body and isinstance(body["documents"], int)) else 30
    platform = body["platform"] if (
        "platform" in body and isinstance(body["platform"], str)) else None
    category = body["category"] if (
        "category" in body and isinstance(body["category"], str)) else None
    status = body["status"] if (
        "status" in body and isinstance(body["status"], str)) else None
    tags = body["tags"] if (
        "tags" in body and isinstance(body["tags"], list)) else []

    items = bm25.query_sources_documents(
        parser.parse_text_to_words(body["query"]),
        n,
        platform,
        category,
        status,
        tags
    )
    return [doc.model_dump() for doc in items], 200


@app.route('/render/documents', methods=["POST"])
def render_documents():
    body = request.get_json()

    if not isinstance(body["documents"], list):
        return "Missing \"documents\" field", 400

        # parse documents
    items = []
    try:
        for d in body["documents"]:
            items.append(Document(**d))
    except ValidationError as e:
        return {"Wrong object field": e.errors()}, 400
    except Exception as e:
        LOGGER.warn(f"Unexpected error: {e}")
        return "Failed to parse documents", 400

    # we then render
    return render_template('components/card.html', documents=[doc.model_dump() for doc in items])


@app.route('/document', methods=["GET"])
def document():
    # ?id="itch"
    id = request.args.get('id')
    # ?collection="itch"
    collection = request.args.get('collection')

    if not id and not collection:
        return "Missing \"id\" or \"collection\" query parameter", 400

    # get doc
    document: Document = indexer.get_document_by_id_and_collection_name(
        id, collection)

    # render
    return render_template('document.html', d=document)


@app.route('/feedback', methods=["POST"])
def post_feedback():
    body = request.get_json()

    if not isinstance(body["feedback"], dict):
        return "Missing \"feedback\" object", 400

    try:
        feedback: UserFeedback = UserFeedback(**body["feedback"])
    except ValidationError as e:
        return {"Wrong object field": e.errors()}, 400
    except Exception as e:
        LOGGER.warn(f"Unexpected error: {e}")
        return "Failed to parse object", 400

    session.store_user_feedback(feedback)
    return "feedback saved", 200


@app.route('/feedback', methods=["GET"])
def feedback():
    return render_template('feedback.html')


@app.route('/feedback/all', methods=["GET"])
def get_feedbacks():
    # how to display data? use js or templates
    items = session.get_all_feedbacks()
    return items, 200


# Starting routine
def main():
    LOGGER.info("Running app..")
    app.run(debug=False, port=3000)


if __name__ == '__main__':
    main()
