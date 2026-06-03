from data_models import Book

# Test get_meaningful_sort_title
book = Book(
    title="The Fellowship of the Ring",
    author_id=None,
    isbn=None,
    publication_year=None,
)
assert book.get_meaningful_sort_title() == "fellowship of the ring"