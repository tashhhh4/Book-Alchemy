from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define models

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def get_sort_name(self):
        """ Tries to get the author's last name.
        If the author's name is only one word,
        returns the original name.
        """
        parts = self.name.split(" ")
        last_name = parts[-1]
        return last_name

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        output = self.__str__()
        return output


class Book (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer, unique=True) # isbn-13
    title = db.Column(db.String(300), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.ForeignKey("author.id"))

    def __str__(self):
        return f"Book \"{self.title}\""

    def __repr__(self):
        output = self.__str__()
        if self.publication_year:
            output += f" ({self.publication_year})"
        if self.isbn:
            output += f" <ISBN-{self.isbn}>"
        return output