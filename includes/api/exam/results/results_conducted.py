from dataclasses import dataclass

from num2words import num2words
from includes.db.models.utils import TimeStamp
from includes.core.globals.entry import app_context
from includes.db.connection import active_exam_db
from includes.db.models.db_exam import ExamDetails, ExamRecord, TeacherProfile
from includes.schemas.cache.member import MemberCache
from includes.utils.exm import (
    calculate_exam_score,
    convert_int_values,
    get_result_datals,
    result_not_public_message,
    result_public_message,
)
from includes.api.exam.results.utils import _question_stats


@dataclass
class Result:
    total_questions: int
    incorrect_count: int
    attempt_questions: int
    total_marks: float
    obtained_marks: float
    percentage: float
    grade: str
    result: str
    marks_in_word: str


def get_grade(obtained_marks, total_marks):
    percentage = (obtained_marks / total_marks) * 100 if total_marks else 0

    return next(
        (
            g
            for p, g in [
                (90, "A+"),
                (80, "A"),
                (70, "B+"),
                (60, "B"),
                (50, "C+"),
                (40, "C"),
                (30, "D"),
            ]
            if percentage >= p
        ),
        "F",
    )


def get_result_details(record, correct_answers):
    correct = 0
    skipped_count = 0
    for idx, item in enumerate(record.content):
        question_id, options, action = item
        correct_answer = correct_answers[question_id]
        try:
            action_index = int(action)
            if 0 <= action_index < len(options):
                selected_answer = options[action_index]
                if selected_answer == correct_answer:
                    correct += 1
        except (TypeError, ValueError):
            if action is False:
                skipped_count += 1
    total_questions = len(record.content)
    incorrect_count = total_questions - (correct + skipped_count)
    attempt_questions = total_questions - skipped_count
    total_marks, obtained_marks, percentage, grade, result = calculate_exam_score(
        total_questions, correct, incorrect_count
    )
    marks_in_word = num2words(obtained_marks, lang="en")

    return Result(
        total_questions=total_questions,
        incorrect_count=incorrect_count,
        attempt_questions=attempt_questions,
        total_marks=total_marks,
        obtained_marks=obtained_marks,
        percentage=percentage,
        grade=grade,
        result=result,
        marks_in_word=marks_in_word,
    )


def calculate_marks(all_q, marks_q, correct, ratio=None):

    wrong = all_q - correct
    if ratio and ":" in ratio:
        pos, neg = map(int, ratio.split(":"))
        neg_marks = wrong * marks_q * (neg / pos)
    else:
        neg_marks = 0
    return all_q * marks_q, (correct * marks_q) - neg_marks


class IS_RESULTS:
    def __init__(self):
        self.request = app_context.request
        self.function = app_context.function

    async def get(self, key):
        db = await active_exam_db()

        record = db.query(ExamRecord).filter_by(key=key).first()
        if record:
            db.expunge(record)
            return record
        return

    @staticmethod
    async def get_result(record, by_pass: bool = None, is_verfy: bool = None):
        db = await active_exam_db()
        controller_query = (
            db.query(ExamDetails).filter(ExamDetails.id == record.exam_id).first()
        )

        if not controller_query:
            return None

        if is_verfy is True:
            id = await app_context.setting.member("id")
            if controller_query.teacher_id != id:
                return None

        current_time = TimeStamp.now_timestamp()
        if by_pass is None and (
            current_time < (controller_query.publish_timestamp or (current_time + 50))
        ):
            return {"__ac": [302, result_public_message(record.submitted_on)]}

        controller_info = (
            db.query(TeacherProfile)
            .filter(TeacherProfile.id == controller_query.teacher_id)
            .first()
        )

        q = await get_result_datals(controller_query, record)

        student = await MemberCache.getrollnumber(record.roll_no)
        q.append([student.get(i) for i in ["name", "roll_no", "reg_no", "img"]])
        q.append(
            [controller_info.name, (controller_info.signature or "/static/logo1x1.png")]
        )
        return q

    @staticmethod
    async def get_ans_seet(record):
        db = await active_exam_db()

        controller_query = (
            db.query(ExamDetails).filter(ExamDetails.id == record.exam_id).first()
        )

        if not controller_query:
            return None, None, None

        correct_map = {
            q["id"]: [q["title"], q["correct_answer"], q.get("subject", None)]
            for ques in controller_query.questions.values()
            for q in ques
        }

        lists = []
        index = 0
        details = convert_int_values(controller_query.details)
        for k, responses in record.content.items():
            inf = details.get(k)
            t, a, s, c, i, l = await _question_stats(correct_map, responses)
            tm, om, p, g, r = calculate_exam_score(t, c, i)

            lists.append([f"{inf[1]} ~ {inf[2]}", l])
            index = index + 1

        info = await MemberCache.getrollnumber(record.roll_no)

        return f"NS{record.id:04}", lists, info

    async def index(self, key):
        record = await self.get(key)
        if not record:
            return None

        if record.is_submitted != True:
            return {"__ac": [302, result_not_public_message()]}

        data = await IS_RESULTS.get_result(record)
        if isinstance(data, list):
            return {"__ac": [301, data]}

        return data
