from flask import g, Flask, render_template, request, redirect, url_for
import dbcon
from werkzeug.security import generate_password_hash, check_password_hash

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)