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
    raw_task_flappy_bird = request.args.get('task_flappy_bird')
    task_flappy_bird: bool | None = raw_task_flappy_bird.lower(
    ) == "true" if raw_task_flappy_bird is not None else None

    raw_task_albion_online = request.args.get('task_albion_online')
    task_albion_online: bool | None = raw_task_albion_online.lower(
    ) == "true" if raw_task_albion_online is not None else None

    raw_task_organized_theft = request.args.get('task_organized_theft')
    task_organized_theft: bool | None = raw_task_organized_theft.lower(
    ) == "true" if raw_task_organized_theft is not None else None

    raw_task_elden_ring = request.args.get('task_elden_ring')
    task_elden_ring: bool | None = raw_task_elden_ring.lower(
    ) == "true" if raw_task_elden_ring is not None else None

    questions = [
        {
            'id': 'task_flappy_bird',
            'name': 'Flappy Bird',
                    'success': task_flappy_bird
        },
        {
            'id': 'task_albion_online',
            'name': 'Albion Online',
                    'success': task_albion_online
        },
        {
            'id': 'task_organized_theft',
            'name': 'The Very Organized Theft',
                    'success': task_organized_theft
        },
        {
            'id': 'task_elden_ring',
            'name': 'Elden Ring',
            'success': task_elden_ring},
        {
            'id': 'task_free_search',
            'name': 'Free Search',
            'success': None
        },
    ]
    LOGGER.info(f"{questions}")
    return render_template('feedback.html',
                           questions=questions
                           )


@app.route('/feedback/analytics', methods=["GET"])
def get_feedbacks():
    items: list[UserFeedback] = session.get_all_feedbacks()

    # ue
    ue_questions = [
        ('Annoying', 'Enjoyable'),
        ('Not Understandable', 'Understandable'),
        ('Easy To Learn', 'Difficult To Learn'),
        ('Unpredictable', 'Predictable'),
        ('Unpleasant', 'Pleasant'),
        ('Clear', 'Confusing'),
        ('Organized', 'Cluttered'),
        ('Friendly', 'Unfriendly')
    ]
    avg_ue_scores = session.compute_avg_eq_scores(items)

    # sus
    sus_questions = [
        "I think I would like to use this tool frequently.",
        "I found the tool unnecessarily complex.",
        "I thought the tool was easy to use.",
        "I think that I would need the support of a technical person to be able to use this system.",
        "I found the various functions in this tool worked well together.",
        "I thought there was too much inconsistency in this tool.",
        "I would imagine that most people would learn to use this tool very quickly.",
        "I found the tool very difficult to use.",
        "I felt very confident using the tool",
        "I needed to learn a lot of things before I could get going with this tool",
    ]
    avg_sus_scores = session.compute_avg_sus_scores(items)
    avg_sus_score = 0
    for i in items:
        avg_sus_score += session.compute_sus_score(i)
    avg_sus_score = avg_sus_score / len(items)

    # usability
    usability_test_questions = [
        "What's your favorite thing about this site?"
        "What's your least favorite thing about this site?",
        "Do you have any recommendation for changes to the way this site looks or works?"
    ]
    favorite_thing_responses = [
        item.favorite_thing_about_site for item in items]
    least_favorite_thing_responses = [
        item.least_favorite_thing_about_site for item in items]
    recommendation_responses = [
        item.recommendations_for_changes for item in items]

    likely_to_suggest_question = "How likely are you to recommend this website to others?"
    avg_likely_to_suggest = session.compute_avg_likely_to_suggest(items)

    # tasks
    tasks = [
        'Flappy Bird',
        'Albion Online',
        'The Very Organized Theft',
        'Elden Ring',
        'Free Search',
    ]
    avg_successes = session.compute_avg_successes(items)
    tasks_completions = [
        [item.task_flappy_bird_completed for item in items],
        [item.task_albion_online_completed for item in items],
        [item.task_organized_theft_completed for item in items],
        [item.task_elden_ring_completed for item in items],
        [item.task_free_search_completed for item in items]
    ]
    tasks_observations = [
        [item.task_flappy_bird_observations for item in items],
        [item.task_albion_online_observations for item in items],
        [item.task_organized_theft_observations for item in items],
        [item.task_elden_ring_observations for item in items],
        [item.task_free_search_observations for item in items]
    ]

    return render_template('statistics.html',
                           users_feedbacks=items,  # necessary?
                           #
                           ue_questions=ue_questions,
                           avg_ue_scores=avg_ue_scores,
                           #
                           sus_questions=sus_questions,
                           avg_sus_scores=avg_sus_scores,
                           avg_sus_score=avg_sus_score,
                           #
                           usability_test_questions=usability_test_questions,
                           favorite_thing_responses=favorite_thing_responses,
                           least_favorite_thing_responses=least_favorite_thing_responses,
                           recommendation_responses=recommendation_responses,
                           likely_to_suggest_question=likely_to_suggest_question,
                           avg_likely_to_suggest=avg_likely_to_suggest,
                           #
                           tasks=tasks,
                           avg_successes=avg_successes,
                           tasks_completions=tasks_completions,
                           tasks_observations=tasks_observations
                           )


# Starting routine
def main():
    LOGGER.info("Running app..")
    app.run(debug=False, port=3000)


if __name__ == '__main__':
    main()
