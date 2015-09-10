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

def decode_colour(colour_string):
    """
    Helper function to convert (valid) colour code; either a name,
    hex code or RGB(A) tuple stored as a string; special value 'none' to
    produce fully transparent colour.
    """
    import ast
    if colour_string is None:
        return 'black' # default
    if colour_string == 'none':
        return (0, 0, 0, 0)
    if isinstance(colour_string, basestring):
        # Already a string
        return colour_string
    return ast.literal_eval(colour_string) # either a colour name,
                                           # hex code or RGB(A) tuple

def decode_symbol(symbol_string):
    """
    Helper function to decode (valid) symbol codes into matplotlib marker
    codes.
    """
    symbol_dict = {'point': '.', 'pixel': ',', 'circle': 'o', 'square': 's',
                   'pentagon': 'p', 'star': '*', 'hexagon1': 'h',
                   'hexagon2': 'H', 'plus': '+', 'x': 'x', 'diamond': 'D',
                   'thin diamond': 'd'}
    if symbol_string is None:
        return 'o' # Default symbol
    if symbol_string not in symbol_dict:
        print(">> Symbol type '{}' not supported by backend".format(
            symbol_string))
        print(">> Falling back to 'point' symbol")
        return '.'
    else:
        return symbol_dict[symbol_string]


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
        import matplotlib
        matplotlib.rcParams['text.usetex'] = False
        self.mpl_marker_size = matplotlib.rcParams['lines.markersize']
    
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
        #x_transform = self.plot_transforms['x_transform']
        #y_transform = self.plot_transforms['y_transform']
        hist_transform = self.plot_transforms['hist_transform']
        render_transform = self.plot_transforms['render_transform']
        
        limits = self.draw_limits['xy_limits']
        self.current_xylimits = limits
        self.current_clim = ['auto', 'auto']
        
        # Sink data
        sink_data = self.plot_options['sink_data']
        if sink_data is not None:
            sink_options = self.plot_options['sink_options']
            nsink = sink_data['mass'].size
            sink_x, sink_y = sink_options['sink_xy']
            #sink_mask = [False] * nsink
            #for i in range(nsink):
                #if (xmin <= sink_x[i] <= xmax) and (ymin <= sink_y[i] <= ymax):
                    #sink_mask[i] = True
            sink_mask = np.logical_and(
                np.logical_and(xmin <= sink_x, sink_x <= xmax),
                np.logical_and(ymin <= sink_y, sink_y <= ymax))
            print('Plotting {} of {} sinks'.format(sum(sink_mask), nsink))
            
            if nsink > 0:
                print('Sink data:')
                fmt_string = (' {:<4s}|{:^12.12s}|{:^42s}|{:^42s}|{:^12s}')
                print(fmt_string.format(
                    'id',
                    'mass' + sink_options['mass_str'],
                    'position (x,y,z)' + sink_options['position_str'],
                    'velocity (vx,vy,vz)' + sink_options['velocity_str'],
                    'age' + sink_options['age_str']))
            s_id = sink_data['id']
            s_mass = sink_data['mass']
            s_position = sink_data['position']
            s_velocity = sink_data['velocity']
            s_age = sink_data['age']
            for i in range(nsink):
                fmt_string = (' {:<4d}|{:<12g}|({:<12g}, {:<12g}, {:<12g})|' +
                              '({:<12g}, {:<12g}, {:<12g})|{:<12g}')
                print(fmt_string.format(
                    s_id[i], s_mass[i],
                    s_position[i][0], s_position[i][1], s_position[i][2],
                    s_velocity[i][0], s_velocity[i][1], s_velocity[i][2],
                    s_age[i]))
            
            sink_plot_dict = {}
            sink_plot_dict['marker'] = decode_symbol(
                sink_options['sink_marker'])
            sink_plot_dict['markerfacecolor'] = decode_colour(
                sink_options['sink_face_colour'])
            if sink_options['sink_edge_colour'] is not None:
                sink_plot_dict['markeredgecolor'] = decode_colour(
                    sink_options['sink_edge_colour'])
            if sink_options['sink_marker_size'] is not None:
                marker_size = float(sink_options['sink_marker_size'])
                if (marker_size < 0.0):
                    marker_size = (-marker_size * self.mpl_marker_size)
                sink_plot_dict['markersize'] = marker_size
            if sink_options['sink_marker_edge_width'] is not None:
                marker_ew = float(sink_options['sink_marker_edge_width'])
                if (marker_ew < 0.0):
                    marker_ew = (-marker_ew * self.mpl_marker_size)
                sink_plot_dict['markeredgewidth'] = marker_ew
            sink_plot_x = sink_x[sink_mask]
            sink_plot_y = sink_y[sink_mask]
        
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
        
        elif plot_type == 'line_plot':
            x = self.data_list[0][:, 0]
            y = self.data_list[0][:, 1]
            line_plot = ax.plot(x, y, 'r+')
            ax.set_xlim(limits[0])
            ax.set_ylim(limits[1])
            clim = None
        
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
            
            if plot_type.properties['plot_type'] == 'hist1d':
                counts, bins, extra_info = self.data_list
                
                if (counts is None) or (bins is None):
                    # empty plot
                    x = []
                    y = []
                    xlim = [0.0, 1.0]
                    ylim = [0.0, 1.0]
                    single_axis_plot = ax.plot(x, y)
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)
                    self.current_xylimits = [xlim, ylim]
                    clim = None
                else:
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
                    
                    if 'xlim' in extra_info:
                        ax.set_xlim(extra_info['xlim'])
                    if 'ylim' in extra_info:
                        ax.set_ylim(extra_info['ylim'])
                    
                    if limits is not None:
                        if limits[0] != ['auto', 'auto']:
                            ax.set_xlim(limits[0])
                        if limits[1] != ['auto', 'auto']:
                            ax.set_ylim(limits[1])
                    
                    xlim = ax.get_xlim()
                    ylim = ax.get_ylim()
                    self.current_xylimits = [xlim, ylim]
                    clim = None
            
            elif plot_type.properties['plot_type'] == 'power_spectrum':
                x, y, extra_info = self.data_list
                
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
                    x_untransformed = qx_transform[1](x_points).astype(
                        np.float_)
                
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
                    ax.legend(loc='center right')
                clim = None
            else:
                print('Backend does not support plot type: ',
                      plot_type.properties['plot_type'])
                raise ValueError()
        
        if clim is not None:
            self.current_clim = clim
        
        # Plot sinks
        if sink_data is not None:
            ax.plot(sink_plot_x, sink_plot_y, linestyle='None',
                    scalex=False, scaley=False, **sink_plot_dict)
        
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
    
    