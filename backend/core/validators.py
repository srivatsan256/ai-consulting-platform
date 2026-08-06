import re

from django.core.exceptions import ValidationError


def validate_email(value):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, value):
        raise ValidationError("Invalid email address.")


def validate_phone(value):
    pattern = r"^\+?1?\d{9,15}$"
    if not re.match(pattern, value):
        raise ValidationError("Invalid phone number.")


def validate_url(value):
    pattern = r"^https?://"
    if not re.match(pattern, value):
        raise ValidationError("Invalid URL.")


def validate_max_length(value, max_length):
    if len(value) > max_length:
        raise ValidationError(f"Maximum length is {max_length} characters.")


def validate_min_length(value, min_length):
    if len(value) < min_length:
        raise ValidationError(f"Minimum length is {min_length} characters.")


def validate_no_special_characters(value):
    pattern = r"^[a-zA-Z0-9\s]+$"
    if not re.match(pattern, value):
        raise ValidationError("No special characters allowed.")


def validate_integer_range(value, min_val=None, max_val=None):
    if min_val is not None and value < min_val:
        raise ValidationError(f"Value must be at least {min_val}.")
    if max_val is not None and value > max_val:
        raise ValidationError(f"Value must be at most {max_val}.")


def validate_hex_color(value):
    pattern = r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
    if not re.match(pattern, value):
        raise ValidationError("Value must be a valid hex color (e.g. #2563eb).")
