# -*- coding: utf-8 -*-
import logging
import os
from odoo import models
from odoo.addons.sign.models.sign_request import SignRequestItemValue

_logger = logging.getLogger(__name__)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    _logger.warning("Could not import arabic_reshaper or python-bidi.")

# --- Correctly load the bundled font ---
try:
    # Build the path to the font file inside our module's static directory
    font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'src', 'fonts', 'Amiri-Regular.ttf')
    pdfmetrics.registerFont(TTFont('Amiri', font_path))
    _logger.info("Successfully registered bundled Amiri font with reportlab.")
except Exception as e:
    _logger.error(f"FATAL: Could not register bundled Amiri font from path {font_path}. Error: {e}")


# --- MONKEY PATCHING THE CORRECT FUNCTION ---
# Save the original function from Odoo's code.
original_render_on_pdf = SignRequestItemValue._render_on_pdf


def _render_on_pdf_arabic(self, canvas, pdf_location):
    """
    This is our patched function that will replace the original.
    It checks for Arabic text, reshapes it, sets the font, and then calls
    the original Odoo function with the corrected text.
    """
    value_to_render = self.value
    
    if ARABIC_SUPPORT and isinstance(self.value, str):
        is_arabic = any('\u0600' <= char <= '\u06FF' for char in self.value)
        if is_arabic:
            _logger.info(f"Processing Arabic value for PDF rendering: {self.value}")
            # Set the canvas to use our registered Amiri font
            canvas.setFont('Amiri', self.font_size)
            
            # Reshape the text for correct display
            reshaped_text = arabic_reshaper.reshape(self.value)
            bidi_text = get_display(reshaped_text)
            value_to_render = bidi_text
            _logger.info("Font set to Amiri and text reshaped.")
    
    # We need to temporarily set the value on the object before calling the original method
    original_value = self.value
    self.value = value_to_render
    
    # Call the original Odoo function to do the actual drawing
    result = original_render_on_pdf(self, canvas, pdf_location)
    
    # Restore the original value
    self.value = original_value
    return result

# Here, we replace Odoo's function with our new, patched version.
SignRequestItemValue._render_on_pdf = _render_on_pdf_arabic


# We still need this empty class definition for the Odoo framework.
class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'
    pass
