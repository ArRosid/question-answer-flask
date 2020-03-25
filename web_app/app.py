from flask import Flask, render_template

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/")
def index():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)