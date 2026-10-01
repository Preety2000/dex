from includes.core.globals.entry import app_context, GlobleCatch
from includes.db.models.owner import Subject
from includes.db.models.secondary import QuizQuestion, QuizRelationships
from includes.utils.utils import create_slug, get_post_value


class AdminApiMCQ:

    @classmethod
    async def _get_data(cls):
        fields = [
            "title",
            "category",
            "correct_answer",
            "incorrect_answer",
            "excerpt",
            "s-status",
            "subject",
        ]

        data = {field: await get_post_value(field) for field in fields}

        string_fields = [
            "title",
            "correct_answer",
            "excerpt",
            "s-status",
            "subject",
        ]

        for field in string_fields:
            if not isinstance(data[field], str) or not data[field].strip():
                return None, f"{field} is required."

        if not isinstance(data["category"], list) or not data["category"]:
            return None, "Category is required."

        if (
            not isinstance(data["incorrect_answer"], list)
            or not data["incorrect_answer"]
        ):
            return None, "Incorrect answers are required."

        return data, None

    @classmethod
    def _update_relationships(cls, db, question_id, category):
        GlobleCatch.get_with_terms = None

        db.query(QuizRelationships).filter(
            QuizRelationships.quiz_id == question_id
        ).delete()

        relationships = [
            QuizRelationships(
                terms_id=int(category_id),
                quiz_id=question_id,
            )
            for category_id in category
        ]

        if relationships:
            db.add_all(relationships)

    @classmethod
    def _update_question(cls, question, data, subject):
        question.question = data["title"]
        question.excerpt = data["excerpt"]
        question.correct_answer = data["correct_answer"]
        question.incorrect_answers = data["incorrect_answer"]
        question.subject_id = subject.id
        question.status = data["s-status"]

    @classmethod
    def _create_question(cls, db, data, subject):
        question = QuizQuestion(
            question=data["title"],
            excerpt=data["excerpt"],
            correct_answer=data["correct_answer"],
            incorrect_answers=data["incorrect_answer"],
            subject_id=subject.id,
            status=data["s-status"],
            views=0,
        )
        db.add(question)
        db.flush()
        cls._update_relationships(
            db,
            question.id,
            data["category"],
        )
        db.commit()
        return {
            "success": True,
            "message": "Question created successfully.",
            "data": {
                "id": question.id,
                "name": data["title"],
                "subject_id": subject.id,
            },
        }

    @classmethod
    async def insert(cls):
        replace = await get_post_value("replace")

        data, error = await cls._get_data()

        if error:
            return {"error": error}

        msb, db = await app_context.db.configure()

        # Subject find
        subject = msb.query(Subject).filter(Subject.name == data["subject"]).first()

        if subject is None:
            return {"error": "6a8473f9-73d4-83ea-ba81-6a76a0d9fd8"}

        # Existing question find
        existing_question = (
            db.query(QuizQuestion)
            .filter(
                QuizQuestion.question == data["title"],
                QuizQuestion.correct_answer == data["correct_answer"],
            )
            .first()
        )

        try:
            # --------------------------------
            # Replace existing question
            # --------------------------------
            if existing_question:
                if not replace:
                    return {
                        "error": (
                            f"This question already exists with the title "
                            f"<strong>{existing_question.question}</strong>. "
                            f"Please choose a different question."
                        )
                    }

                if existing_question != data["title"]:
                    # Create new question
                    return cls._create_question(cls, db, data, subject)

                cls._update_question(
                    existing_question,
                    data,
                    subject,
                )

                cls._update_relationships(
                    db,
                    existing_question.id,
                    data["category"],
                )

                db.commit()

                return {
                    "replace": True,
                    "data": {
                        "id": existing_question.id,
                        "name": data["title"],
                        "subject_id": subject.id,
                    },
                }

            # --------------------------------
            # Create new question
            # --------------------------------
            return cls._create_question(cls, db, data, subject)

        except Exception:
            db.rollback()
            raise
