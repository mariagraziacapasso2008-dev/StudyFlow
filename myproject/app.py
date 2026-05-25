from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "studyflow"


# =========================
# INIT DATABASE
# =========================
def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # TASKS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            user TEXT
        )
    """)

    # EVENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            time TEXT,
            user TEXT
        )
    """)

    # ORARIO SCOLASTICO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            day TEXT,
            hour TEXT,
            subject TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["nome"]
        return redirect("/")
    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# =========================
# HOME
# =========================
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE user=?", (session["user"],))
    tasks = cursor.fetchall()

    conn.close()

    return render_template("index.html", tasks=tasks)


# =========================
# ADD TASK
# =========================
@app.route("/add", methods=["POST"])
def add_task():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, user) VALUES (?, ?)",
        (request.form["task"], session["user"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# DELETE TASK
# =========================
@app.route("/delete/<int:id>", methods=["POST"])
def delete_task(id):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# POMODORO
# =========================
@app.route("/pomodoro")
def pomodoro():
    if "user" not in session:
        return redirect("/login")
    return render_template("pomodoro.html")


# =========================
# CALENDAR
# =========================
@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            INSERT INTO events (title, date, time, user)
            VALUES (?, ?, ?, ?)
        """, (
            request.form["title"],
            request.form["date"],
            request.form.get("time", ""),
            session["user"]
        ))

        conn.commit()

    cursor.execute("SELECT * FROM events WHERE user=?", (session["user"],))
    events = cursor.fetchall()

    conn.close()

    return render_template("calendar.html", events=events)


# =========================
# DELETE EVENT
# =========================
@app.route("/delete_event/<int:id>", methods=["POST"])
def delete_event(id):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM events WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/calendar")


# =========================
# STATS
# =========================
@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user=?", (session["user"],))
    tasks_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events WHERE user=?", (session["user"],))
    events_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "stats.html",
        tasks=tasks_count,
        events=events_count
    )


# =========================
# ORARIO SCOLASTICO
# =========================
@app.route("/orario")
def orario():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT day, hour, subject
        FROM orario
        WHERE user=?
    """, (session["user"],))

    rows = cursor.fetchall()
    conn.close()

    return render_template("orario.html", rows=rows)


# =========================
# ADD ORARIO
# =========================
@app.route("/add_orario", methods=["POST"])
def add_orario():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orario (user, day, hour, subject)
        VALUES (?, ?, ?, ?)
    """, (
        session["user"],
        request.form["day"],
        request.form["hour"],
        request.form["subject"]
    ))

    conn.commit()
    conn.close()

    return redirect("/orario")


# =========================
# START APP
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)