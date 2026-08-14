import os
import urllib.request

import mysql.connector
from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME", "appdb")


def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )


def get_instance_id():
    try:
        req = urllib.request.Request(
            "http://169.254.169.254/latest/meta-data/instance-id"
        )
        return urllib.request.urlopen(req, timeout=1).read().decode()
    except Exception:
        return "unknown"


@app.route("/health")
def health():
    return "OK", 200


@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS tasks
           (id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200), done BOOLEAN DEFAULT FALSE)"""
    )
    cur.execute("SELECT id, title, done FROM tasks ORDER BY id DESC")
    tasks = cur.fetchall()
    conn.close()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <title>Cloud Task Manager</title>

            <style>
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }

                body {
                    font-family: Arial, Helvetica, sans-serif;
                    min-height: 100vh;
                    background: linear-gradient(
                        135deg,
                        #667eea 0%,
                        #764ba2 100%
                    );
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 30px;
                }

                .container {
                    width: 100%;
                    max-width: 650px;
                    background: #ffffff;
                    border-radius: 18px;
                    padding: 35px;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
                }

                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }

                .header h1 {
                    color: #2d3748;
                    font-size: 32px;
                    margin-bottom: 8px;
                }

                .header p {
                    color: #718096;
                    font-size: 14px;
                }

                .instance {
                    margin-top: 12px;
                    font-size: 12px;
                    color: #a0aec0;
                    background: #f7fafc;
                    padding: 8px 12px;
                    border-radius: 8px;
                    display: inline-block;
                }

                .task-form {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 25px;
                }

                .task-form input {
                    flex: 1;
                    padding: 13px 15px;
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    font-size: 15px;
                    outline: none;
                    transition: border-color 0.2s;
                }

                .task-form input:focus {
                    border-color: #667eea;
                }

                .add-btn {
                    border: none;
                    background: #667eea;
                    color: white;
                    padding: 0 22px;
                    border-radius: 10px;
                    cursor: pointer;
                    font-size: 15px;
                    font-weight: bold;
                    transition: background 0.2s, transform 0.1s;
                }

                .add-btn:hover {
                    background: #5a67d8;
                }

                .add-btn:active {
                    transform: scale(0.97);
                }

                .tasks {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }

                .task {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 15px;
                    padding: 15px;
                    background: #f8fafc;
                    border: 1px solid #edf2f7;
                    border-radius: 12px;
                }

                .task-title {
                    flex: 1;
                    color: #2d3748;
                    word-break: break-word;
                }

                .task.completed .task-title {
                    text-decoration: line-through;
                    color: #a0aec0;
                }

                .actions {
                    display: flex;
                    gap: 7px;
                }

                .action-btn {
                    width: 34px;
                    height: 34px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 8px;
                    text-decoration: none;
                    color: white;
                    font-weight: bold;
                    transition: opacity 0.2s;
                }

                .action-btn:hover {
                    opacity: 0.8;
                }

                .done-btn {
                    background: #48bb78;
                }

                .delete-btn {
                    background: #f56565;
                }

                .empty {
                    text-align: center;
                    padding: 30px;
                    color: #a0aec0;
                }

                .footer {
                    text-align: center;
                    margin-top: 25px;
                    font-size: 12px;
                    color: #a0aec0;
                }

                @media (max-width: 600px) {
                    body {
                        padding: 15px;
                    }

                    .container {
                        padding: 25px 20px;
                    }

                    .header h1 {
                        font-size: 26px;
                    }

                    .task-form {
                        flex-direction: column;
                    }

                    .add-btn {
                        padding: 13px;
                    }
                }
            </style>
        </head>

        <body>
            <div class="container">

                <div class="header">
                    <h1>☁️ Cloud Task Manager</h1>
                    <p>Multi-tier Flask application running on AWS</p>

                    <div class="instance">
                        Served by instance: {{ iid }}
                    </div>
                </div>

                <form method="post" action="/add" class="task-form">
                    <input
                        name="title"
                        placeholder="What needs to be done?"
                        required
                    >
                    <button type="submit" class="add-btn">
                        Add Task
                    </button>
                </form>

                <div class="tasks">

                    {% if tasks %}

                        {% for t in tasks %}

                        <div class="task {{ 'completed' if t[2] else '' }}">

                            <div class="task-title">
                                {{ t[1] }}
                            </div>

                            <div class="actions">

                                <a
                                    href="/done/{{ t[0] }}"
                                    class="action-btn done-btn"
                                    title="Mark as done"
                                >
                                    ✓
                                </a>

                                <a
                                    href="/delete/{{ t[0] }}"
                                    class="action-btn delete-btn"
                                    title="Delete task"
                                >
                                    ✕
                                </a>

                            </div>

                        </div>

                        {% endfor %}

                    {% else %}

                        <div class="empty">
                            No tasks yet. Add your first task above!
                        </div>

                    {% endif %}

                </div>

                <div class="footer">
                    AWS • ALB • Auto Scaling • EC2 • RDS
                </div>

            </div>
        </body>
        </html>
        """,
        tasks=tasks,
        iid=get_instance_id(),
    )

@app.route("/add", methods=["POST"])
def add():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s)", (request.form["title"],))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/done/<int:task_id>")
def mark_done(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = TRUE WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
