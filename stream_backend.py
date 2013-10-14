"""
This submodule implements the base class for stream backends.
"""

from __future__ import print_function
import numpy as np

class BackendStream():
    """
    Backend for writing to text files
    """
    
    def __init__(self):
        self.step = None
        self.data_array = None
        self.data_list = None
        self.draw_limits = None
        self.plot_transforms = None
        self.plot_options = None
        self.interactive = False
        
        self.max_auto_resolution = 256
        self.output_filename = ''
    
    def init_figure(self):
        """
        Create the figure
        """
        pass
    
    def on_exit(self):
        """
        Function to tidy up backend on exit
        """
        pass
    
    def set_output_filename(self, filename):
        """
        Set the output filename
        """
        self.output_filename = filename
    
    def plot_data(self):
        """
        Take a data_array and 'plot' to a file
        """
        import numpy as np
        
        # Plot limits
        xmin, xmax = self.draw_limits['x_axis']
        ymin, ymax = self.draw_limits['y_axis']
        
        # Transforms
        x_transform = self.plot_transforms['x_transform']
        y_transform = self.plot_transforms['y_transform']
        hist_transform = self.plot_transforms['hist_transform']
        render_transform = self.plot_transforms['render_transform']
        
        limits = self.draw_limits['xy_limits']
        self.current_xylimits = limits
        
        plot_type = self.plot_options['plot_type']
        
        if plot_type == 'time':
            self.data_array = self.data_list[0]
        
        elif plot_type == 'hist2d':
            xedges, yedges, counts, min_max_data = self.data_list
            
            self.data_array = np.empty((len(xedges)*len(yedges), 3))
            
            k = 0
            for i, x in enumerate(xedges):
                for j, y in enumerate(yedges):
                    self.data_array[k, :] = [xedges[i], yedges[j], counts[i, j]]
                    k = k + 1
        
        elif plot_type == 'render':
            
            nxy = self.data_list[0].shape
            if len(nxy) != 2:
                raise ValueError("Didn't do non-3D stuff!")
            nx, ny = nxy
            
            half_dx = 0.5 * (xmax - xmin) / float(nx)
            half_dy = 0.5 * (ymax - ymin) / float(ny)
            
            x_pos = np.linspace(xmin + half_dx, xmax - half_dx, nx)
            y_pos = np.linspace(ymin + half_dy, ymax - half_dy, ny)
            
            self.data_array = np.empty((nx * ny, 3))
            
            k = 0
            for i, x in enumerate(x_pos):
                for j, y in enumerate(y_pos):
                    self.data_array[k,:] = [x_pos[i], y_pos[i],
                                            self.data_list[0][i, j]]
                    k = k + 1
        else:
            # Single axis plots
            
            
            data_axis = self.plot_options['data_axis']
            if data_axis != 'x':
                qx_transform = self.plot_transforms['qx_transform']
            else:
                qx_transform = None
            
            if data_axis != 'y':
                qy_transform = self.plot_transforms['qy_transform']
            else:
                qy_transform = None
            
            if plot_type == 'hist1d':
                counts, bins, extra_info = self.data_list
                
                if qy_transform is not None:
                    counts = qy_transform[0](counts)
                
                self.data_array = np.empty((len(bins), 2))
                for i, x in enumerate(bins[:-1]):
                    self.data_array[i, :] = [bins[i], counts[i]]
                self.data_array[-1, :] = (bins[-1], 0.0)
        
            elif plot_type == 'power_spectrum':
                
                x = self.data_list[0]
                y = self.data_list[1]
                extra_info = self.data_list[2]
                
                if qx_transform is not None:
                    x = qx_transform[0](x)
                if qy_transform is not None:
                    y = qy_transform[0](y)
                
                self.data_array = np.vstack((x,y)).T
                
        # Write figure to file
        self.output_canvas()
    
    
    
    
    
    
    
    
    
    
    