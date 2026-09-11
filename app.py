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

def sort_books(books, field, reverse=False):
    """ Returns books sorted according to the 'field' and 'reverse' parameters. """

    # Title sorting as default
    result = sorted(books, key=lambda b: b.get_meaningful_sort_title(), reverse=reverse)

    match field:
        case "author":
            result = sorted(books, key=lambda b: b.author.get_sort_name(), reverse=reverse)
        case "year":
            result = sorted(books, key=lambda b: b.publication_year or 0, reverse=reverse)
    
    return result


def search_book_titles(books, search):
    """ Returns a list from 'books' if the 'search' term matches or is found in
    the title of the book. Case-insensitive.
    """
    books = [b for b in books if search.lower() in b.title.lower()]
    return books

def clean_isbn(isbn):
    """ Automatically strips whitespace and dashes (-) from ISBN numbers,
    allowing more convenient form entry.
    """
    isbn = isbn.replace(" ", "")
    isbn = isbn.replace("-", "")
    return isbn


def insert_book(title, author_id, isbn, year):
    """ Creates a new book in the database. """
    isbn = clean_isbn(isbn)
    if isbn == "":
        isbn = None

    book = Book(
        title=title,
        author_id=author_id,
        isbn=isbn,
        publication_year=year,
    )

    try:
        db.session.add(book)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return book


def get_book_by_isbn(isbn):
    """ Fetches a book with the isbn if exists, or None. """
    book = db.session.execute(db.select(Book).where(Book.isbn==isbn)).scalar_one_or_none()
    return book


def list_books(sort_field=None, reverse=None, search=None):
    """ Returns a collection of Books, ordered by title. """
    books = db.session.execute(db.select(Book).order_by(Book.title)).scalars()

    # Add a cover image to each book if available
    result = []
    for book in books:
        if book.isbn:
            book.set_image(fetch_cover(book.isbn))
        result.append(book)

    result = sort_books(result, sort_field, reverse)

    if search:
        result = search_book_titles(result, search)

    return result


def delete_book(id):
    """ Deletes a book by id and returns its data. """
    book = db.get_or_404(Book, id)
    db.session.delete(book)
    db.session.commit()
    return book


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

@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        book_id = request.form["book_id"]
        book = delete_book(book_id)
        message = f"{book} was deleted."

    field = request.args.get("sort")
    reverse = request.args.get("reverse")
    search = request.args.get("search")

    books = list_books(field, reverse=reverse=="true", search=search)
    return render_template("home.html", books=books, sort=field, reverse=reverse, search=search, message=message)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    message = None
    error = False

    if request.method == "POST":
        name = request.form["name"]
        try:
            author = insert_author(
                name,
                make_date(request.form["birthdate"]),
                make_date(request.form["date_of_death"]),
            )
            message = f"Added {author}"
        except Exception as e:
            error = True
            error_message = str(e)
            if "IntegrityError" in error_message and "author.name" in error_message:
                message = f"Error: Author \"{name}\" already exists!"
            else:
                message = f"An unknown error occurred."

    return render_template("add_author.html", message=message, error=error)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    message = None
    error = False

    if request.method == "POST":
        isbn = request.form["isbn"]
        author = request.form.get("author")
        print("author is", author)
        try:
            book = insert_book(
                request.form["title"],
                author, # author id
                isbn,
                request.form["year"],
            )
            message = f"Added {book.__repr__()}"
        except Exception as e:
            error = True
            error_message = str(e)
            if "IntegrityError" in error_message and "book.isbn" in error_message:
                existing_book = get_book_by_isbn(isbn)
                if not existing_book:
                    message = f"Error: ISBN is already present in database but no book has it (this should never happen)."
                else:
                    message = f"Error: ISBN <{isbn}> already present in database ({existing_book.author} - {existing_book.title})."
            else:
                message = f"An unknown Error occurred."
                print(e)

    authors = list_authors()
    return render_template("add_book.html", authors=authors, message=message, error=error)


if __name__ == "__main__":

    # Create DB Schema
    with app.app_context():
        db.create_all()

    app.run()