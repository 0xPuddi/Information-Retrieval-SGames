
from pathlib import Path
from typing import List, Optional

import duckdb
from pydantic import BaseModel, Field

from utils.logger import LOGGER


class UserFeedback(BaseModel):
    # UEQ
    annoying_vs_enjoyable: Optional[int] = Field(None, ge=1, le=7)
    not_understandable_vs_understandable: Optional[int] = Field(
        None, ge=1, le=7)
    unpleasant_vs_pleasant: Optional[int] = Field(None, ge=1, le=7)
    friendly_vs_unfriendly: Optional[int] = Field(None, ge=-1, le=7)
    clear_vs_confusing: Optional[int] = Field(None, ge=1, le=7)

    # SUS
    use_frequently_question: Optional[int] = Field(None, ge=1, le=5)
    unnecessary_complexity_question: Optional[int] = Field(None, ge=1, le=5)
    most_people_learn_quickly_question: Optional[int] = Field(None, ge=1, le=5)
    felt_confident_question: Optional[int] = Field(None, ge=1, le=5)
    how_likely_to_recommend_question: Optional[int] = Field(None, ge=0, le=10)

    # usability testing
    favorite_thing_about_site: Optional[str] = None
    least_favorite_thing_about_site: Optional[str] = None
    recommendations_for_changes: Optional[str] = None

    task_flappy_bird_completed: Optional[bool] = None
    task_flappy_bird_observations: Optional[str] = None
    task_free_search_completed: Optional[bool] = None
    task_free_search_observations: Optional[str] = None


class Session():
    DATABASE_PATH: str = "app/engine/db/session.duckdb"

    def __init__(self):
        # connect to db
        db_path = Path(self.DATABASE_PATH)
        # make folder if missing
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = duckdb.connect(db_path)

        LOGGER.info("Initializing session...")

        self.warm_db()

        LOGGER.ok("Session initialized")

    def warm_db(self):
        try:
            self.connection.execute("CREATE SEQUENCE seq_feedback START 1")
        except Exception as _:
            pass
        self.connection.execute("""
CREATE TABLE IF NOT EXISTS user_feedback (
feedback_id INTEGER PRIMARY KEY DEFAULT nextval('seq_feedback'),

-- UEQ
annoying_vs_enjoyable SMALLINT,
not_understandable_vs_understandable SMALLINT,
unpleasant_vs_pleasant SMALLINT,
friendly_vs_unfriendly SMALLINT,
clear_vs_confusing SMALLINT,

-- SUS
use_frequently_question SMALLINT,
unnecessary_complexity_question SMALLINT,
most_people_learn_quickly_question SMALLINT,
felt_confident_question SMALLINT,
how_likely_to_recommend_question SMALLINT,

-- usability testing
favorite_thing_about_site TEXT,
least_favorite_thing_about_site TEXT,
recommendations_for_changes TEXT,
task_flappy_bird_completed BOOLEAN,
task_flappy_bird_observations TEXT,
task_free_search_completed BOOLEAN,
task_free_search_observations TEXT
);
""")

    def store_user_feedback(self, feedback: UserFeedback):
        """
        Saves a feedback
        """
        if not feedback:
            return
        self.connection.execute(
            """
			INSERT INTO user_feedback (
				annoying_vs_enjoyable,
				not_understandable_vs_understandable,
				unpleasant_vs_pleasant,
				friendly_vs_unfriendly,
				clear_vs_confusing,
				use_frequently_question,
				unnecessary_complexity_question,
				most_people_learn_quickly_question,
				felt_confident_question,
				how_likely_to_recommend_question,
				favorite_thing_about_site,
				least_favorite_thing_about_site,
				recommendations_for_changes,
				task_flappy_bird_completed,
				task_flappy_bird_observations,
				task_free_search_completed,
				task_free_search_observations
			) VALUES (
				$annoying_vs_enjoyable,
				$not_understandable_vs_understandable,
				$unpleasant_vs_pleasant,
				$friendly_vs_unfriendly,
				$clear_vs_confusing,
				$use_frequently_question,
				$unnecessary_complexity_question,
				$most_people_learn_quickly_question,
				$felt_confident_question,
				$how_likely_to_recommend_question,
				$favorite_thing_about_site,
				$least_favorite_thing_about_site,
				$recommendations_for_changes,
				$task_flappy_bird_completed,
				$task_flappy_bird_observations,
				$task_free_search_completed,
				$task_free_search_observations
			)
			""",
            feedback.model_dump(exclude={"feedback_id"})
        )

    def get_all_feedbacks(self) -> List[UserFeedback]:
        """
        Returns all feedbacks
        """
        rows = self.connection.execute("""
SELECT *
FROM user_feedback
""").fetchall()
        return [UserFeedback(**row) for row in rows]
