"""
This submodule implements the base class for matplotlib backends.
"""

from __future__ import print_function
import numpy as np
from matplotlib.ticker import FuncFormatter
    
def mathtexify(text):
    space_str = r'}$ $\mathdefault{'
    return r'$\mathdefault{' + text.replace(' ', space_str) + r'}$'

def ten_to_ticker_func(x, pos):
    from . import text_helpers
    'The two args are the value and tick position'
    return str(text_helpers.round_to_n(10**x,2))

ten_to_formatter = FuncFormatter(ten_to_ticker_func)

class BackendMPL():
    """
    Base class for matplotlib backends
    """
    def __init__(self):
        self.step = None
        self.data_list = None
        self.draw_limits = None
        self.plot_transforms = None
        self.plot_options = None
    
    def on_exit(self):
        """
        Function to tidy up backend on exit
        """
        pass
    
    def decode_location_event(self, event):
        """
        Function to decode matplotlib location event
        """
        inaxes = event.inaxes
        x_axis = self.main_axes.get_xaxis()
        x_axis_label = x_axis.get_label()
        y_axis = self.main_axes.get_yaxis()
        y_axis_label = y_axis.get_label()
        if event.x is None or event.y is None:
            axes_name = ''
        elif x_axis.contains(event)[0]:
            axes_name = 'x-axis'
        elif y_axis.contains(event)[0]:
            axes_name = 'y-axis'
        elif x_axis_label.contains(event)[0]:
            axes_name = 'x-axis'
        elif y_axis_label.contains(event)[0]:
            axes_name = 'y-axis'
        elif inaxes is self.main_axes:
            axes_name = 'main_axes'
        elif inaxes is self.cbar_axes:
            axes_name = 'cbar'
        else:
            axes_name = ''
        return axes_name, event.xdata, event.ydata
    
    def plot_data(self):
        """
        Take a data_array and plot on a graph
        """
        
        # Plot limits
        xmin, xmax = self.draw_limits['x_axis']
        ymin, ymax = self.draw_limits['y_axis']
        clim = self.draw_limits['render']
        
        # Transforms
        x_transform = self.plot_transforms['x_transform']
        y_transform = self.plot_transforms['y_transform']
        hist_transform = self.plot_transforms['hist_transform']
        render_transform = self.plot_transforms['render_transform']
        
        limits = self.draw_limits['xy_limits']
        self.current_xylimits = limits
        
        # Create figure
        ax = self.fig.add_subplot(111)
        self.main_axes = ax
        res = self.plot_options['resolution']
        cmap = None
        if 'cmap' in self.plot_options:
            cmap = self.plot_options['cmap']
        
        plot_type = self.plot_options['plot_type']
        
        if plot_type == 'time':
            x = self.data_list[0][:, 0]
            y = self.data_list[0][:, 1]
            time_plot = ax.plot(x, y, 'r')
            ax.set_xlim(limits[0])
            ax.set_ylim(limits[1])
            clim = None
        
        elif plot_type == 'hist2d':
            
            xedges, yedges, counts, min_max_data = self.data_list
            
            img = ax.pcolorfast(xedges, yedges, counts.T, cmap=cmap)
            ax.set_xlim(xedges[0], xedges[-1])
            ax.set_ylim(yedges[0], yedges[-1])
            
            clim = list(img.get_clim())
            if clim[0] == clim[1]:
                clim[0] = 0.0
            img.set_clim(clim)
        
        elif plot_type == 'render':
            imshow_limits = (limits[0][0], limits[0][1],
                             limits[1][0], limits[1][1])
            if self.plot_options['aspect'] == 'equal':
                imshow_aspect = 'equal'
            elif self.plot_options['aspect'] == 'square_plot':
                data_shape = self.data_list[0].shape
                imshow_aspect = float(data_shape[1]) / float(data_shape[0])
            else:
                imshow_aspect = self.plot_options['aspect']
            
            img = ax.imshow(self.data_list[0], interpolation='none',
                            origin='lower', aspect=imshow_aspect, cmap=cmap,
                            extent=imshow_limits)
            
            img.set_clim(clim)
        
        else:
            # single axis plots
            data_axis = self.plot_options['data_axis']
            if data_axis != 'x':
                qx_transform = self.plot_transforms['qx_transform']
                if qx_transform is not None and qx_transform[0] is np.log10:
                    ax.get_xaxis().set_major_formatter(ten_to_formatter)
            else:
                qx_transform = None
            
            if data_axis != 'y':
                qy_transform = self.plot_transforms['qy_transform']
                if qy_transform is not None and qy_transform[0] is np.log10:
                    ax.get_yaxis().set_major_formatter(ten_to_formatter)
            else:
                qy_transform = None
            
            if plot_type == 'hist1d':
                counts, bins, extra_info = self.data_list
                
                if qy_transform is not None:
                    counts = qy_transform[0](counts)
                
                npoints = 2 * len(bins)
                x = np.zeros(npoints)
                y = np.zeros(npoints)
                
                x[0::2], x[1::2] = bins, bins
                y[0] = 0.0
                i = 1
                for j, count in enumerate(counts):
                    y[i] = count
                    y[i+1] = count
                    i += 2
                y[-1] = 0.0
                
                single_axis_plot = ax.plot(x, y, 'k')
                
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                self.current_xylimits = [xlim, ylim]
                clim = None
            
            elif plot_type == 'power_spectrum':
                
                x = self.data_list[0]
                y = self.data_list[1]
                extra_info = self.data_list[2]
                
                if qx_transform is not None:
                    x = qx_transform[0](x)
                if qy_transform is not None:
                    y = qy_transform[0](y)
                
                single_axis_plot = ax.plot(x, y, 'k', label='')
                
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                self.current_xylimits = [xlim, ylim]
                
                x_points = np.linspace(xlim[0], xlim[1], res)
                if qx_transform is not None:
                    x_untransformed = qx_transform[1](x_points).astype(np.float_)
                
                legend = False
                extra_plots = []
                for extra_func in extra_info['extra_funcs']:
                    func, label = extra_func
                    label = mathtexify(label)
                    if label != '':
                        legend = True
                    if qx_transform is None:
                        y_points = func(x_points)
                    else:
                        y_points = func(x_untransformed)
                    if qy_transform is not None:
                        y_points = qy_transform[0](y_points)
                    extra_plot = ax.plot(x_points, y_points,
                                        label=label, scaley=False)
                    extra_plots.append(extra_plot)
                
                if legend:
                    ax.legend(loc='lower left')
                clim = None
            else:
                raise ValueError('Unknown plot type!')
        
        if clim is not None:
            self.current_clim = clim
        
        # Plot styling
        #self.fig.set_tight_layout = True
        if 'title' in self.plot_options:
            #ax.set_title(plot_options['title'])
            self.fig.suptitle(self.plot_options['title'])
        if 'xlabel' in self.plot_options:
            ax.set_xlabel(mathtexify(self.plot_options['xlabel']))
        if 'xticks' in self.plot_options:
            xticks = self.plot_options['xticks']
            if xticks == 'extra':
                ax.set_xticks(extra_info['xticks'])
            elif not xticks:
                ax.set_xticks([])
            else:
                ax.set_xticks(xticks)
        if 'ylabel' in self.plot_options:
            ax.set_ylabel(mathtexify(self.plot_options['ylabel']))
        if 'yticks' in self.plot_options:
            yticks = self.plot_options['yticks']
            if yticks == 'extra':
                ax.set_yticks(extra_info['yticks'])
            elif not yticks:
                ax.set_yticks([])
            else:
                ax.set_yticks(yticks)
        if 'time_label' in self.plot_options:
            time_label = mathtexify(self.plot_options['time_label'])
            ax.text(0.95, 0.95, time_label,
                    horizontalalignment='right',
                    verticalalignment='top',
                    transform = ax.transAxes)
        if ('colourbar' in self.plot_options and
                self.plot_options['colourbar']):
            self.cbar_dir = 'vertical'
            ax_parent = ax
            cbar = self.fig.colorbar(img, ax=ax)
            # somewhat dubious but no clear alternative...
            self.cbar_axes = self.fig.axes[1]
            if 'colourbar_label' in self.plot_options:
                cbar_label = mathtexify(self.plot_options['colourbar_label'])
                cbar.set_label(cbar_label)
            if 'colourbar_ticks' in self.plot_options:
                cbar.set_ticks(self.plot_options['colourbar_ticks'])
        else:
            cbar = None
            self.cbar_axes = None
        
        # Turn off silly offset thing
        x_formatter = ax.get_xaxis().get_major_formatter()
        try:
            x_formatter.set_useOffset(False)
        except AttributeError:
            pass
        y_formatter = ax.get_yaxis().get_major_formatter()
        try:
            y_formatter.set_useOffset(False)
        except AttributeError:
            pass
        if cbar is not None:
            cbar.formatter.set_useOffset(False)
            cbar.update_ticks()
        
        # Write figure to file
        self.output_canvas()
        
        return
    
    