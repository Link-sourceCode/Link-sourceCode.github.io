from flask import Flask, render_template, redirect, \
        url_for, request, session, flash, g
from functools import wraps
import sqlite3
from config import *
# config file hinzufügen

app = Flask(__name__)

app.secret_key = SECRET_KEY
app.databese = "database.db" # nach Config verschieben

# Sperren von bestimmten bereichen
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# Start seite --> evtl. zu Welcome ändern
@app.route('/home')
@login_required
def home():
    g.db = connect_db()
    reiter_stadt = """SELECT user.name, staedte.stadt_name FROM user
LEFT JOIN staedte ON staedte.reiterin = user.name
ORDER BY staedte.stadt_name, user.name;"""
    reiterin = """SELECT name FROM user ORDER BY name"""
    cur = g.db.execute(reiterin)
    users = [dict(name = row[0]) for row in cur.fetchall()]
    cur = g.db.execute(reiter_stadt)
    staedte = [dict(name = row[0], stadt = row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template("index.html", users=users, staedte=staedte)

# Willkomensseite
@app.route('/')
def welcome():
    return render_template("welcome.html")

# Blog, sollte für alle Sichtbar sein
@app.route('/blog')
#@login_required
def blog():
    g.db = connect_db()
    cur = g.db.execute("""SELECT posts.*, user.name AS autor_name
    FROM posts
    LEFT JOIN user ON posts.autor = user.name;""")
    posts = [dict(title = row[1], autor = row[3]) for row in cur.fetchall()]
    print(posts)
    g.db.close()
    return render_template("blog.html", posts=posts)

@app.route('/board')
@login_required
def board():
    return render_template("board.html")

# Login
@app.route('/login', methods=['GET', 'POST']) # GET ist gegeben, aber POST muss explizit genannt werden
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session["logged_in"] = True
            flash("Du bist nun eingeloggt!")
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Du wurdest ausgelogged!")
    return redirect(url_for("welcome"))

def connect_db():
    return sqlite3.connect("database.db")

if __name__ == '__main__':
    app.run(debug=DEBUG)