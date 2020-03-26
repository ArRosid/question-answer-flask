import os

from flask import (Flask, g, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import dbcon

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    user_result = None

    if 'user' in session:
        user = session["user"]

        db = dbcon.get_db()
        user_cur = db.execute("select * from users where name = ?", [user])
        user_result = user_cur.fetchone()

    return user_result

def get_unanswered_question(expert_user_id):
    db = dbcon.get_db()
    question_cur = db.execute('''select id from questions 
                                 where answer_text is null and expert_id=?''',
                                 [expert_user_id])

    question_result = dbcon.extract_dbs(question_cur.fetchall())

    return len(question_result)

@app.route("/")
def index():
    user = get_current_user()

    # Get unanswered question count (only for expert)
    unanswered_q = None
    if user is not None:
        unanswered_q = get_unanswered_question(user["id"])

    db = dbcon.get_db()

    questions_cur = db.execute(''' select questions.id, questions.question_text, 
                                        asker.name as asker_name, expert.name as expert_name
                                   from questions 
                                   join users as asker on asker.id = questions.asked_by_id
                                   join users as expert on expert.id = questions.expert_id 
                                   where answer_text is not null  ''')

    questions_results = dbcon.extract_dbs(questions_cur.fetchall())    

    return render_template("home.html", user=user, 
                            questions=questions_results, 
                            unanswered_q=unanswered_q)

@app.route("/register", methods=["GET", "POST"])
def register():
    db = dbcon.get_db()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        existing_user_cur = db.execute("select id from users where name=?", [username])
        existing_user = existing_user_cur.fetchone()

        if existing_user:
            return render_template("register.html", error="User already exist!")

        hashed_password = generate_password_hash(password, method='sha256')
        db.execute(''' insert into users (name, password, expert, admin)
                       values (?, ?, ?, ?)''',
                       [username, hashed_password, '0', '0'])
        db.commit()

        session["user"] = username
        return redirect(url_for('index'))
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    db = dbcon.get_db()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_cur = db.execute("select id, name, password from users where name = ? ",
                               [username])
        user = user_cur.fetchone()

        if check_password_hash(user["password"], password):
            session["user"] = user["name"]
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/ask", methods=["GET","POST"])
def ask():
    user = get_current_user()
    db = dbcon.get_db()

    if request.method == "POST":
        db.execute('''insert into questions (question_text, asked_by_id, expert_id)
                      values (?,?,?)''',
                      [request.form["question"], user["id"], request.form["expert"]])
        db.commit()

        return redirect(url_for("index"))

    expert_cur = db.execute("select id, name from users where expert = 1")
    expert_result = expert_cur.fetchall()

    return render_template("ask.html", user=user, experts=expert_result)


@app.route("/unanswered")
def unanswered():
    user = get_current_user()
    unanswered_q = get_unanswered_question(user["id"])

    db = dbcon.get_db()

    question_cur = db.execute('''select questions.id, questions.question_text, 
                                    questions.asked_by_id, users.name 
                                 from questions 
                                 join users on users.id = questions.asked_by_id
                                 where answer_text is null and expert_id = ?''',
                                 [user["id"]])

    question_result = question_cur.fetchall()

    return render_template("unanswered.html", user=user, 
                            questions=question_result,
                            unanswered_q=unanswered_q)


@app.route("/answer/<question_id>", methods=["GET","POST"])
def answer(question_id):
    user = get_current_user()

    db = dbcon.get_db()

    if request.method == "POST":
        db.execute("update questions set answer_text = ? where id=?",
                    [request.form["answer"], question_id])
        db.commit()
        return redirect(url_for("unanswered"))

    question_cur = db.execute("select id, question_text from questions where id=?", [question_id])
    question = question_cur.fetchone()

    return render_template("answer.html", user=user, question=question)


@app.route("/question/<question_id>")
def question(question_id):
    user = get_current_user
    db = dbcon.get_db()
    question_cur = db.execute('''select questions.question_text, questions.answer_text, 
                                    asker.name as asker_name, expert.name as expert_name
                                from questions 
                                join users as asker on asker.id = questions.asked_by_id
                                join users as expert on expert.id = questions.expert_id 
                                where questions.id = ?''', [question_id])

    question_result = dbcon.extract_db(question_cur.fetchone())

    return render_template("question.html", question=question_result)


@app.route("/users")
def users():
    user = get_current_user()

    db = dbcon.get_db()
    users_cur = db.execute("select id, name, expert, admin from users")
    users_results = users_cur.fetchall()

    return render_template("users.html", user=user, users=users_results)

@app.route("/promote/<user_id>")
def promote(user_id):
    db = dbcon.get_db()
    user_cur = db.execute("select expert from users where id = ?", [user_id])
    user_result = user_cur.fetchone()

    if user_result["expert"]: # if user expert, set user to non expert
        db.execute("update users set expert = 0 where id = ?", [user_id])
        db.commit()
    else: # if user is not expert, set user to expert
        db.execute("update users set expert = 1 where id = ?", [user_id])
        db.commit()

    return redirect(url_for("users"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)
