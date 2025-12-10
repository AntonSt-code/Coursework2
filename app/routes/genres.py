from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.models import Genre, Book, BookGenre
from app.forms import GenreForm
from app.utils.decorators import admin_required

genres_bp = Blueprint('genres', __name__, url_prefix='/genres')

@genres_bp.route('/')
def list_all():
    page = request.args.get('page', 1, type=int)
    
    pagination = Genre.query.order_by(Genre.name).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template('genres/list.html',
                         genres=pagination.items,
                         pagination=pagination)

@genres_bp.route('/<int:genre_id>')
def detail(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    
    # Отримати книги цього жанру
    page = request.args.get('page', 1, type=int)
    books_query = Book.query.join(Book.book_genres)\
        .filter(BookGenre.genre_id == genre_id)\
        .filter(Book.is_active == True)
    
    pagination = books_query.paginate(
        page=page,
        per_page=current_app.config['BOOKS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('genres/detail.html', 
                         genre=genre, 
                         books=pagination.items,
                         pagination=pagination)

@genres_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = GenreForm()
    
    if form.validate_on_submit():
        genre = Genre(
            name=form.name.data,
            description=form.description.data
        )
        
        db.session.add(genre)
        db.session.commit()
        
        flash('Жанр успішно додано!', 'success')
        return redirect(url_for('genres.detail', genre_id=genre.id))
    
    return render_template('genres/create.html', form=form)

@genres_bp.route('/<int:genre_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm(obj=genre)
    
    if form.validate_on_submit():
        genre.name = form.name.data
        genre.description = form.description.data
        
        db.session.commit()
        
        flash('Жанр оновлено!', 'success')
        return redirect(url_for('genres.detail', genre_id=genre.id))
    
    return render_template('genres/edit.html', form=form, genre=genre)

@genres_bp.route('/<int:genre_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    
    # Перевірка чи є книги з цим жанром
    books_count = genre.book_genres.count()
    if books_count > 0:
        flash(f'Неможливо видалити жанр. Є {books_count} книг з цим жанром.', 'danger')
        return redirect(url_for('genres.detail', genre_id=genre_id))
    
    db.session.delete(genre)
    db.session.commit()
    
    flash('Жанр видалено.', 'info')
    return redirect(url_for('genres.list_genres'))
