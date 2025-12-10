from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.models import Author, Book, BookAuthor
from app.forms import AuthorForm
from app.utils.decorators import admin_required

authors_bp = Blueprint('authors', __name__, url_prefix='/authors')

@authors_bp.route('/')
def list_authors():
    page = request.args.get('page', 1, type=int)
    
    pagination = Author.query.order_by(Author.last_name, Author.first_name).paginate(
        page=page,
        per_page=current_app.config['AUTHORS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('authors/list.html',
                         authors=pagination.items,
                         pagination=pagination,
                         Book=Book)

@authors_bp.route('/<int:author_id>')
def detail(author_id):
    author = Author.query.get_or_404(author_id)
    
    # Отримати книги автора
    books = Book.query.join(Book.book_authors)\
        .filter_by(author_id=author_id)\
        .filter(Book.is_active==True)\
        .all()
    
    return render_template('authors/detail.html', author=author, books=books)

@authors_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = AuthorForm()
    
    if form.validate_on_submit():
        author = Author(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            bio=form.bio.data,
            birth_date=form.birth_date.data,
            death_date=form.death_date.data,
            country=form.country.data
        )
        
        db.session.add(author)
        db.session.commit()
        
        flash('Автора додано!', 'success')
        return redirect(url_for('authors.detail', author_id=author.id))
    
    return render_template('authors/create.html', form=form)

@authors_bp.route('/<int:author_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(author_id):
    author = Author.query.get_or_404(author_id)
    form = AuthorForm(obj=author)
    
    if form.validate_on_submit():
        author.first_name = form.first_name.data
        author.last_name = form.last_name.data
        author.middle_name = form.middle_name.data
        author.bio = form.bio.data
        author.birth_date = form.birth_date.data
        author.death_date = form.death_date.data
        author.country = form.country.data
        
        db.session.commit()
        
        flash('Автора оновлено!', 'success')
        return redirect(url_for('authors.detail', author_id=author.id))
    
    return render_template('authors/edit.html', form=form, author=author)

@authors_bp.route('/<int:author_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(author_id):
    author = Author.query.get_or_404(author_id)
    
    # Перевірка чи є книги цього автора
    if author.book_authors.count() > 0:
        flash('Неможливо видалити автора, який має книги в системі.', 'danger')
        return redirect(url_for('authors.detail', author_id=author_id))
    
    db.session.delete(author)
    db.session.commit()
    
    flash('Автора видалено.', 'info')
    return redirect(url_for('authors.list_authors'))
