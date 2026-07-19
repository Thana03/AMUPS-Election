from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from functools import wraps

app = Flask(__name__)

SCHOOL_NAME = "AMUPS Kadalundi Nagaram"

app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-something-random")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme123")

# ---------------------------------------------------------------
# SCHOOL LEADER CANDIDATES
# Edit names here. Symbol filenames must exist in static/symbols/
# ---------------------------------------------------------------
SCHOOL_LEADER_CANDIDATES = [
    {"id": 1, "name": "അമീന മുംതാസ് കെ പി",   "symbol": "symbol1.png"},
    {"id": 2, "name": "ആയിഷ ഫിദ  പി",   "symbol": "symbol2.png"},
    {"id": 3, "name": "മുഹമ്മദ് സിയാൻ കെ", "symbol": "symbol3.png"},
    {"id": 4, "name": "നൈല സഫിയ  കെ എം പി",  "symbol": "symbol4.png"},
]

# ---------------------------------------------------------------
# CLASS LEADER ELECTIONS
# Add one block per class. "id" must be unique, short, no spaces
# (used in the web address). Use unique symbol filenames per class
# so classes don't overwrite each other's images.
# ---------------------------------------------------------------
CLASSES = [
    {
        "id": "classIVa",
        "name": "Class IV A",
        "candidates": [
            {"id": 1, "name": "ആയിഷ അംന പി വി", "symbol": "symbol1.png"},
            {"id": 2, "name": "മുഹ്സിന ടി ടി", "symbol": "symbol5.png"},
            {"id": 3, "name": "റബീഹ് പി പി", "symbol": "symbol7.png"},
            {"id": 4, "name": "റയ്യാൻ പി വി", "symbol": "symbol2.png"},
        ],
    },
    {
        "id": "classIVb",
        "name": "Class IV B",
        "candidates": [
            {"id": 1, "name": "മുഹമ്മദ് ഹാഷിം കെ", "symbol": "symbol3.png"},
            {"id": 2, "name": "ബിഷറുൽ ഹാഫി", "symbol": "symbol2.png"},
            {"id": 3, "name": "ഫാത്തിമ നദ  വി", "symbol": "symbol1.png"},
            {"id": 4, "name": "ജസ സൈന  വി പി", "symbol": "symbol7.png"},
        ],
    },
    {
        "id": "classVa",
        "name": "Class V A",
        "candidates": [
            {"id": 1, "name": "ഫാത്തിമ ഇഫ്‌സ", "symbol": "symbol6.png"},
            {"id": 2, "name": "നഫീസത്തുൽ മിസ്‌രിയ", "symbol": "symbol4.png"},
            {"id": 3, "name": "മുഹമ്മദ് ഇഹ്ത്തിഷാൻ", "symbol": "symbol5.png"},
            {"id": 4, "name": "മുഹമ്മദ് തമീം വി പി", "symbol": "symbol1.png"},
        ],
    },
    {
        "id": "classVb",
        "name": "Class V B",
        "candidates": [
            {"id": 1, "name": "ഹിന അയ്യൂബ് വി പി", "symbol": "symbol3.png"},
            {"id": 2, "name": "മിൻഹാജുൽ ഹഖ്  കെ പി", "symbol": "symbol2.png"},
            {"id": 3, "name": "നൈല സഫിയ കെ എം പി", "symbol": "symbol6.png"},
            {"id": 4, "name": "ഫാത്തിമ മലീഹ കെ പി", "symbol": "symbol5.png"},
        ],
    },
    {
        "id": "classVIa",
        "name": "Class VI A",
        "candidates": [
            {"id": 1, "name": "ഫാത്തിമ ഷഹാന കെ പി", "symbol": "symbol6.png"},
            {"id": 2, "name": "ഫാത്തിമ ഹിബ കെ പി", "symbol": "symbol4.png"},
        ],
    },
    {
        "id": "classVIb",
        "name": "Class VI B",
        "candidates": [
            {"id": 1, "name": "ആസ്ബിൻ അൻവർ", "symbol": "symbol2.png"},
            {"id": 2, "name": "മുഹമ്മദ് ഷിബിലി", "symbol": "symbol7.png"},
        ],
    },
    {
        "id": "classVIc",
        "name": "Class VI C",
        "candidates": [
            {"id": 1, "name": "ഫാത്തിമ ഫഹ്‌മ എ എൻ", "symbol": "symbol6.png"},
            {"id": 2, "name": "മുഹമ്മദ് റബീഹ് എം പി", "symbol": "symbol2.png"},
            {"id": 3, "name": "ഷിഫ മെഹറിൻ പി", "symbol": "symbol4.png"},
        ],
    },
    {
        "id": "classVIIa",
        "name": "Class VII A",
        "candidates": [
            {"id": 1, "name": "ഇസ്മായിൽ എ", "symbol": "symbol1.png"},
            {"id": 2, "name": "ഫാത്തിമ ഷഫ് ല  വി പി", "symbol": "symbol2.png"},
        ],
    },
    {
        "id": "classVIIb",
        "name": "Class VII B",
        "candidates": [
            {"id": 1, "name": "മുഹമ്മദ് സിയാൻ വി കെ ", "symbol": "symbol2.png"},
            {"id": 2, "name": "മുഹമ്മദ് റാസി", "symbol": "symbol6.png"},
        ],
    },

    
]

VOTES_FILE = "votes.json"


def default_votes():
    data = {
        "school_leader": {str(c["id"]): 0 for c in SCHOOL_LEADER_CANDIDATES},
        "classes": {},
    }
    for cls in CLASSES:
        data["classes"][cls["id"]] = {str(c["id"]): 0 for c in cls["candidates"]}
    return data


def load_votes():
    if not os.path.exists(VOTES_FILE):
        return default_votes()

    with open(VOTES_FILE, "r") as f:
        data = json.load(f)

    defaults = default_votes()

    if "school_leader" not in data:
        data["school_leader"] = defaults["school_leader"]
    else:
        for cid in defaults["school_leader"]:
            data["school_leader"].setdefault(cid, 0)

    if "classes" not in data:
        data["classes"] = {}
    for cls_id, counts in defaults["classes"].items():
        if cls_id not in data["classes"]:
            data["classes"][cls_id] = counts
        else:
            for cid in counts:
                data["classes"][cls_id].setdefault(cid, 0)

    return data


def save_votes(data):
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_class(class_id):
    for cls in CLASSES:
        if cls["id"] == class_id:
            return cls
    return None


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


def build_result_list(candidates, counts):
    total = sum(counts.values())
    result_list = []
    for c in candidates:
        count = counts.get(str(c["id"]), 0)
        percent = round((count / total) * 100, 1) if total > 0 else 0
        result_list.append({**c, "count": count, "percent": percent})
    result_list.sort(key=lambda x: x["count"], reverse=True)
    return result_list, total


@app.route("/")
def home():
    return render_template("home.html", school_name=SCHOOL_NAME)


@app.route("/school-leader")
def school_leader():
    return render_template(
        "vote_page.html",
        school_name=SCHOOL_NAME,
        page_title="School Leader",
        candidates=SCHOOL_LEADER_CANDIDATES,
        vote_action=url_for("school_leader_vote"),
        back_url=url_for("home"),
    )


@app.route("/school-leader/vote", methods=["POST"])
def school_leader_vote():
    data = load_votes()
    candidate_id = request.form.get("candidate_id")
    if candidate_id in data["school_leader"]:
        data["school_leader"][candidate_id] += 1
        save_votes(data)
    return redirect(url_for("thanks"))


@app.route("/class-leader")
def class_leader_list():
    return render_template(
        "class_list.html",
        school_name=SCHOOL_NAME,
        classes=CLASSES,
    )


@app.route("/class-leader/<class_id>")
def class_leader_vote_page(class_id):
    cls = get_class(class_id)
    if not cls:
        return "Class not found", 404
    return render_template(
        "vote_page.html",
        school_name=SCHOOL_NAME,
        page_title=cls["name"] + " - Class Leader",
        candidates=cls["candidates"],
        vote_action=url_for("class_leader_vote", class_id=class_id),
        back_url=url_for("class_leader_list"),
    )


@app.route("/class-leader/<class_id>/vote", methods=["POST"])
def class_leader_vote(class_id):
    cls = get_class(class_id)
    if not cls:
        return "Class not found", 404
    data = load_votes()
    candidate_id = request.form.get("candidate_id")
    if candidate_id in data["classes"].get(class_id, {}):
        data["classes"][class_id][candidate_id] += 1
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
            return redirect(url_for("results_overview"))
        error = "Incorrect password."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


@app.route("/results")
@admin_required
def results_overview():
    return render_template(
        "results_overview.html",
        school_name=SCHOOL_NAME,
        classes=CLASSES,
    )


@app.route("/results/school-leader")
@admin_required
def results_school_leader():
    data = load_votes()
    result_list, total = build_result_list(SCHOOL_LEADER_CANDIDATES, data["school_leader"])
    return render_template(
        "results_page.html",
        school_name=SCHOOL_NAME,
        page_title="School Leader",
        results=result_list,
        total=total,
        reset_url=url_for("reset_school_leader"),
        back_url=url_for("results_overview"),
    )


@app.route("/results/class/<class_id>")
@admin_required
def results_class(class_id):
    cls = get_class(class_id)
    if not cls:
        return "Class not found", 404
    data = load_votes()
    counts = data["classes"].get(class_id, {})
    result_list, total = build_result_list(cls["candidates"], counts)
    return render_template(
        "results_page.html",
        school_name=SCHOOL_NAME,
        page_title=cls["name"] + " - Class Leader",
        results=result_list,
        total=total,
        reset_url=url_for("reset_class", class_id=class_id),
        back_url=url_for("results_overview"),
    )


@app.route("/reset/school-leader")
@admin_required
def reset_school_leader():
    data = load_votes()
    data["school_leader"] = {str(c["id"]): 0 for c in SCHOOL_LEADER_CANDIDATES}
    save_votes(data)
    return "School Leader votes reset. <a href='" + url_for("results_overview") + "'>Back to results</a>"


@app.route("/reset/class/<class_id>")
@admin_required
def reset_class(class_id):
    cls = get_class(class_id)
    if not cls:
        return "Class not found", 404
    data = load_votes()
    data["classes"][class_id] = {str(c["id"]): 0 for c in cls["candidates"]}
    save_votes(data)
    return "Votes reset for " + cls["name"] + ". <a href='" + url_for("results_overview") + "'>Back to results</a>"


if __name__ == "__main__":
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.5, open_browser).start()

    app.run(host="0.0.0.0", port=5000, debug=True)
