#-*- coding: utf-8 -*-

__author__ = "Toshiyuki Nishiyama"
__version__ = "0.1"

try:
    __FX_SETUP__
except NameError:
    __FX_SETUP__ = False

if __FX_SETUP__:
    import sys as _sys
    _sys.stderr.write('Running from FX source directory.\n')
    del _sys
else:
    from . import backtest
    from . import core
    from . import SQLDBclass
    from . import MLClass
