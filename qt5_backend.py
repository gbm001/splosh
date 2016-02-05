"""
This submodule implements the QT4 interactive backend.
"""

from __future__ import print_function
import numpy as np
from mpl_base_backend import BackendMPL
from matplotlib import rcParams

# We only support PyQt5 at present
qt_library = 'pyqt5'
#if 'backend.qt4' in rcParams:
#    # We need to match what matplotlib is using
#    qt_library = rcParams['backend.qt4'].lower()
#    if qt_library == 'pyqt4':      # should be PyQt4 in rcParams
#        pass
#    elif qt_library == 'pyside':   # shoule be PySide in rcParams
#        pass
#    else:
#        raise ImportError('Unknown matplotlib setting of backend.qt4!')
#else:
#    # best guess if we don't have backend.qt4? But probably PyQt4
#    try:
#        import PyQt4
#        qt_library = 'pyqt4'
#    except ImportError:
#        import PySide
#        qt_library = 'pyside'

if qt_library == 'pyqt5':
    print('Using PyQt5')
    from PyQt5 import QtCore, QtWidgets
elif qt_library == 'pyside2':
    print('Using PySide2')
    raise NotImplementedError('PySide2 not supported')
    #from PySide import QtCore, QtGui

class BackendQT5(BackendMPL):
    """
    Backend for interactive QT5 use
    """
    
    def __init__(self):
        BackendMPL.__init__(self)
        self.name = '\QT5'
        self.long_name = 'QT5 backend'
        self.interactive = True
        from matplotlib.backends.backend_qt5agg \
            import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        
        self.FigureCanvas = FigureCanvas
        self.Figure = Figure
        
        self.max_auto_resolution = 1024
        
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication([])
        self.figure_exists = False
        self.window_active = False
        
        self.plot_args = {}
        
        self.key_press_event = None
        self.zoom_main_event = None
        self.zoom_cbar_event = None
        
        self.main_axes = None
        self.main_zoom = None
        self.cbar_axes = None
        self.cbar_zoom = None
        
        self.zoom_factor = 1
        self.zoom_mult = 1
    
    def on_exit(self):
        """
        Function to tidy up backend on exit
        """
        #self.app.quit()
        self.app.processEvents()
        self.app.quit()
        self.app.processEvents()
        
    def interactive_loop(self):
        """
        The QT interactive loop. Process events until the window is closed.
        """
        while self.window_active:
            self.app.processEvents()
    
    def init_figure(self):
        """
        Create the figure
        """
        self.fig = self.Figure()
        self.canvas = self.FigureCanvas(self.fig)
        self.fig.canvas.mpl_connect('key_press_event', self.key_press_pass)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()
        
        self.win = QtWidgets.QMainWindow()
        self.win.closeEvent = self.close_canvas
        self.win.setCentralWidget(self.canvas)
        self.win.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def key_press_pass(self, event):
        """
        Pass backend and keys to 'key_press_event' function
        """
        axis_name, x, y = self.decode_location_event(event)
        self.app.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.key_press_event(self, event.key, axis_name, x, y)
        self.app.restoreOverrideCursor()

    def onselect_main(self, eclick, erelease):
        """
        Called when main zoom RectangleSelector is completed
        """
        xlim = (min(eclick.xdata, erelease.xdata),
                max(eclick.xdata, erelease.xdata))
        ylim = (min(eclick.ydata, erelease.ydata),
                max(eclick.ydata, erelease.ydata))
        self.zoom_main_event(self, xlim, ylim)

    def onselect_cbar(self, vmin, vmax):
        """
        Called when cbar zoom SpanSelector is completed
        """
        crange = self.current_clim[1] - self.current_clim[0]
        cmin = crange * vmin + self.current_clim[0]
        cmax = crange * vmax + self.current_clim[0]
        clim = (cmin, cmax)
        self.zoom_cbar_event(self, clim)

    def update_plot(self):
        """
        Data has been updated; replot figure
        """
        self.fig.clf()
        self.plot_data()
        
    def close_plot(self, *args):
        """
        Close the plot (just call close_canvas)
        """
        self.close_canvas()
    
    def close_canvas(self, event=None):
        """
        Close the output canvas
        """
        if event:
            event.accept()
            self.win.close()
        else:
            self.win.close()
        self.window_active = False

    def output_canvas(self):
        """
        Output canvas
        """
        from matplotlib.widgets import SpanSelector, RectangleSelector
        
        rectprops = dict(edgecolor = 'black', linewidth=1.5, fill=False)
        self.main_zoom = RectangleSelector(
            self.main_axes, self.onselect_main, button=1, drawtype='box',
            minspanx=2, minspany=2, spancoords='pixels', rectprops=rectprops)
        if (self.plot_options['plot_type'] == 'render' and
                self.cbar_axes is not None):
            self.cbar_zoom = SpanSelector(
                self.cbar_axes, self.onselect_cbar, direction=self.cbar_dir,
                minspan=0.02)
        else:
            self.cbar_zoom = None
        
        if self.window_active:
            self.canvas.draw()
            self.win.raise_()
        else:
            self.win.show()
            self.win.raise_()
            self.window_active = True
            self.interactive_loop()
    
    
    
    
    
    
    
    
    
    
