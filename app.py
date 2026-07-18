

from flask import Flask, render_template, request, redirect, url_for, make_response, session
import json
import os
import uuid
from functools import wraps

app = Flask(__name__)

# ---------------------------------------------------------------
# SCHOOL / ELECTION SETTINGS
# ---------------------------------------------------------------
SCHOOL_NAME = "AMUPS Kadalundi Nagaram"
POST_NAME = "School Leader"
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-something-random")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme123")

# ---------------------------------------------------------------
# CANDIDATES
# Edit the "name" for each candidate.
# The "symbol" filename must match an image file you place inside
# the static/symbols folder (e.g. static/symbols/star.png).
# ---------------------------------------------------------------
CANDIDATES = [
    {"id": 1, "name": "അമീന മുംതാസ് കെ പി",   "symbol": "symbol1.png"},
    {"id": 2, "name": "ആയിഷ ഫിദ  പി",   "symbol": "symbol2.png"},
    {"id": 3, "name": "മുഹമ്മദ് സിയാൻ കെ", "symbol": "symbol3.png"},
    {"id": 4, "name": "നൈല സഫിയ  കെ എം പി",  "symbol": "symbol4.png"},
]

VOTES_FILE = "votes.json"


def load_votes():
    if not os.path.exists(VOTES_FILE):
        return {"counts": {str(c["id"]): 0 for c in CANDIDATES}, "voted_ids": []}
    with open(VOTES_FILE, "r") as f:
        return json.load(f)


def save_votes(data):
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    return render_template(
        "index.html",
        school_name=SCHOOL_NAME,
        post_name=POST_NAME,
        candidates=CANDIDATES,
    )


@app.route("/vote", methods=["POST"])
def vote():
    data = load_votes()
    candidate_id = request.form.get("candidate_id")

    if candidate_id in data["counts"]:
        data["counts"][candidate_id] += 1
        save_votes(data)

    return redirect(url_for("thanks"))


@app.route("/thanks")
def thanks():
    return render_template("thanks.html", school_name=SCHOOL_NAME)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("results"))
        error = "Incorrect password."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/results")
def results():
    data = load_votes()
    result_list = []
    total = sum(data["counts"].values())
    for c in CANDIDATES:
        count = data["counts"].get(str(c["id"]), 0)
        percent = round((count / total) * 100, 1) if total > 0 else 0
        result_list.append({**c, "count": count, "percent": percent})

    result_list.sort(key=lambda x: x["count"], reverse=True)

    return render_template(
        "results.html",
        school_name=SCHOOL_NAME,
        post_name=POST_NAME,
        results=result_list,
        total=total,
    )


@app.route("/reset")
def reset():
    # Visit this page (e.g. http://127.0.0.1:5000/reset) to wipe all votes
    # and start the election over. Remove or password-protect this in real use.
    save_votes({"counts": {str(c["id"]): 0 for c in CANDIDATES}, "voted_ids": []})
    return "All votes have been reset. <a href='/'>Go back to voting page</a>"




if __name__ == "__main__":
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")

    threading.Timer(1.5, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
