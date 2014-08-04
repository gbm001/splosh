"""
This module implements a visualization program, in the style of Daniel Price's
SPLASH, to view RAMSES data files.
"""
__author__ = "Andrew McLeod"
__license__ = "Public Domain"
__version__ = "0.001"
__code_name = "SPLOSH"

__significant_figures = 6

import numpy as np
import matplotlib as mpl

import pymses

import pymses_wrapper as wrapper_functions
from interactive import run

backend_list = []
try:
    from qt4_backend import BackendQT4
    backend_list.append(BackendQT4())
except ImportError:
    pass
try:
    from png_backend import BackendPNG
    backend_list.append(BackendPNG())
except ImportError:
    pass
try:
    from pdf_backend import BackendPDF
    backend_list.append(BackendPDF())
except ImportError:
    pass
try:
    from txt_backend import BackendTXT
    backend_list.append(BackendTXT())
except ImportError:
    pass

print(__code_name + ' loaded')
