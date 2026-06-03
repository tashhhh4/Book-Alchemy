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


# Cover API Helper

def fetch_cover(isbn):
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"


# Do the database

def insert_book(title, author_id, isbn, year):
    """ Creates a new book in the database. """
    book = Book(
        title=title,
        author_id=author_id,
        isbn=isbn,
        publication_year=year,
    )
    db.session.add(book)
    db.session.commit()
    return book


def list_books():
    """ Returns a collection of Books, ordered by title. """
    books = db.session.execute(db.select(Book).order_by(Book.title)).scalars()

    # Add a cover image to each book if available
    result = []
    for book in books:
        if book.isbn:
            book.set_image(fetch_cover(book.isbn))
        result.append(book)

    return sorted(result, key=lambda b: b.get_meaningful_sort_title())


def insert_author(name, birthdate, deathdate):
    """ Creates a new author in the database. """
    author = Author(
        name=name,
        birth_date=birthdate,
        date_of_death=deathdate,
    )
    db.session.add(author)
    db.session.commit()
    return author


def list_authors():
    """ Returns a collection of Authors, sorted by last name. """
    authors = db.session.execute(db.select(Author).order_by(Author.id)).scalars()
    return sorted(authors, key=lambda a: a.get_sort_name())



# Define routes

@app.route("/", methods=["GET"])
def home():
    books = list_books()
    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    message = None

    if request.method == "POST":
        author = insert_author(
            request.form["name"],
            make_date(request.form["birthdate"]),
            make_date(request.form["date_of_death"]),
        )
        message = f"Added {author}"

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    message = None

    if request.method == "POST":
        book = insert_book(
            request.form["title"],
            request.form["author"], # author id
            request.form["isbn"],
            request.form["year"],
        )
        message = f"Added {book.__repr__()}"

    authors = list_authors()
    return render_template("add_book.html", authors=authors, message=message)


if __name__ == "__main__":

    app.run()

    # DB Migrations
    # with app.app_context():
        # db.create_all()