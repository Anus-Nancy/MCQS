import json
import os
from typing import List, Dict, Optional

import google.generativeai as genai

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def load_prompt(filename: str) -> str:
    path = os.path.join(PROMPT_DIR, filename)
    with open(path, "r", encoding="utf-8") as file:
        return file.read().strip()


def safe_json_parse(text: str) -> Optional[List[Dict]]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def validate_mcqs(data: object) -> Optional[List[Dict]]:
    if not isinstance(data, list):
        return None

    normalized = []
    for item in data:
        if not isinstance(item, dict):
            return None
        question = item.get("question")
        options = item.get("options")
        correct_answer = item.get("correct_answer")
        if (
            not isinstance(question, str)
            or not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(opt, str) for opt in options)
            or not isinstance(correct_answer, str)
            or correct_answer not in options
        ):
            return None
        normalized.append(
            {
                "question": question.strip(),
                "options": [opt.strip() for opt in options],
                "correct_answer": correct_answer.strip(),
            }
        )
    return normalized


def generate_mcqs(subject: str, class_level: str, count: int) -> Optional[List[Dict]]:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    system_prompt = load_prompt("system_prompt.txt")
    mcq_prompt = load_prompt("mcq_prompt.txt")
    prompt = mcq_prompt.format(subject=subject, class_level=class_level, count=count)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
    )

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json",
        },
    )

    raw_text = response.text.strip()
    parsed = safe_json_parse(raw_text)
    return validate_mcqs(parsed)
