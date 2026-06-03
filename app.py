import os
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

app = Flask(__name__)


# Configure database

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


# Date Helper

def make_date(datestr):
    if not datestr:
        return None
    return datetime.strptime(datestr, "%Y-%m-%d").date()


# Do the database

def insert_author(name, birthdate, deathdate):
    author = Author(
        name=name,
        birth_date=birthdate,
        date_of_death=deathdate,
    )
    db.session.add(author)
    db.session.commit()
    return author

def other_function():
    print("Running other_function.")


# Define routes

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        author = insert_author(
            request.form["name"],
            make_date(request.form["birthdate"]),
            make_date(request.form["date_of_death"]),
        )

        return render_template("add_author.html", message=f"Added {author}")

    return render_template("add_author.html")


@app.route("/add_book")
def add_book():
    return render_template("add_book.html")


if __name__ == "__main__":

    app.run()

    # DB Migrations
    # with app.app_context():
        # db.create_all()