from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, BooleanField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from app.models import User, Author, Genre

class RegistrationForm(FlaskForm):
    username = StringField('Логін', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Length(min=3, max=80, message='Логін повинен бути від 3 до 80 символів')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Email(message='Невірний формат email')
    ])
    first_name = StringField('Ім\'я', validators=[Length(max=100)])
    last_name = StringField('Прізвище', validators=[Length(max=100)])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Length(min=6, message='Пароль повинен містити мінімум 6 символів')
    ])
    confirm_password = PasswordField('Підтвердіть пароль', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        EqualTo('password', message='Паролі не співпадають')
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Цей логін вже зайнятий. Оберіть інший.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Цей email вже зареєстрований.')

class LoginForm(FlaskForm):
    username = StringField('Логін або Email', validators=[
        DataRequired(message='Це поле обов\'язкове')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Це поле обов\'язкове')
    ])
    remember_me = BooleanField('Запам\'ятати мене')

class BookForm(FlaskForm):
    title = StringField('Назва книги', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Length(max=255)
    ])
    original_title = StringField('Оригінальна назва', validators=[Length(max=255)])
    description = TextAreaField('Опис')
    isbn = StringField('ISBN', validators=[Length(max=20)])
    language = SelectField('Мова', choices=[
        ('uk', 'Українська'),
        ('en', 'English'),
        ('ru', 'Русский'),
        ('de', 'Deutsch'),
        ('fr', 'Français')
    ])
    publisher = StringField('Видавництво', validators=[Length(max=200)])
    publication_year = IntegerField('Рік публікації', validators=[
        Optional(),
        NumberRange(min=1000, max=2100, message='Невірний рік')
    ])
    cover_image = FileField('Обкладинка', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Тільки зображення!')
    ])
    authors = SelectMultipleField('Автори', coerce=int)
    genres = SelectMultipleField('Жанри', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        # Динамічно завантажуємо авторів та жанри
        self.authors.choices = [(a.id, a.full_name) for a in Author.query.order_by(Author.last_name).all()]
        self.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]

class ReviewForm(FlaskForm):
    rating = SelectField('Рейтинг', choices=[
        ('5', '★★★★★ (5)'),
        ('4', '★★★★☆ (4)'),
        ('3', '★★★☆☆ (3)'),
        ('2', '★★☆☆☆ (2)'),
        ('1', '★☆☆☆☆ (1)')
    ], validators=[DataRequired(message='Оберіть рейтинг')])
    title = StringField('Заголовок відгуку', validators=[Length(max=200)])
    review_text = TextAreaField('Ваш відгук', validators=[
        DataRequired(message='Напишіть відгук'),
        Length(min=10, message='Відгук повинен містити мінімум 10 символів')
    ])

class AuthorForm(FlaskForm):
    first_name = StringField('Ім\'я', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Length(max=100)
    ])
    last_name = StringField('Прізвище', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Length(max=100)
    ])
    middle_name = StringField('По батькові', validators=[Length(max=100)])
    bio = TextAreaField('Біографія')
    birth_date = DateField('Дата народження', validators=[Optional()], format='%Y-%m-%d')
    death_date = DateField('Дата смерті', validators=[Optional()], format='%Y-%m-%d')
    country = StringField('Країна', validators=[Length(max=100)])

class SearchForm(FlaskForm):
    query = StringField('Пошук', validators=[DataRequired()])
    search_type = SelectField('Де шукати', choices=[
        ('all', 'Всюди'),
        ('title', 'Назва книги'),
        ('author', 'Автор'),
        ('isbn', 'ISBN')
    ])

class GenreForm(FlaskForm):
    name = StringField('Назва жанру', validators=[
        DataRequired(message='Це поле обов\'язкове'),
        Length(min=2, max=100, message='Назва повинна бути від 2 до 100 символів')
    ])
    description = TextAreaField('Опис жанру', validators=[
        Optional(),
        Length(max=500, message='Опис не повинен перевищувати 500 символів')
    ])
    
    def validate_name(self, name):
        # Перевірка унікальності назви жанру
        from app.models import Genre
        genre = Genre.query.filter_by(name=name.data).first()
        if genre:
            raise ValidationError('Жанр з такою назвою вже існує.')
