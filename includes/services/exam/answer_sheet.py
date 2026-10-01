from includes.api.exam.student import RecordType, Student
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.api.exam.results.results_practice import SELF_RESULTS
from includes.core.globals.entry import app_context
from includes.utils.exm import result_not_public_message


class AnsSeet:
    # async def index(self, option_keys, keys_private, params):
    @staticmethod
    async def index():

        source, code, cls = (
            (app_context.route.resource_slug, RecordType.STUDENT, SELF_RESULTS)
            if (app_context.route.resource_type and app_context.route.resource_slug)
            else (app_context.route.resource_type, RecordType.INVIGILATOR, IS_RESULTS)
        )
        record = await Student.get_by_exam_key(source, code)
        if record:
            if record.is_submitted != True:
                app_context.response.update(result_not_public_message())
                return "widget/answer_sheet"

            result_no, lists, student = await cls.get_ans_seet(record)

            return "widget/answer_sheet", {
                "lists": lists,
                "result_no": result_no,
                "sname": student.get("name"),
            }

        return "error", {}
