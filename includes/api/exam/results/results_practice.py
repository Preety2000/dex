from num2words import num2words
from sqlalchemy import func, literal_column
from includes.utils._sub import get_code_to_subject
from includes.api.exam.student import RecordType, Student
from includes.core.config import exam_database
from includes.core.globals.entry import app_context
from includes.db.models.db_exam import _ExamRecord, PracticeExamRecord
from includes.db.models.secondary import QuizQuestion, QuizRelationships, Terms
from includes.schemas.cache.member import MemberCache
from includes.utils.exm import (
    calculate_exam_score,
    calculate_result,
    get_timestamp_and_year,
    result_not_public_message,
)
from includes.api.exam.results.utils import _question_stats
from includes.schemas.cache.mcq_question import QuizQuestionCache


async def question_stats(answer_key, responses):
    total = len(responses)
    correct = attempted = skipped = 0
    for qid, options, choice in responses:
        try:
            idx = int(choice)
            if 0 <= idx < len(options):
                if isinstance(choice, bool):
                    skipped += 1
                elif options[idx] == answer_key.get(qid):
                    attempted += 1
                    correct += 1
                else:
                    attempted += 1

        except (TypeError, ValueError):
            if choice is False:
                attempted += 1
            elif choice is None:
                skipped += 1

    incorrect = total - (correct + skipped)

    return (total, attempted, skipped, correct, incorrect)


class SELF_RESULTS:
    def __init__(self):
        self.request = app_context.request
        self.function = app_context.function

    @staticmethod
    async def _result_info(record: _ExamRecord):
        # Get all question IDs
        q_ids = [q[0] for v in record.content.values() for q in v]

        # print(await QuizQuestionCache.get_many(q_ids))
        # return {}
        # Map correct answers
        correct_map = {
            q["id"]: q["correct_answer"]
            for q in await QuizQuestionCache.get_many(q_ids)
        }

        papers = []
        totals = {
            "total": 0,
            "attempted": 0,
            "skipped": 0,
            "correct": 0,
            "incorrect": 0,
            "marks": 0,
            "obtained": 0,
        }

        name_code = await get_code_to_subject()
        for name, responses in record.content.items():
            t, a, s, c, i = await question_stats(correct_map, responses)
            tm, om, p, g, r = calculate_exam_score(t, c, i)

            papers.append(
                {
                    "subject": name_code.get(name),
                    "questions": {
                        "total": t,
                        "attempted": a,
                        "skipped": s,
                        "correct": c,
                        "incorrect": i,
                    },
                    "result": {
                        "total_marks": tm,
                        "obtained_marks": om,
                        "percentage": p,
                        "marks_in_words": num2words(om, lang="en"),
                        "grade": g,
                        "result": r,
                    },
                }
            )

            totals["total"] += t
            totals["attempted"] += a
            totals["skipped"] += s
            totals["correct"] += c
            totals["incorrect"] += i
            totals["marks"] += tm
            totals["obtained"] += om

        percentage, grade, result = calculate_result(
            totals["marks"], totals["obtained"]
        )

        info = record.ts_info.get("info")
        published, year = get_timestamp_and_year(record.submitted_on)

        return {
            "exam": {
                "id": f"NS{record.id:04}",
                "name": "Self Online Test Series",
                "subject": info[1],
                "category": info[2],
                "nim_que": info[3],
                "published": published,
                "year": year,
            },
            "summary": {
                "total_marks": totals["marks"],
                "obtained_marks": totals["obtained"],
                "percentage": percentage,
                "total_questions": totals["total"],
                "total_time": info[0],
                "correct": totals["correct"],
                "incorrect": totals["incorrect"],
                "attempted": totals["attempted"],
                "skipped": totals["skipped"],
                "grade": grade,
                "result": result,
            },
            "papers": papers,
        }

    @staticmethod
    async def get_exam_result(record: _ExamRecord):
        # Get all question IDs
        q_ids = [q[0] for v in record.content.values() for q in v]

        # Map correct answers
        correct_map = {
            q.id: q.correct_answer
            for q in app_context.db.query(QuizQuestion).filter(
                QuizQuestion.id.in_(q_ids)
            )
        }

        papers = []
        totals = dict(
            total=0, attempted=0, skipped=0, correct=0, incorrect=0, marks=0, obtained=0
        )

        name_code = await get_code_to_subject()
        for name, responses in record.content.items():
            t, a, s, c, i = await question_stats(correct_map, responses)
            tm, om, p, g, r = calculate_exam_score(t, c, i)

            papers.append(
                [
                    name_code.get(name),
                    [t, a, s, c, i],
                    [tm, om, p, num2words(om, lang="en"), g, r],
                ]
            )

            totals["total"] += t
            totals["attempted"] += a
            totals["skipped"] += s
            totals["correct"] += c
            totals["incorrect"] += i
            totals["marks"] += tm
            totals["obtained"] += om

        perc, grade, result = calculate_result(totals["marks"], totals["obtained"])

        ismeta = record.ts_info.get("info")
        published, year = get_timestamp_and_year(record.submitted_on)

        print(totals)
        student = await MemberCache.getrollnumber(record.roll_no)

        return [
            [f"NS{record.id:04}", "Self", ismeta[2], published, year],
            [
                totals["total"],
                totals["incorrect"],
                totals["correct"],
                totals["skipped"],
                totals["attempted"],
            ],
            papers,
            [
                totals["marks"],
                totals["obtained"],
                perc,
                num2words(totals["obtained"], lang="en"),
                grade,
                result,
            ],
            [student.get(i) for i in ["name", "roll_no", "reg_no", "img"]],
            [None, "/static/logo1x1.png"],
        ]

    @staticmethod
    async def get_ans_seet(record):

        # Get all question IDs
        q_ids = [q[0] for v in record.content.values() for q in v]

        # Map correct answers
        correct_map = {
            q.id: [q.question, q.correct_answer, q.subject_id]
            for q in app_context.db.query(QuizQuestion).filter(
                QuizQuestion.id.in_(q_ids)
            )
        }

        lists = []
        papers = []
        totals = dict(
            total=0, attempted=0, skipped=0, correct=0, incorrect=0, marks=0, obtained=0
        )

        name_code = await get_code_to_subject()
        for name, responses in record.content.items():
            t, a, s, c, i, l = await _question_stats(correct_map, responses)
            tm, om, p, g, r = calculate_exam_score(t, c, i)
            lists.append([name_code.get(name), l])

        info = await MemberCache.getrollnumber(record.roll_no)
        return f"NS{record.id:04}", lists, info

    async def index(self, key):
        record = await Student.get_by_exam_key(key, RecordType.STUDENT)
        if not record:
            return None

        if record.is_submitted != True:
            return {"__ac": [302, result_not_public_message()]}

        data = await SELF_RESULTS.get_exam_result(record)
        info = await MemberCache.getrollnumber(record.roll_no)

        student = [info.get(i) for i in ["name", "roll_no", "reg_no", "img"]]
        data.append(student)
        data.append([None, "/static/logo1x1.png"])

        return {"__ac": [301, data]}
