"""TaskBoard - a tiny Flask task manager that keeps its tasks in a JSON file.

A small internal to-do list for a team at Zurich. It is deliberately simple:
a handful of routes, server-rendered HTML forms (no JavaScript framework) and
a single JSON file as its "database". That file is the point of the course:
where it lives, who may write to it and whether it survives a restart are
exactly the questions containers and OpenShift make you answer.

Routes
  GET  /                     the task list with an add form
  POST /tasks                add a task          (form field: title)
  POST /tasks/<id>/toggle    mark a task done / not done
  POST /tasks/<id>/delete    delete a task
  GET  /api/tasks            the task list as JSON
  GET  /healthz              health check used by OpenShift probes

Configuration (environment variables)
  PORT       port for the Flask dev server         (default 8080)
  DATA_DIR   directory that holds tasks.json       (default ./data)
  GREETING   heading shown on the page             (default "TaskBoard")
"""
import fcntl
import json
import os
import socket
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template_string, request

app = Flask(__name__)

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))
DATA_FILE = DATA_DIR / "tasks.json"
LOCK_FILE = DATA_DIR / ".tasks.lock"
MAX_TITLE = 200

# Written to tasks.json the first time the app starts with an empty DATA_DIR.
SEED_TASKS = [
    {"title": "Review claim #4711 (water damage, Lisbon)", "done": False},
    {"title": "Call customer about motor policy renewal", "done": False},
    {"title": "Prepare Q3 risk report for the claims team", "done": True},
]


# --------------------------------------------------------------------------
# Storage: one JSON file, guarded by a lock, written atomically.
# gunicorn runs several worker processes, so two requests can write at the
# same time - the lock serialises them, and write-to-temp + rename means a
# crash mid-write never leaves a half-written tasks.json behind.
# --------------------------------------------------------------------------
def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def _locked():
    _ensure_data_dir()
    with open(LOCK_FILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _read_tasks() -> list:
    if not DATA_FILE.exists():
        tasks = [dict(t, id=uuid.uuid4().hex[:8], created=_now()) for t in SEED_TASKS]
        _write_tasks(tasks)
        return tasks
    with open(DATA_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def _write_tasks(tasks: list) -> None:
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, prefix=".tasks-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(tasks, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.chmod(tmp, 0o664)  # group-writable: other UIDs in GID 0 may take over the file
    os.replace(tmp, DATA_FILE)


def load_tasks() -> list:
    with _locked():
        return _read_tasks()


def update_tasks(mutate) -> None:
    """Read tasks, apply `mutate(tasks)` and write them back - all under the lock."""
    with _locked():
        tasks = _read_tasks()
        mutate(tasks)
        _write_tasks(tasks)


# --------------------------------------------------------------------------
# The page
#
# Form actions and redirects are deliberately *relative* ("tasks", "../..")
# rather than absolute ("/tasks"). The app is often reached through a reverse
# proxy that adds a path prefix - the training server's code editor serves it
# at /proxy/8090/, and an OpenShift Route could do the same - and relative
# URLs keep working under any prefix without the app having to know it.
# --------------------------------------------------------------------------
PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ greeting }}</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 640px; padding: 0 1rem; color: #1f2933; }
    h1 { color: #0870b0; margin-bottom: 0.25rem; }
    .sub { color: #5b6b7b; margin-top: 0; }
    form.add { display: flex; gap: 0.5rem; margin: 1.25rem 0; }
    form.add input[type=text] { flex: 1; padding: 0.5rem 0.6rem; font-size: 1rem; border: 1px solid #c3ccd6; border-radius: 4px; }
    button { padding: 0.45rem 0.8rem; font-size: 0.95rem; border: 1px solid #0870b0; border-radius: 4px; background: #0870b0; color: #fff; cursor: pointer; }
    button.secondary { background: #fff; color: #0870b0; }
    button.danger { background: #fff; color: #b03030; border-color: #b03030; }
    ul.tasks { list-style: none; padding: 0; margin: 0; }
    ul.tasks li { display: flex; align-items: center; gap: 0.6rem; padding: 0.55rem 0.2rem; border-bottom: 1px solid #e4e9ee; }
    ul.tasks li .title { flex: 1; }
    ul.tasks li.done .title { text-decoration: line-through; color: #8a98a6; }
    ul.tasks li form { margin: 0; }
    .empty { color: #8a98a6; font-style: italic; }
    .meta { color: #5b6b7b; font-size: 0.85rem; margin-top: 1.5rem; }
    .meta code { background: #f1f4f7; padding: 0.1rem 0.3rem; border-radius: 3px; }
  </style>
</head>
<body>
  <h1>☑ {{ greeting }}</h1>
  <p class="sub">{{ open_count }} open &middot; {{ done_count }} done</p>

  <form class="add" method="post" action="tasks">
    <label for="title" style="position:absolute;left:-9999px">New task</label>
    <input id="title" type="text" name="title" placeholder="What needs doing?" maxlength="{{ max_title }}" required autofocus>
    <button type="submit">Add</button>
  </form>

  {% if tasks %}
  <ul class="tasks">
    {% for t in tasks %}
    <li class="{{ 'done' if t.done else '' }}">
      <form method="post" action="tasks/{{ t.id }}/toggle">
        <button type="submit" class="secondary" aria-label="{{ 'Mark as not done' if t.done else 'Mark as done' }}">{% if t.done %}↺ Undo{% else %}✓ Done{% endif %}</button>
      </form>
      <span class="title">{{ t.title }}</span>
      <form method="post" action="tasks/{{ t.id }}/delete">
        <button type="submit" class="danger" aria-label="Delete task">✕</button>
      </form>
    </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="empty">No tasks yet. Add one above.</p>
  {% endif %}

  <p class="meta">
    Served by host <strong>{{ host }}</strong> at {{ now }} UTC.<br>
    Tasks are stored in <code>{{ data_file }}</code>.
  </p>
</body>
</html>
"""


def _greeting() -> str:
    return os.environ.get("GREETING", "TaskBoard")


@app.route("/")
def index():
    tasks = load_tasks()
    return render_template_string(
        PAGE,
        greeting=_greeting(),
        tasks=tasks,
        open_count=sum(1 for t in tasks if not t["done"]),
        done_count=sum(1 for t in tasks if t["done"]),
        max_title=MAX_TITLE,
        host=socket.gethostname(),
        now=_now(),
        data_file=DATA_FILE.resolve(),
    )


@app.route("/tasks", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if not title or len(title) > MAX_TITLE:
        abort(400, "title must be 1-%d characters" % MAX_TITLE)
    update_tasks(lambda tasks: tasks.append(
        {"id": uuid.uuid4().hex[:8], "title": title, "done": False, "created": _now()}
    ))
    return redirect(".", code=303)        # from /tasks back to the list


@app.route("/tasks/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    def flip(tasks):
        for t in tasks:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                return
        abort(404)
    update_tasks(flip)
    return redirect("../..", code=303)    # from /tasks/<id>/toggle back to the list


@app.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task(task_id):
    def remove(tasks):
        tasks[:] = [t for t in tasks if t["id"] != task_id]
    update_tasks(remove)
    return redirect("../..", code=303)    # from /tasks/<id>/delete back to the list


@app.route("/api/tasks")
def api_tasks():
    return jsonify(load_tasks())


@app.route("/healthz")
def healthz():
    """Liveness/readiness probe used by OpenShift.

    Reports 503 when the data directory cannot be written - exactly what
    happens when the image is not prepared for OpenShift's arbitrary UID.
    """
    try:
        _ensure_data_dir()
        writable = os.access(DATA_DIR, os.W_OK)
    except OSError:
        writable = False
    body = {
        "status": "ok" if writable else "error",
        "host": socket.gethostname(),
        "data_dir": str(DATA_DIR.resolve()),
        "data_dir_writable": writable,
    }
    return jsonify(body), (200 if writable else 503)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
