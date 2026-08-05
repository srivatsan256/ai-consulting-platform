import uuid
from datetime import timedelta

from django.utils import timezone


def generate_unique_id():
    return str(uuid.uuid4())


def get_previous_month():
    return timezone.now() - timedelta(days=30)


def get_previous_week():
    return timezone.now() - timedelta(days=7)


def get_start_of_day():
    now = timezone.now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day():
    now = timezone.now()
    return now.replace(hour=23, minute=59, second=59, microsecond=999999)


def format_currency(amount, currency="USD"):
    return f"{currency} {amount:,.2f}"


def truncate_text(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def mask_email(email):
    username, domain = email.split("@")
    masked_username = username[0] + "***" + username[-1] if len(username) > 1 else "***"
    return f"{masked_username}@{domain}"


def mask_phone(phone):
    if len(phone) < 4:
        return phone
    return "***" + phone[-4:]


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)
