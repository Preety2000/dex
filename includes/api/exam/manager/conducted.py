from includes.api.exam.index import Exam
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.database.connection import config_exam_db
from includes.database.models.exam import _ExamRecord, ExamDetails


async def get_id_exam_json(record: _ExamRecord, request):
    if not record:
        return None

    is_result = IS_RESULTS(request)
    result_data = await is_result.get_result(record, True)
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
