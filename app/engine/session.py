
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
    easy_to_learn_vs_difficult_to_learn: Optional[int] = Field(
        None, ge=1, le=7)
    unpredictable_vs_predictable: Optional[int] = Field(None, ge=1, le=7)
    unpleasant_vs_pleasant: Optional[int] = Field(None, ge=1, le=7)
    clear_vs_confusing: Optional[int] = Field(None, ge=1, le=7)
    organized_vs_cluttered: Optional[int] = Field(None, ge=1, le=7)
    friendly_vs_unfriendly: Optional[int] = Field(None, ge=-1, le=7)

    # SUS
    use_frequently_question: Optional[int] = Field(None, ge=1, le=5)
    unnecessary_complexity_question: Optional[int] = Field(None, ge=1, le=5)
    easy_to_use_question: Optional[int] = Field(None, ge=1, le=5)
    technical_support_question: Optional[int] = Field(None, ge=1, le=5)
    functions_worked_well_question: Optional[int] = Field(None, ge=1, le=5)
    inconsitency_in_tool_question: Optional[int] = Field(None, ge=1, le=5)
    most_people_learn_quickly_question: Optional[int] = Field(None, ge=1, le=5)
    difficult_to_use_question: Optional[int] = Field(None, ge=1, le=5)
    felt_confident_question: Optional[int] = Field(None, ge=1, le=5)
    need_to_learn_a_lot_question: Optional[int] = Field(None, ge=1, le=5)
    how_likely_to_recommend_question: Optional[int] = Field(None, ge=0, le=10)

    # usability testing
    favorite_thing_about_site: Optional[str] = None
    least_favorite_thing_about_site: Optional[str] = None
    recommendations_for_changes: Optional[str] = None

    task_flappy_bird_completed: Optional[bool] = None
    task_flappy_bird_observations: Optional[str] = None

    task_albion_online_completed: Optional[bool] = None
    task_albion_online_observations: Optional[str] = None

    task_organized_theft_completed: Optional[bool] = None
    task_organized_theft_observations: Optional[str] = None

    task_elden_ring_completed: Optional[bool] = None
    task_elden_ring_observations: Optional[str] = None

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
easy_to_learn_vs_difficult_to_learn SMALLINT,
unpredictable_vs_predictable SMALLINT,
unpleasant_vs_pleasant SMALLINT,
clear_vs_confusing SMALLINT,
organized_vs_cluttered SMALLINT,
friendly_vs_unfriendly SMALLINT,

-- SUS
use_frequently_question SMALLINT,
unnecessary_complexity_question SMALLINT,
easy_to_use_question SMALLINT,
technical_support_question SMALLINT,
functions_worked_well_question SMALLINT,
inconsitency_in_tool_question SMALLINT,
most_people_learn_quickly_question SMALLINT,
difficult_to_use_question SMALLINT,
felt_confident_question SMALLINT,
need_to_learn_a_lot_question SMALLINT,

how_likely_to_recommend_question SMALLINT,

-- usability testing
favorite_thing_about_site TEXT,
least_favorite_thing_about_site TEXT,
recommendations_for_changes TEXT,

task_flappy_bird_completed BOOLEAN,
task_flappy_bird_observations TEXT,

task_albion_online_completed BOOLEAN,
task_albion_online_observations TEXT,

task_organized_theft_completed BOOLEAN,
task_organized_theft_observations TEXT,

task_elden_ring_completed BOOLEAN,
task_elden_ring_observations TEXT,

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
				easy_to_learn_vs_difficult_to_learn,
				unpredictable_vs_predictable,
				unpleasant_vs_pleasant,
				clear_vs_confusing,
				organized_vs_cluttered,
				friendly_vs_unfriendly,

				use_frequently_question,
				unnecessary_complexity_question,
				easy_to_use_question,
				technical_support_question,
				functions_worked_well_question,
				inconsitency_in_tool_question,
				most_people_learn_quickly_question,
				difficult_to_use_question,
				felt_confident_question,
				need_to_learn_a_lot_question,

				how_likely_to_recommend_question,

				favorite_thing_about_site,
				least_favorite_thing_about_site,
				recommendations_for_changes,

				task_flappy_bird_completed,
				task_flappy_bird_observations,

				task_albion_online_completed,
				task_albion_online_observations,

				task_organized_theft_completed,
				task_organized_theft_observations,

				task_elden_ring_completed,
				task_elden_ring_observations,

				task_free_search_completed,
				task_free_search_observations
			) VALUES (
				$annoying_vs_enjoyable,
				$not_understandable_vs_understandable,
				$easy_to_learn_vs_difficult_to_learn,
				$unpredictable_vs_predictable,
				$unpleasant_vs_pleasant,
				$clear_vs_confusing,
				$organized_vs_cluttered,
				$friendly_vs_unfriendly,

				$use_frequently_question,
				$unnecessary_complexity_question,
				$easy_to_use_question,
				$technical_support_question,
				$functions_worked_well_question,
				$inconsitency_in_tool_question,
				$most_people_learn_quickly_question,
				$difficult_to_use_question,
				$felt_confident_question,
				$need_to_learn_a_lot_question,

				$how_likely_to_recommend_question,

				$favorite_thing_about_site,
				$least_favorite_thing_about_site,
				$recommendations_for_changes,

				$task_flappy_bird_completed,
				$task_flappy_bird_observations,

				$task_albion_online_completed,
				$task_albion_online_observations,

				$task_organized_theft_completed,
				$task_organized_theft_observations,

				$task_elden_ring_completed,
				$task_elden_ring_observations,

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
        result = self.connection.execute("SELECT * FROM user_feedback")
        columns = [desc[0] for desc in result.description]
        return [UserFeedback(**dict(zip(columns, row))) for row in result.fetchall()]

    def compute_sus_score(self, user_feedback: UserFeedback) -> float:
        scores = [
            user_feedback.use_frequently_question,
            user_feedback.unnecessary_complexity_question,
            user_feedback.easy_to_use_question,
            user_feedback.technical_support_question,
            user_feedback.functions_worked_well_question,
            user_feedback.inconsitency_in_tool_question,
            user_feedback.most_people_learn_quickly_question,
            user_feedback.difficult_to_use_question,
            user_feedback.felt_confident_question,
            user_feedback.need_to_learn_a_lot_question,
        ]
        sus_score = 0

        for i in range(len(scores)):
            if i % 2 == 0:
                sus_score += scores[i] - 1
            else:
                sus_score += 5 - scores[i]

        sus_score *= 2.5
        return sus_score

    def compute_avg_eq_scores(self, items: list[UserFeedback]):
        scores = [
            [
                item.annoying_vs_enjoyable,
                item.not_understandable_vs_understandable,
                item.easy_to_learn_vs_difficult_to_learn,
                item.unpredictable_vs_predictable,
                item.unpleasant_vs_pleasant,
                item.clear_vs_confusing,
                item.organized_vs_cluttered,
                item.friendly_vs_unfriendly
            ] for item in items
        ]

        # reduce
        for i in range(len(items) - 1, 0, -1):
            scores[0][0] += scores[i][0]
            scores[0][1] += scores[i][1]
            scores[0][2] += scores[i][2]
            scores[0][3] += scores[i][3]
            scores[0][4] += scores[i][4]
            scores[0][5] += scores[i][5]
            scores[0][6] += scores[i][6]
            scores[0][7] += scores[i][7]

        # divide
        return [
            scores[0][0] / len(items),
            scores[0][1] / len(items),
            scores[0][2] / len(items),
            scores[0][3] / len(items),
            scores[0][4] / len(items),
            scores[0][5] / len(items),
            scores[0][6] / len(items),
            scores[0][7] / len(items),
        ]

    def compute_avg_sus_scores(self, items: list[UserFeedback]):
        scores = [
            [item.use_frequently_question,
             item.unnecessary_complexity_question,
             item.easy_to_use_question,
             item.technical_support_question,
             item.functions_worked_well_question,
             item.inconsitency_in_tool_question,
             item.most_people_learn_quickly_question,
             item.difficult_to_use_question,
             item.felt_confident_question,
             item.need_to_learn_a_lot_question] for item in items
        ]

        # reduce
        for i in range(len(items) - 1, 0, -1):
            scores[0][0] += scores[i][0]
            scores[0][1] += scores[i][1]
            scores[0][2] += scores[i][2]
            scores[0][3] += scores[i][3]
            scores[0][4] += scores[i][4]
            scores[0][5] += scores[i][5]
            scores[0][6] += scores[i][6]
            scores[0][7] += scores[i][7]
            scores[0][8] += scores[i][8]
            scores[0][9] += scores[i][9]

        # divide
        return [
            scores[0][0] / len(items),
            scores[0][1] / len(items),
            scores[0][2] / len(items),
            scores[0][3] / len(items),
            scores[0][4] / len(items),
            scores[0][5] / len(items),
            scores[0][6] / len(items),
            scores[0][7] / len(items),
            scores[0][8] / len(items),
            scores[0][9] / len(items)
        ]

    def compute_avg_likely_to_suggest(self, items: list[UserFeedback]):
        likely_to_suggest = 0

        for i in range(len(items)):
            likely_to_suggest += items[i].how_likely_to_recommend_question

        return likely_to_suggest / len(items)

    def compute_avg_successes(self, items: list[UserFeedback]):
        successes = [
            0, 0, 0, 0, 0
        ]

        for i in range(len(items)):
            if items[i].task_flappy_bird_completed:
                successes[0] += 1
            if items[i].task_albion_online_completed:
                successes[1] += 1
            if items[i].task_organized_theft_completed:
                successes[2] += 1
            if items[i].task_elden_ring_observations:
                successes[3] += 1
            if items[i].task_free_search_completed:
                successes[4] += 1

        return [avg_successes / len(items) for avg_successes in successes]
