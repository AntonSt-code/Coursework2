from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User, Log
from app.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Логування реєстрації
        log = Log(
            user_id=user.id,
            action='register',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Пошук по username або email
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Ваш обліковий запис деактивовано.', 'danger')
                return redirect(url_for('auth.login'))
            
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            
            # Логування входу
            log = Log(
                user_id=user.id,
                action='login',
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            db.session.add(log)
            db.session.commit()
            
            next_page = request.args.get('next')
            flash(f'Ласкаво просимо, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Невірний логін або пароль.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        # Логування виходу
        log = Log(
            user_id=current_user.id,
            action='logout',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
    
    logout_user()
    flash('Ви успішно вийшли з системи.', 'info')
    return redirect(url_for('main.index'))
