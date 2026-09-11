from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import CheckConstraint

db = SQLAlchemy()


# Define models

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", back_populates="author")

    __table_args__ = (
        CheckConstraint("length(name) > 0",
                        name="name_min_length"),
    )

    def get_sort_name(self):
        """ Transforms the author's name for sorting.
        
        First the last name is used, then the remainder of the name
        is considered. If the author only has one name,
        that will be their sorting key.
        """
        parts = self.name.split(" ")
        sort_name = parts[-1]
        if len(parts) > 1:
            sort_name += " ".join(parts[:-1])
        return sort_name

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
    author = db.relationship("Author", back_populates="books")

    __table_args__ = (
        CheckConstraint("length(title) > 0",
                        name="title_min_length"),
    )

    def set_image(self, url):
        self.image = url

    def get_meaningful_sort_title(self):
        """ Returns the title, transformed for meaningful sorting.
        
        Removes words like 'the', 'a', and 'an' from the beginning of
        the title and converts the remainder to lowercase.
        """
        words_to_strip = ['the', 'a', 'an', 'der', 'das']
        title = self.title.lower()
        for w in words_to_strip:
            w += " "
            if title.startswith(w):
                return title[len(w):]
        return title


    def __str__(self):
        return f"\"{self.title}\""

    def __repr__(self):
        output = self.__str__()
        if self.author:
            output += f", {self.author}"
        if self.publication_year:
            output += f" ({self.publication_year})"
        if self.isbn:
            output += f" <ISBN-{self.isbn}>"
        return output