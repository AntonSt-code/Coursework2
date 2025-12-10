from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Favorite, Book, Log

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html')

@users_bp.route('/favorites')
@login_required
def favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id)\
        .join(Book).filter(Book.is_active==True)\
        .order_by(Favorite.added_at.desc()).all()
    
    return render_template('users/favorites.html', favorites=favorites)

@users_bp.route('/favorites/add/<int:book_id>', methods=['POST'])
@login_required
def add_favorite(book_id):
    book = Book.query.get_or_404(book_id)
    
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if existing:
        flash('Книга вже в обраному.', 'info')
    else:
        favorite = Favorite(user_id=current_user.id, book_id=book_id)
        db.session.add(favorite)
        
        # Логування додавання в обране
        log = Log(
            user_id=current_user.id,
            book_id=book_id,
            action='add_favorite',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Додано до обраного!', 'success')
    
    return redirect(url_for('books.detail', book_id=book_id))

@users_bp.route('/favorites/remove/<int:book_id>', methods=['POST'])
@login_required
def remove_favorite(book_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first_or_404()
    
    db.session.delete(favorite)
    
    # Логування видалення з обраного
    log = Log(
        user_id=current_user.id,
        book_id=book_id,
        action='remove_favorite',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Видалено з обраного.', 'info')
    return redirect(request.referrer or url_for('users.favorites'))
