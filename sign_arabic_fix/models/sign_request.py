# -*- coding: utf-8 -*-
import logging
import os

from odoo import models

_logger = logging.getLogger(__name__)

# Flag to indicate if Arabic support is fully enabled
_ARABIC_ENABLED = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas as reportlab_canvas

    # Path to font inside your module
    font_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'static', 'src', 'fonts', 'Amiri-Regular.ttf'
    )

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Amiri', font_path))
        _logger.info("Arabic Fix: Amiri font registered successfully.")
        _ARABIC_ENABLED = True
    else:
        _logger.error(f"Arabic Fix: Font NOT found at: {font_path}")

except ImportError:
    _logger.warning("Arabic Fix: Missing arabic_reshaper or bidi or reportlab.")
except Exception as e:
    _logger.error(f"Arabic Fix: Error during setup: {e}")


# ================================
# 🔥 PATCH REPORTLAB DIRECTLY FOR RTL ARABIC
# ================================
if _ARABIC_ENABLED:
    try:
        original_drawString = reportlab_canvas.Canvas.drawString
        original_drawRightString = reportlab_canvas.Canvas.drawRightString
        original_drawCentredString = reportlab_canvas.Canvas.drawCentredString

        def _process_arabic_text(text):
            if not isinstance(text, str):
                return text, False

            # Detect Arabic letters
            is_arabic = any('\u0600' <= c <= '\u06FF' for c in text)

            if not is_arabic:
                return text, False

            # Reshape letters and reorder for RTL
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text, True

        # Patch left-aligned drawString
        def drawString_patched(self, x, y, text, *args, **kwargs):
            text, is_arabic = _process_arabic_text(text)

            if is_arabic:
                self.setFont('Amiri', self._fontsize or 12)
                # Draw Arabic RTL text aligned to the right
                return original_drawRightString(self, x, y, text, *args, **kwargs)

            return original_drawString(self, x, y, text, *args, **kwargs)

        # Patch right-aligned drawRightString (just apply reshaping)
        def drawRightString_patched(self, x, y, text, *args, **kwargs):
            text, is_arabic = _process_arabic_text(text)

            if is_arabic:
                self.setFont('Amiri', self._fontsize or 12)

            return original_drawRightString(self, x, y, text, *args, **kwargs)

        # Patch centered text
        def drawCentredString_patched(self, x, y, text, *args, **kwargs):
            text, is_arabic = _process_arabic_text(text)

            if is_arabic:
                self.setFont('Amiri', self._fontsize or 12)

            return original_drawCentredString(self, x, y, text, *args, **kwargs)

        # Apply the patches
        reportlab_canvas.Canvas.drawString = drawString_patched
        reportlab_canvas.Canvas.drawRightString = drawRightString_patched
        reportlab_canvas.Canvas.drawCentredString = drawCentredString_patched

        _logger.info("Arabic Fix: ReportLab canvas patched successfully (RTL).")

    except Exception as e:
        _logger.error(f"Arabic Fix: Failed to patch canvas: {e}")

else:
    _logger.warning("Arabic Fix: Arabic support NOT enabled, skipping patch.")


# Required dummy model for Odoo
class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'
