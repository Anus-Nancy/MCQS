import os
from math import ceil
from flask import Flask, render_template, request, redirect, url_for, session, flash
from gemini_client import generate_mcqs

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

SUBJECTS = ["Physics", "Chemistry", "Mathematics"]
CLASSES = ["11", "12"]


def chunk_count(total, chunk_size):
    return [min(chunk_size, total - idx) for idx in range(0, total, chunk_size)]


@app.route("/")
def index():
    return render_template("index.html", subjects=SUBJECTS, classes=CLASSES)


@app.route("/generate", methods=["POST"])
def generate():
    subject = request.form.get("subject")
    class_level = request.form.get("class_level")
    try:
        total_questions = int(request.form.get("question_count", "0"))
    except ValueError:
        total_questions = 0

    if subject not in SUBJECTS or class_level not in CLASSES or total_questions <= 0:
        flash("Please select a valid subject, class, and MCQ count.")
        return redirect(url_for("index"))

    batches = chunk_count(total_questions, 25)
    mcqs = []
    for batch_size in batches:
        batch = generate_mcqs(subject=subject, class_level=class_level, count=batch_size)
        if not batch:
            flash("Unable to generate MCQs right now. Please try again.")
            return redirect(url_for("index"))
        mcqs.extend(batch)

    session["mcqs"] = mcqs
    session["quiz_meta"] = {
        "subject": subject,
        "class_level": class_level,
        "total": total_questions,
    }
    return redirect(url_for("quiz"))


@app.route("/quiz")
def quiz():
    mcqs = session.get("mcqs")
    meta = session.get("quiz_meta")
    if not mcqs or not meta:
        flash("Please generate a quiz first.")
        return redirect(url_for("index"))
    return render_template("quiz.html", mcqs=mcqs, meta=meta)


@app.route("/submit", methods=["POST"])
def submit():
    mcqs = session.get("mcqs")
    if not mcqs:
        flash("Your quiz session expired. Please generate again.")
        return redirect(url_for("index"))

    answers = {
        key.replace("question_", ""): value
        for key, value in request.form.items()
        if key.startswith("question_")
    }

    correct = 0
    for idx, mcq in enumerate(mcqs):
        selected = answers.get(str(idx))
        if selected and selected == mcq.get("correct_answer"):
            correct += 1

    total = len(mcqs)
    wrong = total - correct
    percentage = round((correct / total) * 100, 2) if total else 0

    session["result"] = {
        "correct": correct,
        "wrong": wrong,
        "percentage": percentage,
        "total": total,
    }
    return redirect(url_for("result"))


@app.route("/result")
def result():
    result_data = session.get("result")
    meta = session.get("quiz_meta")
    if not result_data or not meta:
        flash("No results found. Please generate a quiz first.")
        return redirect(url_for("index"))
    return render_template("result.html", result=result_data, meta=meta)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
