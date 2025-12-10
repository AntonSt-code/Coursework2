from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Review, Book, Log
from app.forms import ReviewForm

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/books/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def create(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Перевірка чи вже є відгук
    existing = Review.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if existing:
        flash('Ви вже залишили відгук на цю книгу.', 'warning')
        return redirect(url_for('books.detail', book_id=book_id))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            book_id=book_id,
            rating=int(form.rating.data),
            title=form.title.data,
            review_text=form.review_text.data
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Логування додавання відгуку
        log = Log(
            user_id=current_user.id,
            book_id=book_id,
            action='add_review',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Дякуємо за відгук!', 'success')
        return redirect(url_for('books.detail', book_id=book_id))
    
    return render_template('reviews/create.html', form=form, book=book)

@reviews_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(review_id):
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id:
        flash('Ви не можете редагувати цей відгук.', 'danger')
        return redirect(url_for('books.detail', book_id=review.book_id))
    
    form = ReviewForm(obj=review)
    
    if form.validate_on_submit():
        review.rating = int(form.rating.data)
        review.title = form.title.data
        review.review_text = form.review_text.data
        
        db.session.commit()
        
        flash('Відгук оновлено!', 'success')
        return redirect(url_for('books.detail', book_id=review.book_id))
    
    return render_template('reviews/edit.html', form=form, review=review)

@reviews_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete(review_id):
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id and not current_user.is_admin():
        flash('Ви не можете видалити цей відгук.', 'danger')
        return redirect(url_for('books.detail', book_id=review.book_id))
    
    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()
    
    flash('Відгук видалено.', 'info')
    return redirect(url_for('books.detail', book_id=book_id))
