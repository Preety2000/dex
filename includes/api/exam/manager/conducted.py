from includes.api.exam.index import Exam
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.db.connection import active_exam_db
from includes.db.models.db_exam import _ExamRecord, ExamDetails


async def get_id_exam_json(record: _ExamRecord):
    if not record:
        return None

    result_data = await IS_RESULTS.get_result(record, True)
    result = {
        "result_no": result_data[0][0],
        "exam_name": result_data[0][1],
        "category": result_data[0][2],
        "published": result_data[0][3],
        "result_year": result_data[0][4],
        "total_questions": result_data[1][0],
        "incorrect_count": result_data[1][1],
        "correct_count": result_data[1][2],
        "skipped_count": result_data[1][3],
        "attempt_questions": result_data[1][4],
        "paper": result_data[2],
        "total_marks": result_data[3][0],
        "total_obtained_marks": result_data[3][1],
        "percentage": result_data[3][2],
        "marks_in_word": result_data[3][3],
        "total_grade": result_data[3][4],
        "result": result_data[3][5],
        "sname": result_data[4][0],
        "roll_number": result_data[4][1],
        "registration_number": result_data[4][2],
        "image": result_data[4][3],
        "examinant": result_data[5][0],
        "instructor": result_data[5][1],
    }

    return result
