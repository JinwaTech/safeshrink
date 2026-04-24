# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from format_to_ssd import MARKITDOWN_AVAILABLE, is_ssd_convertible
print(f'MARKITDOWN_AVAILABLE: {MARKITDOWN_AVAILABLE}')
print(f'PDF convertible: {is_ssd_convertible("test.pdf")}')
