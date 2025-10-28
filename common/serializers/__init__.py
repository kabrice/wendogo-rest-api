# common/serializers/__init__.py
"""
Module de sérialisation centralisé avec support i18n
"""

from .base_serializer import BaseSerializer
from .program_serializer import ProgramSerializer
from .school_serializer import SchoolSerializer

__all__ = [
    'BaseSerializer',
    'ProgramSerializer',
    'SchoolSerializer',
]
