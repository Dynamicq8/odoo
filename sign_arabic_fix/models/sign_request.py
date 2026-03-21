# -*- coding: utf-8 -*-
import logging
from odoo import models
from odoo.addons.sign.models.sign_request import SignRequestItemValue

_logger = logging.getLogger(__name__)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Register the Amiri font that we installed via apt_packages.txt
    # The path to system fonts in Debian/Ubuntu is usually here.
    try:
        pdfmetrics.registerFont(TTFont('Amiri', '/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf'))
        _logger.info("Successfully registered Amiri font with reportlab.")
    except Exception as e:
        _logger.error(f"Could not register Amiri font. Path might be wrong. Error: {e}")

    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    _logger.warning("Could not import arabic_reshaper, python-bidi, or reportlab components.")


# This is the core class Odoo uses to represent a value before printing.
# We will inherit it and change its behavior.
class SignRequestItemValue(SignRequestItemValue):

    def _get_cairo_font_name_and_size(self, font_name='Helvetica', font_size=12, box_height=20):
        """
        Force the font to be Amiri if Arabic is detected. This is a key
        function for rendering.
        """
        if ARABIC_SUPPORT and isinstance(self.value, str):
            is_arabic = any('\u0600' <= char <= '\u06FF' for char in self.value)
            if is_arabic:
                _logger.info("Arabic detected, forcing font to Amiri.")
                # Return 'Amiri' instead of the default font.
                return 'Amiri', min(font_size, box_height) * 0.8
        
        # If not Arabic, use the original Odoo function.
        return super()._get_cairo_font_name_and_size(font_name, font_size, box_height)

    def _get_resampled_value(self):
        """
        This is the final function that gets the text value. We will
        reshape the text here.
        """
        value = super()._get_resampled_value()
        
        if ARABIC_SUPPORT and isinstance(value, str):
            is_arabic = any('\u0600' <= char <= '\u06FF' for char in value)
            if is_arabic:
                _logger.info(f"Reshaping Arabic value: {value}")
                reshaped_text = arabic_reshaper.reshape(value)
                bidi_text = get_display(reshaped_text)
                return bidi_text
        
        return value
