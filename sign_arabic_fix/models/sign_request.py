# -*- coding: utf-8 -*-
import logging
import os
from odoo import models
from odoo.addons.sign.models.sign_request import SignRequestItemValue # Import the class we need to patch

_logger = logging.getLogger(__name__)

# Flag to indicate if Arabic support is fully enabled (libraries and font registered)
_ARABIC_ENABLED = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Attempt to register the font
    # Build the path to the font file inside our module's static directory
    font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'src', 'fonts', 'Amiri-Regular.ttf')
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Amiri', font_path))
        _logger.info("Sign Arabic Fix: Successfully registered bundled Amiri font 'Amiri' with reportlab.")
        _ARABIC_ENABLED = True
    else:
        _logger.error(f"Sign Arabic Fix: FATAL: Amiri font file not found at expected path: {font_path}. Arabic font support disabled.")
        
except ImportError:
    _logger.warning("Sign Arabic Fix: Could not import arabic_reshaper, python-bidi, or reportlab components. Arabic text reshaping will not occur.")
except Exception as e:
    _logger.error(f"Sign Arabic Fix: FATAL: Error during font registration: {e}. Arabic font support disabled.")


# --- MONKEY PATCHING `_draw_text` METHOD on SignRequestItemValue ---
# This is the most direct point where text is put onto the PDF.
if _ARABIC_ENABLED and hasattr(SignRequestItemValue, '_draw_text'):
    _logger.info("Sign Arabic Fix: Attempting to patch SignRequestItemValue._draw_text...")
    original_draw_text = SignRequestItemValue._draw_text

    def _draw_text_arabic_patched(self, canvas, pdf_location):
        """
        Overrides _draw_text to reshape Arabic text and ensure Amiri font is used.
        """
        value_to_process = self.value
        
        if isinstance(value_to_process, str):
            is_arabic = any('\u0600' <= char <= '\u06FF' for char in value_to_process)
            
            if is_arabic:
                _logger.info(f"Sign Arabic Fix: Arabic text detected in _draw_text: '{value_to_process}'")
                
                # Reshape the text for correct display
                reshaped_text = arabic_reshaper.reshape(value_to_process)
                bidi_text = get_display(reshaped_text)
                
                # Store original font and size to restore them later
                original_canvas_font_name = canvas._fontname
                original_canvas_font_size = canvas._fontsize

                # Force the canvas to use our registered Amiri font for this drawing operation
                canvas.setFont('Amiri', self.font_size)
                _logger.info(f"Sign Arabic Fix: Canvas font temporarily set to Amiri ({self.font_size}), text reshaped to: '{bidi_text}'")
                
                # Odoo's original _draw_text method in SignRequestItemValue
                # directly calls canvas.drawString(x, y, self.value).
                # So, we must temporarily modify self.value before calling the original.
                original_self_value = self.value
                self.value = bidi_text # Assign reshaped text
                
                try:
                    # Call the original method to draw the text, which will use the modified self.value
                    original_draw_text(self, canvas, pdf_location)
                finally:
                    # Restore original values after drawing is complete
                    self.value = original_self_value
                    canvas.setFont(original_canvas_font_name, original_canvas_font_size)
                    _logger.info("Sign Arabic Fix: Restored original self.value and canvas font after drawing.")
                return # Drawing handled by our patch
        
        # If not Arabic, or no Arabic text detected, or _ARABIC_ENABLED is False, call the original method directly
        return original_draw_text(self, canvas, pdf_location)

    SignRequestItemValue._draw_text = _draw_text_arabic_patched
    _logger.info("Sign Arabic Fix: Successfully replaced SignRequestItemValue._draw_text with patched version.")
else:
    _logger.warning("Sign Arabic Fix: SignRequestItemValue._draw_text not found or Arabic support not fully enabled. Arabic text fix will not be applied.")


# This empty class definition is still necessary for Odoo to correctly load the file.
# It acts as a valid model extension for the Odoo framework.
class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'
    pass
