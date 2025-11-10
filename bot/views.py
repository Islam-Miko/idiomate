def create_final_result_view(
    questions: list[dict], correct_answers: int
) -> str:
    result_lines = [
        f"Quiz Completed! You answered {correct_answers} out of {len(questions)} questions correctly.",  # noqa
        "",
        "Here are the correct answers:",
        "",
    ]
    for idx, question in enumerate(questions, start=1):
        correct_option = question["options"][0]
        result_lines.append(f"{idx}) {question['q']}:\n Ans: {correct_option}")
    return "\n".join(result_lines)
