"""Public scanner module.

The complete scanner implementation lives in ``Scanner/OMR_scanner.py``.
This module exposes the same scanning API from the services package while
keeping one maintained implementation.
"""

if __package__:
    from .Scanner.OMR_scanner import *
else:
    from Scanner.OMR_scanner import *
