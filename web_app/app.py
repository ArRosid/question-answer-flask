from flask import Flask, g, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import dbcon

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    db = dbcon.get_db()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        hashed_password = generate_password_hash(password, method='sha256')
        db.execute(''' insert into users (name, password, expert, admin)
                       values (?, ?, ?, ?)''',
                       [username, hashed_password, '0', '0'])
        db.commit()

        return redirect(url_for('index'))
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    db = dbcon.get_db()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_cur = db.execute("select id, name, password from users where name = ? ", [username])
        user = user_cur.fetchone()

        if check_password_hash(user["password"], password):
            return "<h1>Login Successful!</h1>"
        else:
            return "<h1>Login failed</h1>"

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)
