
async def _question_stats(answer_key, responses):
    total = len(responses)
    correct = attempted = skipped = 0
    result = []

    for qid, options, choice in responses:
        question = correct_answer = subject = selected_answer = None

        question, correct_answer, subject = answer_key.get(qid, (None, None, None))
        if isinstance(choice, int) and not isinstance(choice, bool) and 0 <= choice < len(options):
            attempted += 1
            selected_answer = options[choice]

            if selected_answer == correct_answer:
                correct += 1

        elif choice is None:
            skipped += 1
        else:
            attempted += 1

        result.append({
            "question_id": qid,
            "question": question,
            "options": options,
            "subject": subject,
            "correct_answer": correct_answer,
            "selected_answer": selected_answer,
        })

    incorrect = total - (correct + skipped)

    return total, attempted, skipped, correct, incorrect, result
