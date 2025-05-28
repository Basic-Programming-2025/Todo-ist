import threading
import webview
from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import json, os
from datetime import datetime, timedelta
from plyer import notification
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict
import calendar

app = Flask(__name__)
CORS(app)

DATA_FILE = "tasks.json"
scheduler = BackgroundScheduler()
scheduler.start()

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

def get_calendar(year, month):
    cal = calendar.Calendar()
    weeks = cal.monthdayscalendar(year, month)
    return [[day if day != 0 else None for day in week] for week in weeks]

def load_todos():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def notify(task, label=""):
    notification.notify(
        title=f"{label} {task['title']}",
        message=task['desc'],
        app_name="TodoList",
        timeout=10
    )

def schedule_alarms(task, task_id):
    deadline = task.get("deadline")
    if not deadline:
        return

    deadline = datetime.fromisoformat(deadline)
    now = datetime.now()
    alert_times = [
        (deadline - timedelta(hours=4), "⏰ 4시간 전! 🚀 제목 : "),
        (deadline - timedelta(hours=2), "⏰ 2시간 전! 🚀 제목 : "),
        (deadline - timedelta(minutes=10), "⏰ 30분 전! 🚀 제목 : ")
    ]

    for i, (alert_time, label) in enumerate(alert_times):
        if alert_time > now:
            scheduler.add_job(
                notify,
                'date',
                run_date=alert_time,
                args=[task, label],
                id=f"{task_id}-{i}",
                replace_existing=True
            )

def cancel_alarms(task_id):
    for i in range(3):
        job_id = f"{task_id}-{i}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

@app.route("/")
def index():
    year = int(request.args.get("year", datetime.now().year))
    month = int(request.args.get("month", datetime.now().month))
    selected_date = request.args.get("selected_date", datetime.now().strftime("%Y-%m-%d"))

    tasks = load_todos()
    todos = defaultdict(list)

    for i, task in enumerate(tasks):
        task_with_id = {"id": i, **task}
        todos[task["date"]].append(task_with_id)

    calendar_data = get_calendar(year, month)

    return render_template("index.html",
                           year=year,
                           month=month,
                           calendar=calendar_data,
                           selected_date=selected_date,
                           todos=todos)

@app.route("/add", methods=["POST"])
def add_task():
    date = request.form.get("date")
    title = request.form.get("title")
    desc = request.form.get("desc")
    deadline = request.form.get("deadline")

    task = {
        "date": date,
        "title": title,
        "desc": desc,
        "deadline": deadline,
        "done": False
    }

    with open(DATA_FILE, "r+", encoding="utf-8") as f:
        try:
            tasks = json.load(f)
        except:
            tasks = []

        tasks.append(task)
        f.seek(0)
        f.truncate()
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    task_id = len(tasks) - 1
    schedule_alarms(task, task_id)

    return redirect(url_for('index', selected_date=task["date"]))

@app.route("/toggle", methods=["POST"])
def toggle_done():
    try:
        task_id = int(request.form.get("task_id"))
    except:
        return redirect(url_for("index"))

    with open(DATA_FILE, "r+", encoding="utf-8") as f:
        try:
            tasks = json.load(f)
        except:
            tasks = []

        if 0 <= task_id < len(tasks):
            tasks[task_id]["done"] = not tasks[task_id].get("done", False)
            date = tasks[task_id]["date"]
            f.seek(0)
            f.truncate()
            json.dump(tasks, f, ensure_ascii=False, indent=2)
            return redirect(url_for("index", selected_date=date))

    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_task():
    try:
        task_id = int(request.form.get("task_id"))
    except:
        return redirect(url_for("index"))

    with open(DATA_FILE, "r+", encoding="utf-8") as f:
        try:
            tasks = json.load(f)
        except:
            tasks = []

        if 0 <= task_id < len(tasks):
            deleted = tasks.pop(task_id)
            f.seek(0)
            f.truncate()
            json.dump(tasks, f, ensure_ascii=False, indent=2)
            cancel_alarms(task_id)
            return redirect(url_for('index', selected_date=deleted["date"]))

    return redirect(url_for('index'))

def start_flask():
    app.run()

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("Todo List", "http://localhost:5000")
    webview.start(gui='edgechromium')
