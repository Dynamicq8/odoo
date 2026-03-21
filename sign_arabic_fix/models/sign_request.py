# -*- coding: utf-8 -*-
import logging
import os
from odoo import models
from odoo.addons.sign.models.sign_request import SignRequestItemValue # Import the class we need to patch

_logger = logging.getLogger(__name__)

# Flag to indicate if Arabic support is fully enabled (libraries and font registered)
ARABIC_SUPPORT = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    ARABIC_SUPPORT = True
except ImportError:
    _logger.warning("Could not import arabic_reshaper or python-bidi. Arabic text reshaping will not occur.")

# --- Correctly load the bundled font and register it ---
if ARABIC_SUPPORT: # Only attempt if Arabic libraries loaded
    try:
        # Build the path to the font file inside our module's static directory
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'src', 'fonts', 'Amiri-Regular.ttf')
        
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Amiri', font_path))
            _logger.info("Successfully registered bundled Amiri font 'Amiri' with reportlab.")
        else:
            _logger.error(f"FATAL: Amiri font file not found at expected path: {font_path}. Arabic font support disabled.")
            ARABIC_SUPPORT = False # Disable if font file not found
            
    except Exception as e:
        _logger.error(f"FATAL: Could not register bundled Amiri font. Error: {e}. Arabic font support disabled.")
        ARABIC_SUPPORT = False # Disable if font registration fails


# --- MONKEY PATCHING `_get_resampled_value` (More Robust) ---

# Check if _get_resampled_value exists on SignRequestItemValue before patching
if hasattr(SignRequestItemValue, '_get_resampled_value'):
    original_get_resampled_value = SignRequestItemValue._get_resampled_value

    def _get_resampled_value_arabic(self):
        """
        Overrides _get_resampled_value to reshape Arabic text before it's rendered.
        Also attempts to set the font_name dynamically if Arabic is detected.
        """
        # Get the value first using the original Odoo method
        value = original_get_resampled_value(self)
        
        if ARABIC_SUPPORT and isinstance(value, str):
            is_arabic = any('\u0600' <= char <= '\u06FF' for char in value)
            if is_arabic:
                _logger.info(f"Reshaping Arabic value: '{value}' for Sign app.")
                reshaped_text = arabic_reshaper.reshape(value)
                bidi_text = get_display(reshaped_text)
                _logger.info(f"Reshaped to: '{bidi_text}'")
                
                # IMPORTANT: Attempt to dynamically set font_name on the instance
                # This is a softer approach than patching the property itself,
                # as it won't crash the module if 'font_name' isn't a property.
                if hasattr(self, 'font_name') and self.font_name != 'Amiri':
                    self.font_name = 'Amiri'
                    _logger.info(f"Dynamically set font_name to 'Amiri' for item with value '{value}'.")
                
                return bidi_text
        
        return value

    # Replace the original '_get_resampled_value' method with our new patched version
    SignRequestItemValue._get_resampled_value = _get_resampled_value_arabic
    _logger.info("Successfully patched SignRequestItemValue._get_resampled_value.")
else:
    _logger.warning("SignRequestItemValue._get_resampled_value not found. Arabic text reshaping will not occur.")


# We still need this empty class definition for the Odoo framework.
# This ensures Odoo loads the file as a valid model extension.
class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'
    pass
