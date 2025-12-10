from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import User, Book, Author, Review, Log
from app.utils.decorators import admin_required
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Основна статистика
    stats = {
        'total_users': User.query.count(),
        'total_books': Book.query.filter_by(is_active=True).count(),
        'total_authors': Author.query.count(),
        'total_reviews': Review.query.count(),
        'total_downloads': Log.query.filter_by(action='download').count()
    }
    
    # TOP 5 книг за завантаженнями
    top_books = db.session.query(
        Book, func.count(Log.id).label('downloads')
    ).join(Log).filter(Log.action=='download')\
     .group_by(Book.id)\
     .order_by(func.count(Log.id).desc())\
     .limit(5).all()
    
    # Статистика за типами дій
    action_stats = db.session.query(
        Log.action, func.count(Log.id).label('count')
    ).group_by(Log.action).all()
    
    # Активність за останній тиждень
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.session.query(
        func.date(Log.created_at).label('date'),
        func.count(Log.id).label('count')
    ).filter(Log.created_at >= week_ago)\
     .group_by(func.date(Log.created_at))\
     .order_by(func.date(Log.created_at)).all()
    
    # ТОП-5 активних користувачів
    top_users = db.session.query(
        User, func.count(Log.id).label('activity')
    ).join(Log).group_by(User.id)\
     .order_by(func.count(Log.id).desc())\
     .limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         top_books=top_books,
                         action_stats=action_stats,
                         recent_activity=recent_activity,
                         top_users=top_users)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=pagination.items, pagination=pagination)

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Ви не можете деактивувати свій обліковий запис.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'активовано' if user.is_active else 'деактивовано'
    flash(f'Користувача {user.username} {status}.', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action')
    user_filter = request.args.get('user_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Log.query
    
    # Фільтр за дією
    if action_filter:
        query = query.filter_by(action=action_filter)
    
    # Фільтр за користувачем
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    
    # Фільтр за датами
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Log.created_at >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Log.created_at < date_to_obj)
        except ValueError:
            pass
    
    pagination = query.order_by(Log.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # Статистика логів
    total_logs = Log.query.count()
    downloads = Log.query.filter_by(action='download').count()
    logins = Log.query.filter_by(action='login').count()
    
    # Топ користувачів за активністю
    top_users = db.session.query(
        User, func.count(Log.id).label('activity_count')
    ).join(Log).group_by(User.id)\
     .order_by(func.count(Log.id).desc()).limit(5).all()
    
    return render_template('admin/logs.html', 
                         logs=pagination.items, 
                         pagination=pagination,
                         total_logs=total_logs,
                         downloads=downloads,
                         logins=logins,
                         top_users=top_users,
                         action_filter=action_filter,
                         user_filter=user_filter,
                         date_from=date_from,
                         date_to=date_to)

@admin_bp.route('/logs/clear', methods=['POST'])
@login_required
@admin_required
def clear_logs():
    """Очистити старі логи (старші за 90 днів)."""
    days_ago = datetime.utcnow() - timedelta(days=90)
    deleted = Log.query.filter(Log.created_at < days_ago).delete()
    db.session.commit()
    
    flash(f'Видалено {deleted} старих записів логів.', 'success')
    return redirect(url_for('admin.logs'))
