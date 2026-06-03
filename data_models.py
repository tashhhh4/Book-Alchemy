from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define models

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", back_populates="author")

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
    isbn = db.Column(db.Integer) # isbn-13
    title = db.Column(db.String(300), nullable=False)
    publication_year = db.Column(db.Integer)

    author_id = db.Column(db.ForeignKey("author.id"))
    author = db.relationship("Author", back_populates="books")

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
        return f"Book \"{self.title}\""

    def __repr__(self):
        output = self.__str__()
        if self.publication_year:
            output += f" ({self.publication_year})"
        if self.isbn:
            output += f" <ISBN-{self.isbn}>"
        return output