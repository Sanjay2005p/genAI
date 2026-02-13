import json
import os

from openai import OpenAI


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def generate_quiz_question(subject, grade_level="school"):
    client = _get_client()
    if client is None:
        question = f"What is 2 + 2 in {subject}?"
        return {
            "question": question,
            "answer": "4",
            "hint": f"Basic {subject} arithmetic for grade {grade_level}.",
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You create one short quiz question and answer. "
                    "Return valid JSON only with keys: question, answer, hint."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Subject: {subject}. Grade level: {grade_level}. "
                    "Create one easy question."
                ),
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    return {
        "question": data.get("question", "").strip(),
        "answer": data.get("answer", "").strip(),
        "hint": data.get("hint", "").strip(),
    }


def check_quiz_answer(question, correct_answer, student_answer):
    client = _get_client()
    if client is None:
        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
        return {
            "verdict": "Correct" if is_correct else "Wrong",
            "feedback": "Good job." if is_correct else f"Review the concept. Correct answer: {correct_answer}",
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are grading a student answer. "
                    "Return valid JSON only with keys: verdict, feedback. "
                    "verdict must be Correct or Wrong."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Correct answer: {correct_answer}\n"
                    f"Student answer: {student_answer}"
                ),
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    verdict = data.get("verdict", "Wrong").strip()
    if verdict not in {"Correct", "Wrong"}:
        verdict = "Wrong"
    return {
        "verdict": verdict,
        "feedback": data.get("feedback", "").strip(),
    }
