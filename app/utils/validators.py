"""Custom validators for forms."""
from wtforms.validators import ValidationError
import re

def validate_isbn(form, field):
    """Validate ISBN-10 or ISBN-13 format."""
    if field.data:
        isbn = field.data.replace('-', '').replace(' ', '')
        if not (len(isbn) == 10 or len(isbn) == 13):
            raise ValidationError('ISBN повинен містити 10 або 13 цифр.')
        if not isbn.isdigit():
            raise ValidationError('ISBN повинен містити тільки цифри.')

def validate_year(form, field):
    """Validate publication year."""
    if field.data:
        if field.data < 1000 or field.data > 2100:
            raise ValidationError('Невірний рік публікації.')
