import json
import math
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend; must be set before pyplot is imported anywhere

from flask import Flask, render_template_string, request, send_from_directory, url_for

# CHANGE THIS to the name of the .py file (without the extension) that contains your function.
from histogram_work import plot_grade_histogram

BASE_DIR = Path(__file__).resolve().parent
PLOT_FILENAME = "grade_histogram.png"
STATE_FILE = BASE_DIR / "last_inputs.json"

app = Flask(__name__)

FORM_PAGE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Grade Histogram</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }
    .fields { display: flex; gap: 1.5rem; }
    .field { flex: 1; display: flex; flex-direction: column; }
    label { font-weight: 600; margin-bottom: 0.4rem; }
    textarea { height: 280px; font-family: monospace; font-size: 1rem; padding: 0.5rem; }
    .hint { color: #666; font-size: 0.85rem; margin-top: 0.3rem; }
    button { margin-top: 1.2rem; padding: 0.6rem 1.6rem; font-size: 1rem; cursor: pointer; }
    .error { background: #fde8e8; color: #9b1c1c; padding: 0.7rem 1rem; border-radius: 6px; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>Grade Histogram</h1>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="post" action="{{ url_for('plot') }}">
    <div class="fields">
      <div class="field">
        <label for="scores">Scores</label>
        <textarea id="scores" name="scores">{{ scores }}</textarea>
        <span class="hint">One score per line, e.g. 98.5</span>
      </div>
      <div class="field">
        <label for="boundaries">Boundaries</label>
        <textarea id="boundaries" name="boundaries">{{ boundaries }}</textarea>
        <span class="hint">One boundary per line, e.g. 90</span>
      </div>
    </div>
    <button type="submit">Plot</button>
  </form>
</body>
</html>
"""

RESULT_PAGE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Histogram</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; text-align: center; }
    img { max-width: 100%; height: auto; }
    a { display: inline-block; margin-top: 1rem; }
  </style>
</head>
<body>
  <img src="{{ image_url }}" alt="Grade histogram">
  <br>
  <a href="{{ url_for('index') }}">&larr; Back</a>
</body>
</html>
"""


def parse_numbers(text, label):
    """Turn one-number-per-line text into a list of floats, with friendly errors."""
    values = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            value = float(line)
        except ValueError:
            raise ValueError(f"{label}, line {line_no}: '{line}' is not a number")
        if not math.isfinite(value):
            raise ValueError(f"{label}, line {line_no}: '{line}' is not a finite number")
        values.append(value)
    if not values:
        raise ValueError(f"{label}: please enter at least one value")
    return values


def load_last_inputs():
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return str(data.get("scores", "")), str(data.get("boundaries", ""))
    except (OSError, ValueError):
        return "", ""


def save_last_inputs(scores, boundaries):
    try:
        STATE_FILE.write_text(
            json.dumps({"scores": scores, "boundaries": boundaries}), encoding="utf-8"
        )
    except OSError:
        pass


@app.route("/")
def index():
    scores, boundaries = load_last_inputs()
    return render_template_string(FORM_PAGE, scores=scores, boundaries=boundaries, error=None)


@app.route("/plot", methods=["POST"])
def plot():
    scores_text = request.form.get("scores", "")
    boundaries_text = request.form.get("boundaries", "")
    save_last_inputs(scores_text, boundaries_text)

    try:
        grades = parse_numbers(scores_text, "Scores")
        boundaries = parse_numbers(boundaries_text, "Boundaries")
        plot_grade_histogram(grades, boundaries, str(BASE_DIR / PLOT_FILENAME))
    except ValueError as e:
        return render_template_string(
            FORM_PAGE, scores=scores_text, boundaries=boundaries_text, error=str(e)
        ), 400
    except Exception as e:
        return render_template_string(
            FORM_PAGE,
            scores=scores_text,
            boundaries=boundaries_text,
            error=f"Plotting failed: {e}",
        ), 500

    # The timestamp makes the browser fetch the new image instead of showing a cached one.
    image_url = url_for("plot_image", v=int(time.time() * 1000))
    return render_template_string(RESULT_PAGE, image_url=image_url)


@app.route("/plot-image")
def plot_image():
    response = send_from_directory(BASE_DIR, PLOT_FILENAME)
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)