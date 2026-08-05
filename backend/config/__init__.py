"""Django 4.2 + Python 3.14 compatibility patch.

Django's BaseContext.__copy__ uses ``copy(super())`` which raises
"AttributeError: 'super' object has no attribute 'dicts'" on Python 3.14.
This mirrors the upstream fix (Django ticket #35844).
"""

from copy import copy

from django.template.context import BaseContext


def _patched_base_context_copy(self):
    duplicate = BaseContext()
    duplicate.__class__ = self.__class__
    duplicate.__dict__ = copy(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate


if BaseContext.__copy__ is not _patched_base_context_copy:
    BaseContext.__copy__ = _patched_base_context_copy
