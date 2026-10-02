from datetime import datetime
import time
from typing import Union
from fastapi import Request
from num2words import num2words
from collections import Counter, defaultdict

from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import encode_id
from includes.core.security import _Security
from includes.db.dataclass import ExamRqStatus

ES = {}


def get_folder_key(id: int):
    return f"{encode_id(50)}{_Security.short_encode(id)}"


def get_exam_id(exam_id: Union[str, int]) -> int:
    """
    Normalize exam_id into integer form.
    Accepts either an int or an encoded string.
    """
    if isinstance(exam_id, int):
        return exam_id

    try:
        if isinstance(exam_id, str):
            decoded = _Security.short_decode(exam_id)
            return int(decoded)

    except (ValueError, TypeError) as e:
        print(f"Invalid exam_id format: {exam_id}")

    print(f"\033[91m{exam_id}\033[0m")

    return exam_id


def get_session_key_and_exam_key(request: Request):
    custom_id = request.cookies.get("_exmeg")
    try:
        first, rest = custom_id.split("-", 1)
        middle, last = rest.rsplit("-", 1)
        return first, middle, last
        return first, last, middle
    except ValueError:
        return custom_id, None, None


def calculate_marks(all_q, marks_q, correct, ratio=None):
    wrong = all_q - correct
    if ratio and ":" in ratio:
        pos, neg = map(int, ratio.split(":"))
        neg_marks = wrong * marks_q * (neg / pos)
    else:
        neg_marks = 0
    return all_q * marks_q, (correct * marks_q) - neg_marks


def get_timestamp_and_year(timestamp):
    if timestamp is None:
        timestamp = TimeStamp.now_iso()
    
    dt = TimeStamp.timestamp(timestamp)
    return dt.strftime("%d %B, %Y at %I:%M %p"), dt.strftime("%Y")


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


def convert_int_values(data):
    """
    Recursively converts all numeric string values inside
    dicts/lists to integers, leaving non-numeric values unchanged.
    """
    if isinstance(data, dict):
        return {k: convert_int_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_int_values(v) for v in data]
    elif isinstance(data, str):
        # Convert only if string is numeric (including negatives)
        return (
            int(data)
            if data.isdigit() or (data.startswith("-") and data[1:].isdigit())
            else data
        )
    else:
        return data


def calculate_result(total, obtained):
    pct = (obtained / total * 100) if total else 0

    grades = [
        (90, "A+"),
        (80, "A"),
        (70, "B+"),
        (60, "B"),
        (50, "C+"),
        (40, "C"),
        (30, "D"),
    ]

    grade = next((g for p, g in grades if pct >= p), "F")
    result = "Pass" if pct >= 33 else "Fail"

    return round(pct, 1), grade, result


def calculate_exam_score(total_questions, correct_count, incorrect_count):
    marks_per_question = 2
    negative_marking = 0
    """
    Calculate total marks, obtained marks, percentage, grade, and pass/fail for an exam.

    Parameters:
    - total_questions (int): Total number of questions in the exam.
    - correct_count (int): Number of correct answers.
    - incorrect_count (int, optional): Number of incorrect answers. If None, calculated automatically.
    - marks_per_question (int, optional): Marks per correct answer. Default is 2.
    - negative_marking (float, optional): Marks deducted for incorrect answers. Default is 0.

    Returns:
    - total_marks (int): Maximum possible marks.
    - obtained_marks (float): Marks obtained after calculation.
    - percentage (float): Percentage score.
    - grade (str): Grade based on percentage.
    - result (str): "Pass" if percentage >= 33%, else "Fail".
    """

    # Calculate marks
    total_marks = marks_per_question * total_questions
    obtained_marks = (marks_per_question * correct_count) - (
        negative_marking * incorrect_count
    )

    percentage, grade, result = calculate_result(total_marks, obtained_marks)

    return total_marks, obtained_marks, percentage, grade, result


async def get_result_datals(controller_query, record):
    # --- Prepare correct answers ---
    correct_answers = {
        q["id"]: (paper, q["correct_answer"])
        for paper, qs in controller_query.questions.items()
        for q in qs
    }

    details = convert_int_values(controller_query.details)

    # --- Duplicate subjects ---
    subject_counts = Counter(v[1].strip() for v in details.values())
    dup_subjects = {s for s, c in subject_counts.items() if c > 1}

    # --- Collect responses per paper ---
    paper_query = defaultdict(list)

    for content in record.content.values():
        for qid, opts, act in content:
            paper, correct = correct_answers[qid]

            if isinstance(act, int) and act < len(opts):
                sel = opts[act]
            elif act is False:
                sel = None
            else:
                sel = act

            paper_query[paper].append((sel, correct, act))

    # --- Initialize totals ---
    full_marks = full_obtained = correct_total = 0
    all_skipped = all_attempted = 0

    papers = []

    # --- Process each paper ---
    for paper, responses in paper_query.items():
        all_q, sub, cog, time_, marks_q, ratio = details[paper]

        correct = skipped = attempted = 0

        for sel, cor, act in responses:
            if sel is None:
                skipped += 1
            else:
                attempted += 1
                if sel == cor:
                    correct += 1

        incorrect = attempted - correct

        total_marks, obtained = calculate_marks(all_q, marks_q, correct, ratio)
        percentage, grade, result = calculate_result(total_marks, obtained)

        # sub_name = f"{sub} ~ {cog}" if sub in dup_subjects else sub
        sub_name = f"{sub} ~ {cog}"

        # accumulate totals
        full_marks += total_marks
        full_obtained += obtained
        correct_total += correct
        all_skipped += skipped
        all_attempted += attempted

        print(sub_name, full_obtained, obtained)

        papers.append(
            [
                sub_name,
                [total_marks, attempted, skipped, correct, incorrect],
                [
                    total_marks,
                    obtained,
                    round(percentage, 2),
                    num2words(obtained, lang="en"),
                    grade,
                    result,
                ],
            ]
        )

    # --- Final summary ---
    total_q = len(correct_answers)
    incorrect_total = total_q - correct_total

    published, result_year = get_timestamp_and_year(controller_query.publish_timestamp)

    percentage = (full_obtained / full_marks * 100) if full_marks else 0
    result = "Pass" if percentage >= 33 else "Fail"
    total_grade = get_grade(full_obtained, full_marks)

    return [
        [
            f"NS{record.id:04}",
            controller_query.exam_name,
            None,
            published,
            result_year,
        ],
        [total_q, incorrect_total, correct_total, all_skipped, all_attempted],
        papers,
        [
            full_marks,
            full_obtained,
            round(percentage, 2),
            num2words(full_obtained, lang="en"),
            total_grade,
            result,
        ],
    ]


def get_expired_time(start_timestamp, minutes):
    if not start_timestamp:
        return None
    if isinstance(start_timestamp, datetime):
        start_timestamp = start_timestamp.timestamp()  # ms

    expiration_time = start_timestamp + (minutes * 60)
    return (time.time()) < expiration_time


def is_expired_exam(timestamp):
    if not timestamp:
        return True

    if isinstance(timestamp, datetime):
        timestamp = timestamp.timestamp()

    return (time.time()) > timestamp


def int_to_timestamp(time):
    try:
        if isinstance(time, (int, float)):
            if time > 1e12:
                time = time

            if time <= 0:
                raise ValueError("Timestamp must be positive.")

            return datetime.fromtimestamp(time)

    except Exception as e:
        print(f"Invalid target_time value: {time}. Error: {e}")
        return None


def get_format_date(dt):

    if not dt:
        return None

    dt = TimeStamp.timestamp(dt)
    day = dt.day
    suffix = (
        "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    return f"{day}{suffix} {dt.strftime('%B %Y')}"


def update_countdown(target_time):
    try:
        if isinstance(target_time, (int, float)):
            if target_time > 1e12:  # Likely in milliseconds
                target_time = target_time
            if target_time <= 0:
                raise ValueError("Timestamp must be positive.")
            target_time = datetime.fromtimestamp(target_time)
    except Exception as e:
        print(f"Invalid target_time value: {target_time}. Error: {e}")
        return None

    current_time = datetime.now()
    diff = target_time - current_time

    if diff.total_seconds() <= 0:
        print("Countdown complete!")
        return target_time

    total_seconds = int(diff.total_seconds())

    days = total_seconds // (60 * 60 * 24)
    hours = (total_seconds % (60 * 60 * 24)) // (60 * 60)
    minutes = (total_seconds % (60 * 60)) // 60
    seconds = total_seconds % 60

    formatted = (
        f"{str(days).zfill(2)} Days, {str(hours).zfill(2)} Hours, "
        f"{str(minutes).zfill(2)} Minutes, {str(seconds).zfill(2)} Seconds"
    )

    return formatted


from includes.db.models.utils import TimeStamp


def time_until(target_time: int):
    current_time = TimeStamp.now_timestamp()

    # Milliseconds difference (target_time bhi int/ms me hona chahiye)
    diff_ms = target_time - current_time

    # Milliseconds ko seconds me convert karein
    seconds_remaining = max(0, int(diff_ms / 1000))

    return target_time, seconds_remaining


def result_not_public_message():
    return {
        "title": "Result Not Available Publicly",
        "desc": [
            "This result is currently not accessible to the public.",
            "Please check back later or contact the administrator for more information.",
        ],
    }


def result_public_message(target_time):
    return {
        "title": "Result is not public",
        "desc": [
            f"Your exam was successfully submitted on {get_format_date( target_time)}.",
            "This result is not publicly available.",
            "Please check your access permissions or try again later.",
        ],
    }


def exam_not_started_message(target_time):
    return {
        "title": "Please Wait for the Exam Date",
        "desc": [
            f"Your exam is scheduled for {get_format_date(target_time)}. You’ll be able to join once it becomes active. Please check back on the scheduled date."
        ],
        "action": "fe40dt",
    }


def exam_submitted_message(href):
    return {
        "title": "Test Successfully Submitted",
        "desc": [
            "Thank you for completing the test and submitting your responses successfully.",
            "You will receive your results soon; please check back later.",
            {"tagName": "a", "href": href, "inner": "Check Result"},
        ],
    }


def get_request_rejected_message(response):
    return {
        "title": "Request Rejected",
        "desc": [
            "Your request to join the exam was not approved. Please contact your instructor/teacher for further assistance.",
            f"Exam Code : {response['code']}",
            f"Instructor : {response['teacherName']}",
        ],
    }


def get_waiting_message(exam_name):
    return {
        "title": "Waiting for exam to start",
        "desc": [
            f"Exam Name: {exam_name}",
            "You are currently in waiting mode. Please do not close this page until the countdown ends. The test will start automatically once the timer reaches zero.",
        ],
    }


def error_exam_message():
    return {
        "title": "404 - Exam Not Found",
        "desc": [
            "The exam you're looking for could not be found. It may have been removed, renamed, or never existed."
        ],
    }


def get_invalid_activity_error():
    return {
        "title": "404 - Invalid Activity",
        "action": "fe40dt",
        "desc": ["The requested activity does not exist or is invalid."],
    }


def completed_exam_message(timestamp, href):
    return {
        "submitExame": True,
        "url": "",
        "title": "Ohho!",
        "desc": [
            "Your exam has been successfully completed.",
            f"Exam submitted at {TimeStamp.format_ts(timestamp, "%d %B, %Y at %I:%M %p")}",
            {"tagName": "a", "href": href, "inner": "Check Result"},
        ],
    }


def exam_timeout_message(timestamp, href):
    return {
        "title": "Time's Up!",
        "desc": [
            "The allotted time for this exam has ended.",
            f"Exam automatically submitted at {TimeStamp.format_ts(timestamp, "%d %B, %Y at %I:%M %p")}",
            {"tagName": "a", "href": href, "inner": "Ok"},
        ],
    }


def block_exam_message(href):
    return {
        # "submitExame": True,
        "title": "Exam Notice",
        "desc": [
            "You are informed that the examiner has expelled a student from the examination hall due to non-compliance with examination rules. More information can be obtained from the examination authority.",
            {"tagName": "a", "href": href, "inner": "Report it"},
        ],
    }


def remove_exam_message(href):
    return {
        "title": "Exam Notice",
        "desc": [
            "You are informed that the examiner has expelled a student from the examination hall due to non-compliance with examination rules. More information can be obtained from the examination authority.",
            {"tagName": "a", "href": "/exam", "inner": "Ok"},
        ],
    }


def calculate_exam_stats(t):
    aq_count = 0
    al_marks = 0
    al_times = 0
    end_time = None

    details = convert_int_values(t.details)

    for q_count, _, _, time, number_pq, _ in details.values():
        aq_count += q_count
        al_times += time
        al_marks += q_count * number_pq

    if t.start_timestamp:
        end_time = t.start_timestamp + (al_times * 60 * 1000)

    return {
        "totalQuestion": aq_count,
        "totalMarks": al_marks,
        "totalTime": al_times,
        "endTime": end_time,
    }


async def get_exam_status_message(message_status: str) -> dict | None:
    message_group = {
        ExamRqStatus.REQUEST_REJECTED: {
            "English": {
                "title": "Request Rejected",
                "message": (
                    "Your request for this exam has been rejected. "
                    "Please contact the administrator for more details."
                ),
            },
            "Hindi": {
                "title": "अनुरोध अस्वीकार किया गया",
                "message": (
                    "इस परीक्षा के लिए आपका अनुरोध अस्वीकार कर दिया गया है। "
                    "अधिक जानकारी के लिए कृपया प्रशासक से संपर्क करें।"
                ),
            },
        },
        ExamRqStatus.BLOCK_IN_EXAM: {
            "English": {
                "title": "Exam Access Blocked",
                "message": (
                    "You are not authorized to access this exam because "
                    "your participation has been blocked by the administrator."
                ),
            },
            "Hindi": {
                "title": "परीक्षा प्रवेश अवरुद्ध",
                "message": (
                    "आपको इस परीक्षा में प्रवेश की अनुमति नहीं है क्योंकि "
                    "प्रशासक द्वारा आपकी भागीदारी अवरुद्ध कर दी गई है।"
                ),
            },
        },
        ExamRqStatus.STUDENT_REMOVED_FROM_EXAM: {
            "English": {
                "title": "Exam Removal Notice",
                "message": (
                    "You have been removed from this examination. "
                    "You are no longer eligible to appear for this exam. "
                    "If you believe this is an error, please contact the examination administrator."
                ),
            },
            "Hindi": {
                "title": "परीक्षा से हटाया गया",
                "message": (
                    "आपको इस परीक्षा से हटा दिया गया है। "
                    "अब आप इस परीक्षा में शामिल होने के पात्र नहीं हैं। "
                    "यदि आपको लगता है कि यह गलती से हुआ है, तो कृपया परीक्षा प्रशासक से संपर्क करें।"
                ),
            },
        },
    }

    language = await app_context.setting.get("language") or "English"

    return message_group.get(message_status, {}).get(language)


rejection_reasons = {
    "mobile": {
        "title": "Mobile Number Not Verified",
        "description": "Your mobile number has not been successfully verified. Please complete the mobile number verification process before submitting your educator verification request again.",
    },
    "doc_missing": {
        "title": "Required Document Not Uploaded",
        "description": "One or more mandatory documents required for educator verification have not been uploaded. Please upload all the required documents and make sure they are complete and valid before resubmitting.",
    },
    "doc_invalid": {
        "title": "Invalid or Incorrect Document",
        "description": "One or more submitted documents are not valid or do not meet the required verification criteria. Please review the document requirements and upload the correct documents before submitting again.",
    },
    "doc_clear": {
        "title": "Document Not Clear or Readable",
        "description": "The submitted document is unclear, blurred, cropped, or otherwise difficult to read. Please upload a clear, complete, and high-quality copy of the required document.",
    },
    "info_match": {
        "title": "Information Does Not Match",
        "description": "The information provided in your educator profile does not match the details shown on the submitted documents. Please verify your information and update any incorrect details before resubmitting.",
    },
    "info_incomplete": {
        "title": "Incomplete Information",
        "description": "Some of the information required to complete your educator verification is missing or incomplete. Please provide all required details and ensure that the submitted information is accurate.",
    },
    "doc_expired": {
        "title": "Expired Document",
        "description": "One or more submitted documents are expired and cannot be accepted for verification. Please provide a valid and currently active document before submitting your verification request again.",
    },
    "rules": {
        "title": "Verification Rules Not Followed",
        "description": "Your verification request does not meet one or more of the required verification rules or guidelines. Please review the verification requirements carefully and make the necessary changes before resubmitting.",
    },
    "other": {
        "title": "Other Reason",
        "description": "Your educator verification request cannot be approved due to a reason not covered by the options above. Please provide a clear explanation of the issue so the educator can understand what needs to be corrected.",
    },
}
