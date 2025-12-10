from app import create_app, db
from app.models import User, Author, Genre, Book, BookAuthor, BookGenre, File, Favorite, Review, Log

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Author': Author,
        'Genre': Genre,
        'Book': Book,
        'BookAuthor': BookAuthor,
        'BookGenre': BookGenre,
        'File': File,
        'Favorite': Favorite,
        'Review': Review,
        'Log': Log
    }

if __name__ == '__main__':
    app.run(debug=True)
