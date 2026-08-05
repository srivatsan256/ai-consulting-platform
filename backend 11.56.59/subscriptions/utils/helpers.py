from datetime import datetime
from django.utils import timezone

def calculate_remaining_days(end_date: datetime) -> int:
    if not end_date:
        return 0
    delta = end_date - timezone.now()
    return max(0, delta.days)
