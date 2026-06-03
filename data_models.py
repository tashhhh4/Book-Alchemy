from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define models

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__(self)


class Book (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(300), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.ForeignKey("author.id"))

    def __str__(self):
        return f"Book '{self.title}'"

    def __repr__(self):
        return f"{self.title} <ISBN-{self.isbn}>"