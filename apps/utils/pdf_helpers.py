import os
import arabic_reshaper
from bidi.algorithm import get_display


def ar(text):
    return get_display(arabic_reshaper.reshape(str(text)))


def get_arabic_font():
    bundled_regular = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'fonts', 'Amiri-Regular.ttf')
    bundled_bold = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'fonts', 'Amiri-Bold.ttf')

    if os.path.exists(bundled_regular):
        return (bundled_regular, bundled_bold if os.path.exists(bundled_bold) else bundled_regular)

    win_fonts = [
        ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
        ('C:/Windows/Fonts/arabtype.ttf', 'C:/Windows/Fonts/arabtype.ttf'),
        ('C:/Windows/Fonts/trado.ttf', 'C:/Windows/Fonts/trado.ttf'),
    ]
    for regular, bold in win_fonts:
        if os.path.exists(regular):
            return (regular, bold)
    return (None, None)
