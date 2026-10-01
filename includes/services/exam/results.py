import json
import ast
from datetime import date, datetime

from includes.api.exam.student import RecordType, Student
from includes.core.globals.entry import app_context
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.api.exam.results.results_practice import SELF_RESULTS


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
        return super(CustomJSONEncoder, self).default(obj)


class Results:

    @staticmethod
    async def index():
        source, code = (
            (app_context.route.resource_slug, RecordType.STUDENT)
            if (app_context.route.resource_type and app_context.route.resource_slug)
            else (app_context.route.resource_type, RecordType.INVIGILATOR)
        )

        record = await Student.get_by_exam_key(source, code)
        app_context.response["record"] = record
        return "widget/results_index"
