"""
This submodule implements the PNG backend.
"""

from __future__ import print_function
import numpy as np
from mpl_base_backend import BackendMPL

class BackendPDF(BackendMPL):
    """
    Backend for writing to PNG files
    """
    
    def __init__(self):
        BackendMPL.__init__(self)
        self.name = '\PDF'
        self.long_name = 'PDF backend'
        self.interactive = False
        from matplotlib.backends.backend_pdf \
            import FigureCanvasPdf as FigureCanvas
        from matplotlib.figure import Figure
        
        self.FigureCanvas = FigureCanvas
        self.Figure = Figure
        
        self.max_auto_resolution = 256
        self.output_filename = ''
    
    def init_figure(self):
        """
        Create the figure
        """
        self.fig = self.Figure()
        self.canvas = self.FigureCanvas(self.fig)
    
    def set_output_filename(self, filename):
        """
        Set the output filename
        """
        self.output_filename = filename
        
    def output_canvas(self):
        """
        Output canvas
        """
        print('Writing to file {}.pdf...'.format(self.output_filename))
        self.canvas.print_figure(self.output_filename)
    
    
    
    
    
    
    
    
    
    
    
    
    