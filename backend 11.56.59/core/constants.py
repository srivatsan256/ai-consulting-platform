from django.db.models import TextChoices


class StatusChoices(TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    IN_PROGRESS = "in_progress", "In Progress"
    ON_HOLD = "on_hold", "On Hold"
    ARCHIVED = "archived", "Archived"


class PriorityChoices(TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class RoleChoices(TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    MEMBER = "member", "Member"
    VIEWER = "viewer", "Viewer"


class SortOrderChoices(TextChoices):
    ASC = "asc", "Ascending"
    DESC = "desc", "Descending"


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

MAX_CHAR_LENGTH = 255
MAX_TEXT_LENGTH = 10000

API_VERSION = "v1"
