import logging

from django.conf import settings


def get_logger(name):
    return logging.getLogger(name)


def log_info(message, extra=None):
    logger = get_logger("core")
    logger.info(message, extra=extra or {})


def log_error(message, exc_info=False, extra=None):
    logger = get_logger("core")
    logger.error(message, exc_info=exc_info, extra=extra or {})


def log_warning(message, extra=None):
    logger = get_logger("core")
    logger.warning(message, extra=extra or {})


def log_debug(message, extra=None):
    logger = get_logger("core")
    logger.debug(message, extra=extra or {})


def log_security(message, extra=None):
    logger = get_logger("security")
    logger.warning(message, extra=extra or {})


def log_audit(message, user=None, action=None, extra=None):
    logger = get_logger("audit")
    log_data = extra or {}
    if user:
        log_data["user_id"] = user.pk
        log_data["user_email"] = user.email
    if action:
        log_data["action"] = action
    logger.info(message, extra=log_data)


def log_performance(message, duration=None, extra=None):
    logger = get_logger("performance")
    log_data = extra or {}
    if duration:
        log_data["duration_ms"] = duration
    logger.info(message, extra=log_data)
