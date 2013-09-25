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

from png_backend import BackendPNG
from pdf_backend import BackendPDF
from qt4_backend import BackendQT4
from txt_backend import BackendTXT
backend_list = []
backend_list.append(BackendQT4())
backend_list.append(BackendPNG())
backend_list.append(BackendPDF())
backend_list.append(BackendTXT())

print(__code_name + ' loaded')
