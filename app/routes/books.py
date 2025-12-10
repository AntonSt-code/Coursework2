from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app import db
from app.models import Book, File, Log, BookAuthor, BookGenre, Author, Genre
from app.forms import BookForm
from app.utils.decorators import admin_required

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def catalog():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre')
    language = request.args.get('language')
    sort_by = request.args.get('sort', 'recent')
    
    query = Book.query.filter_by(is_active=True)
    
    # Фільтри
    if genre_id:
        query = query.join(Book.book_genres).filter_by(genre_id=genre_id)
    if language:
        query = query.filter_by(language=language)
    
    # Сортування
    if sort_by == 'rating':
        # TODO: сортування за рейтингом
        pass
    elif sort_by == 'title':
        query = query.order_by(Book.title)
    else:  # recent
        query = query.order_by(Book.created_at.desc())
    
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['BOOKS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('books/catalog.html',
                         books=pagination.items,
                         pagination=pagination)

@books_bp.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.is_active:
        flash('Книга недоступна.', 'warning')
        return redirect(url_for('books.catalog'))
    
    # Логування перегляду книги
    if current_user.is_authenticated:
        log = Log(
            user_id=current_user.id,
            book_id=book_id,
            action='view',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
    
    return render_template('books/detail.html', book=book)

@books_bp.route('/<int:book_id>/download/<int:file_id>')
@login_required
def download(book_id, file_id):
    book = Book.query.get_or_404(book_id)
    file = File.query.get_or_404(file_id)
    
    if file.book_id != book_id or not file.is_active:
        flash('Файл недоступний.', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))
    
    # Правильний повний шлях до файлу
    file_path = os.path.join(current_app.root_path, 'static', file.file_path.replace('/', os.sep))
    
    if not os.path.exists(file_path):
        flash('Файл не знайдено на сервері.', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))
    
    # Логування
    log = Log(
        user_id=current_user.id,
        book_id=book_id,
        file_id=file_id,
        action='download',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(file_path, as_attachment=True)

@books_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = BookForm()
    
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            original_title=form.original_title.data or None,
            description=form.description.data,
            isbn=form.isbn.data or None,  # Перетворюємо пустий рядок на None
            language=form.language.data,
            publisher=form.publisher.data or None,
            publication_year=form.publication_year.data
        )
        
        # Обробка завантаження обкладинки
        if form.cover_image.data:
            file = form.cover_image.data
            filename = secure_filename(file.filename)
            
            covers_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
            os.makedirs(covers_folder, exist_ok=True)
            
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file_path = os.path.join(covers_folder, unique_filename)
            file.save(file_path)
            
            book.cover_image_path = f'uploads/covers/{unique_filename}'
        
        db.session.add(book)
        db.session.flush()  # Отримати ID книги
        
        # Додати авторів
        for author_id in form.authors.data:
            book_author = BookAuthor(book_id=book.id, author_id=author_id)
            db.session.add(book_author)
        
        # Додати жанри
        for genre_id in form.genres.data:
            book_genre = BookGenre(book_id=book.id, genre_id=genre_id)
            db.session.add(book_genre)
        
        db.session.commit()
        
        # Логування створення книги
        log = Log(
            user_id=current_user.id,
            book_id=book.id,
            action='create_book',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Книга успішно додана!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/create.html', form=form)

@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    
    # Попередньо заповнити поточних авторів та жанри
    if request.method == 'GET':
        form.authors.data = [ba.author_id for ba in book.book_authors.all()]
        form.genres.data = [bg.genre_id for bg in book.book_genres.all()]
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.original_title = form.original_title.data or None
        book.description = form.description.data
        book.isbn = form.isbn.data or None  # Перетворюємо пустий рядок на None
        book.language = form.language.data
        book.publisher = form.publisher.data or None
        book.publication_year = form.publication_year.data
        
        # Обробка нової обкладинки
        if form.cover_image.data:
            file = form.cover_image.data
            filename = secure_filename(file.filename)
            
            covers_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
            os.makedirs(covers_folder, exist_ok=True)
            
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file_path = os.path.join(covers_folder, unique_filename)
            file.save(file_path)
            
            if book.cover_image_path:
                old_path = os.path.join(current_app.root_path, 'static', book.cover_image_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            book.cover_image_path = f'uploads/covers/{unique_filename}'
        
        # Оновити авторів
        BookAuthor.query.filter_by(book_id=book.id).delete()
        for author_id in form.authors.data:
            book_author = BookAuthor(book_id=book.id, author_id=author_id)
            db.session.add(book_author)
        
        # Оновити жанри
        BookGenre.query.filter_by(book_id=book.id).delete()
        for genre_id in form.genres.data:
            book_genre = BookGenre(book_id=book.id, genre_id=genre_id)
            db.session.add(book_genre)
        
        db.session.commit()
        
        # Логування редагування
        log = Log(
            user_id=current_user.id,
            book_id=book.id,
            action='edit_book',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Книга оновлена!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/edit.html', form=form, book=book)

@books_bp.route('/<int:book_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    book.is_active = False
    
    # Логування видалення
    log = Log(
        user_id=current_user.id,
        book_id=book.id,
        action='delete_book',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Книга видалена.', 'info')
    return redirect(url_for('books.catalog'))

@books_bp.route('/<int:book_id>/upload-files', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_files(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        files = request.files.getlist('files')
        
        if not files:
            flash('Файли не вибрано.', 'warning')
            return redirect(request.url)
        
        # Правильний шлях до папки uploads/books
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'books')
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_format = filename.rsplit('.', 1)[1].lower()
                
                if file_format not in current_app.config['ALLOWED_EXTENSIONS']:
                    flash(f'Формат {file_format} не підтримується.', 'danger')
                    continue
                
                # Унікальне ім'я файлу
                unique_filename = f"{book.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(upload_folder, unique_filename)
                
                file.save(file_path)
                
                # Зберегти в БД відносний шлях
                db_file = File(
                    book_id=book.id,
                    file_path=os.path.join('uploads', 'books', unique_filename).replace('\\', '/'),
                    format=file_format,
                    file_size=os.path.getsize(file_path),
                    is_active=True
                )
                db.session.add(db_file)
        
        db.session.commit()
        flash('Файли успішно завантажено!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))
    
    return render_template('books/upload_files.html', book=book)

@books_bp.route('/files/<int:file_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    book_id = file.book_id
    
    # Видалити фізичний файл
    file_path = os.path.join(current_app.root_path, 'static', file.file_path.replace('/', os.sep))
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            flash(f'Помилка при видаленні файлу: {e}', 'danger')
    
    db.session.delete(file)
    db.session.commit()
    
    flash('Файл видалено.', 'info')
    return redirect(url_for('books.upload_files', book_id=book_id))
