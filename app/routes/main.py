from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app.models import Book, Author, Genre, Review, User, Log
from app.forms import SearchForm
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Останні додані книги
    recent_books = Book.query.filter_by(is_active=True)\
        .order_by(Book.created_at.desc()).limit(6).all()
    
    # Популярні книги (за кількістю відгуків)
    popular_books = Book.query.filter_by(is_active=True)\
        .outerjoin(Review, Review.book_id == Book.id)\
        .group_by(Book.id)\
        .order_by(func.count(Review.id).desc())\
        .limit(6).all()
    
    return render_template('index.html', 
                         recent_books=recent_books,
                         popular_books=popular_books)

@main_bp.route('/about')
def about():
    return render_template('about.html', 
                         Book=Book,
                         Author=Author, 
                         User=User,
                         Log=Log)

@main_bp.route('/search')
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('search_type', 'all')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('main.index'))
    
    books_query = Book.query.filter_by(is_active=True)
    
    if search_type == 'title' or search_type == 'all':
        books_query = books_query.filter(Book.title.contains(query))
    
    # TODO: Додати пошук по авторам та ISBN
    
    pagination = books_query.paginate(
        page=page, 
        per_page=current_app.config['BOOKS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('search_results.html',
                         books=pagination.items,
                         pagination=pagination,
                         query=query,
                         search_type=search_type)
