# nkrane_gt/__init__.py
"""
Nkrane-GT - Enhanced Machine Translation with Terminology Control (Google Translate)
"""

from .translator import NkraneTranslator
from .terminology_manager import TerminologyManager
from .utils import list_available_options, export_terminology, create_sample_terminology
from .language_codes import convert_lang_code, is_google_supported

__version__ = "0.3.0"
__all__ = [
    'NkraneTranslator', 
    'TerminologyManager', 
    'convert_lang_code',
    'is_google_supported',
    'list_available_options', 
    'export_terminology', 
    'create_sample_terminology'
]
