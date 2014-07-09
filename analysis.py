"""
This submodule organizes analysis tasks, such as calculating histograms, and
interfaces with wrapper modules to obtain data
"""

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass

class analysis_tool():
    def __init__(self, func, properties=None):
        self.func = func
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}

def bracket_data(value, transform):
    """
    If you have a situation where minimum and maximum are the same,
    come up with a sensible bracketing situation
    """
    if transform is not None:
        value = transform[1](value)
    if value == 0.0:
        minval = -1.0
        maxval = 1.0
    elif value < 0.0:
        minval = value * 2.0
        maxval = value / 2.0
    else:
        minval = value / 2.0
        maxval = value * 2.0
    if transform is not None:
        minval = transform[0](minval)
        maxval = transform[0](maxval)
    return minval, maxval


def get_histogram2d(x_field, x_index, x_unit, x_pos,
                    y_field, y_index, y_unit, y_pos,
                    resolution, plot_transforms, draw_limits,
                    data_limits, step, shared, data_list_pass=None):
    """
    Obtain histogrammed data of arbitrary quantities
    """
    from . import wrapper_functions as wf
    import numpy as np
    
    # Box length and transforms
    box_length = step.box_length
    x_transform = plot_transforms['x_transform']
    y_transform = plot_transforms['y_transform']
    hist_transform = plot_transforms['hist_transform']
    
    if data_list_pass is None:
        # Get data
        if x_pos:
            xlim = (np.array(draw_limits['x_axis']) * x_unit *
                    box_length[x_index] / step.length_mks)
        else:
            xlim = None
        
        if y_pos:
            ylim = (np.array(draw_limits['y_axis']) * y_unit *
                    box_length[y_index] / step.length_mks)
        else:
            ylim = None
        
        if x_pos or y_pos:
            data_array, weights, (bins_x, bins_y) = wf.get_sample_data(
                x_field, x_index, xlim,
                y_field, y_index, ylim,
                resolution, data_limits, step, shared)
        else:
            data_array, weights = wf.get_cell_data(
                x_field, x_index, y_field, y_index, data_limits, step, shared)
            bins_x, bins_y = None, None
        
        # Save to convenient names
        x = data_array[:, 0]
        y = data_array[:, 1]
        
        # Scale to units
        if x_field is not None:
            x_units = x_field.code_mks / x_unit
            if x_units != 1.0:
                x[:] = x * x_units
        if y_field is not None:
            y_units = y_field.code_mks / y_unit
            if y_units != 1.0:
                y[:] = y * y_units
        if bins_x is not None:
            bins_x = bins_x * step.length_mks / x_unit
        if bins_y is not None:
            bins_y = bins_y * step.length_mks / y_unit
        
        # Perform transform
        if (not x_pos) and (x_transform is not None):
            x[:] = x_transform[0](x)
        if (not y_pos) and (y_transform is not None):
            y[:] = y_transform[0](y)
        
        # Check for invalid data
        if (not np.isfinite(np.sum(x))) or (not np.isfinite(np.sum(y))):
            print('Warning - invalidly transformed data skipped!')
            x_mask = np.isfinite(x)
            y_mask = np.isfinite(y)
            mask_values = np.logical_and(x_mask, y_mask)
            if not np.any(mask_values):
                raise ValueError('No valid values remaining!')
            x = x[mask_values]
            y = y[mask_values]
            weights = weights[mask_values]
    
        min_max_data = {}
        min_max_data['x_min'] = x.min()
        min_max_data['x_max'] = x.max()
        min_max_data['y_min'] = y.min()
        min_max_data['y_max'] = y.max()
    
    else:
        # Use old data
        xedges, yedges, counts, min_max_data = data_list_pass
    
    # Plot limits
    xmin, xmax = draw_limits['x_axis']
    ymin, ymax = draw_limits['y_axis']
    
    if xmin == 'auto':
        xmin = min_max_data['x_min']
    elif x_transform is not None:
        xmin = x_transform[0](xmin)
    if xmax == 'auto':
        xmax = min_max_data['x_max']
    elif x_transform is not None:
        xmax = x_transform[0](xmax)
    
    if (x_transform is not None) and (xmin > xmax):
        xmin, xmax = xmax, xmin
    
    if ymin == 'auto':
        ymin = min_max_data['y_min']
    elif y_transform is not None:
        ymin = y_transform[0](ymin)
    if ymax == 'auto':
        ymax = min_max_data['y_max']
    elif y_transform is not None:
        ymax = y_transform[0](ymax)
    
    if (y_transform is not None) and (ymin > ymax):
        ymin, ymax = ymax, ymin
    
    if np.allclose(xmin, xmax, rtol=1e-20, atol=1e-100):
        if draw_limits['x_axis'][0] == 'auto':
            xmin = bracket_data(xmin, x_transform)[0]
        if draw_limits['x_axis'][1] == 'auto':
            xmax = bracket_data(xmax, x_transform)[1]
    if np.allclose(ymin, ymax, rtol=1e-20, atol=1e-100):
        if draw_limits['y_axis'][0] == 'auto':
            ymin = bracket_data(ymin, y_transform)[0]
        if draw_limits['y_axis'][1] == 'auto':
            ymax = bracket_data(ymax, y_transform)[1]
    
    xy_limits = [[xmin, xmax], [ymin, ymax]]
    
    if data_list_pass is None:
        # Calculate bins for non-position axes
        if bins_x is None:
            bins_x = np.linspace(xmin, xmax, resolution+1)
        if bins_y is None:
            bins_y = np.linspace(ymin, ymax, resolution+1)
        
        counts, xedges, yedges = np.histogram2d(x, y, bins=[bins_x, bins_y],
                                                range=xy_limits,
                                                weights=weights)
        old_settings = np.geterr()
        np.seterr(all='ignore')
        if hist_transform is not None:
            if not np.isfinite(hist_transform[0](0.0)):
                mask = counts==0.0
            else:
                mask = None
            counts = hist_transform[0](counts)
            if mask is not None:
                counts[mask] = None
        np.seterr(**old_settings)
    
    #counts[counts<cmin] = None
    #counts[counts>cmax] = None
    
    return [xedges, yedges, counts, min_max_data], xy_limits


def get_render_plot(x_field, x_index, x_unit,
                    y_field, y_index, y_unit,
                    render_field, render_index, render_unit,
                    vector_field, vector_unit, proj, z_slice,
                    resolution, plot_transforms, draw_limits,
                    data_limits, step, shared, data_list_pass=None):
    
    """
    Obtain rendered plot of arbitrary quantity
    """
    from . import wrapper_functions as wf
    import numpy as np
    import ast
    
    # Box length and transforms
    box_length = step.box_length
    render_transform = plot_transforms['render_transform']
    
    if data_list_pass is None:
        # Obtain data
        
        # get code units
        render_fac = render_field.code_mks / render_unit
        if vector_field is not None:
            vector_fac = vector_field.code_mks / vector_unit
        else:
            vector_fac = None
        
        if (x_unit != y_unit):
            raise ValueError('different units on coordinate axes!')
        
        xlim = (np.array(draw_limits['x_axis']) * x_unit *
                    box_length[x_index] / step.length_mks)
        ylim = (np.array(draw_limits['y_axis']) * y_unit *
                    box_length[y_index] / step.length_mks)
        
        # We need to restrict xlim and ylim now, based on data limits
        # and find a zlim
        position_limits = [x for x in data_limits if x['name'] == 'position']
        zlim = np.array([0.0, 1.0])
        changed_x = False
        changed_y = False
        for limit in position_limits:
            index = limit['index']
            code_mks = limit['field'].code_mks
            min_f, max_f = limit['limits']
            if min_f != 'none':
                min_f = min_f * step.box_length[index] / code_mks
            if max_f != 'none':
                max_f = max_f * step.box_length[index] / code_mks
            
            if limit['index'] == x_index:
                changed_x = True
                if min_f != 'none':
                    xlim[0] = max(xlim[0], min_f)
                elif max_f != 'none':
                    xlim[1] = min(xlim[1], max_f)
            elif limit['index'] == y_index:
                changed_y = True
                if min_f != 'none':
                    ylim[0] = max(ylim[0], min_f)
                elif max_f != 'none':
                    ylim[1] = min(ylim[1], max_f)
            else:
                zlim = [min_f, max_f]
        
        # Get grid data WITHOUT render_transform: transform later
        grid_data = wf.get_grid_data(
                x_field, x_index, xlim, y_field, y_index, ylim, zlim,
                render_field, render_index, render_fac, None,
                vector_field, vector_fac, data_limits,
                proj, resolution, z_slice, step, shared)
        
        if proj:
            # account for integral over 0->1 instead of physical units
            if shared.config.has_option('units', 'column'):
                unit_tuple_str = shared.config.get('units', 'column')
                column_unit, unit_str = ast.literal_eval(unit_tuple_str)
            else:
                column_unit = x_unit
            xy_fac = step.length_mks / column_unit
            if xy_fac != 1.0:
                grid_data = grid_data * xy_fac
        
        if plot_transforms['render_transform'] is not None:
            grid_data = plot_transforms['render_transform'][0](grid_data)
    
    else:
        # Use old data
        grid_data = data_list_pass[0]
    
    # Plot limits
    xlim = xlim * step.length_mks / (x_unit * box_length[x_index])
    ylim = ylim * step.length_mks / (x_unit * box_length[x_index])
    
    if changed_x:
        xmin, xmax = xlim
    else:
        xmin, xmax = draw_limits['x_axis']
    if changed_y:
        ymin, ymax = ylim
    else:
        ymin, ymax = draw_limits['y_axis']
    
    cmin, cmax = draw_limits['render']
    if cmin == 'auto':
        cmin = grid_data.min()
    elif render_transform is not None:
        cmin = render_transform[0](cmin)
    if cmax == 'auto':
        cmax = grid_data.max()
    elif render_transform is not None:
        cmax = render_transform[0](cmax)
    if (render_transform is not None) and (cmin > cmax):
        cmin, cmax = cmax, cmin

    if np.allclose(cmin, cmax, rtol=1e-10, atol=1e-50):
        if draw_limits['render'][0] == 'auto':
            cmin = bracket_data(cmin, render_transform)[0]
        if draw_limits['render'][1] == 'auto':
            cmax = bracket_data(cmax, render_transform)[1]
    clim = (cmin, cmax)

    xy_limits = [[xmin, xmax], [ymin, ymax]]
    
    return [grid_data], xy_limits, clim
    
    
def get_single_data(field, index, unit, transform,
                    data_limits, step, shared):
    """
    Obtain cell data of arbitrary quantity
    """
    from . import wrapper_functions as wf
    import numpy as np
    
    # Box length and transforms
    box_length = step.box_length
    
    data_array, weights = wf.get_cell_data(
            None, None, field, index, data_limits, step, shared)
    
    # Scale to units
    if field is not None:
        units = field.code_mks / unit
        if units != 1.0:
            data_array[:] = data_array * units
    
    # Perform transform
    if transform is not None:
        data_array[:] = transform[0](data_array)
    
    return data_array, weights


def get_box_data(field, index, unit, resolution, transform,
                 data_limits, step, shared):
    """
    Obtain cell data of arbitrary quantity
    """
    from . import wrapper_functions as wf
    import numpy as np
    
    # Box length and transforms
    box_length = step.box_length
    
    data_array, weights, bins = wf.get_sample_data(
            None, None, None, field, index, None,
            resolution, data_limits, step, shared)
    
    # Scale to units
    if field is not None:
        units = field.code_mks / unit
        if units != 1.0:
            data_array[:] = data_array * units
    
    # Perform transform
    if transform is not None:
        data_array[:] = transform[0](data_array)
    
    return data_array, weights


def calc_PDF(data_array, weights, shared):
    import numpy as np
    
    bin_number = shared.temp_config['PDF_bin_number']
    
    n = len(data_array)
    if n == 0:
        return [None, None, {}]
    elif bin_number == 'auto':
        minval, lq, uq, maxval = np.percentile(data_array,
                                            (0.0, 25.0, 75.0, 100.0))
        IQR = uq - lq
        h = 2.0 * IQR / float(n)**(1.0/3.0)
        
        num_bins = int(np.ceil((maxval - minval) / h))
    else:
        num_bins = bin_number
    
    bin_min = shared.temp_config['PDF_bin_min']
    bin_max = shared.temp_config['PDF_bin_max']
    if bin_min == 'auto':
        bin_min = data_array.min()
    if bin_max == 'auto':
        bin_max = data_array.max()
    bin_range = (bin_min, bin_max)
    
    counts, bins = np.histogram(data_array, bins=num_bins,
                                range=bin_range, weights=weights)
    
    return [counts, bins, {}]


def PDF_interactive(shared):
    import numpy as np
    
    while True:
        input_string = input('Enter number of bins [default=auto]: ').strip()
        if not input_string or input_string=='auto':
            bin_number = 'auto'
            break
        elif not input_string.isdigit():
            print('  >> Invalid number of bins!')
            continue
        bin_number = int(input_string)
        if not (2 <= bin_number <= 1e6):
            print('  >> Invalid number of bins!')
            continue
        break
        
    while True:
        input_string = input('Enter minimum [default=auto]: ').strip()
        if not input_string:
            bin_min = 'auto'
            break
        try:
            bin_min = float(input_string)
        except ValueError:
            print(' >> Not a valid number!')
            continue
        if not np.isfinite(bin_min):
            print(' >> Not a valid number!')
            continue
        break
    
    while True:
        input_string = input('Enter maximum [default=auto]: ').strip()
        if not input_string:
            bin_max = 'auto'
            break
        try:
            bin_max = float(input_string)
        except ValueError:
            print(' >> Not a valid number!')
            continue
        if not np.isfinite(bin_max):
            print(' >> Not a valid number!')
            continue
        break
    
    shared.temp_config['PDF_bin_number'] = bin_number
    shared.temp_config['PDF_bin_min'] = bin_min
    shared.temp_config['PDF_bin_max'] = bin_max


def calc_power_spectrum(data_array, weights, shared):
    import numpy as np
    
    n_tot = data_array.shape[0]
    n_float = n_tot**(1.0/3.0)
    n = np.rint(n_float)
    if not np.allclose(n, n_float, rtol=1e-05, atol=1e-08):
        raise ValueError('Not got a cube!')
    
    n = int(n)
    
    cells = data_array.reshape((n,n,n))
    
    cells_F = np.fft.fftshift(np.fft.rfftn(cells),axes=(0,1))
    cells_P = np.real(cells_F * np.conjugate(cells_F))
    
    if n%2 == 1:
        # not an even resolution
        raise ValueError('Not using an even resolution number')
    
    n_half = n / 2
    n_bins = n_half - 2
    bin_sum = np.zeros(n_bins)
    bin_count = np.zeros(n_bins)
    
    for i2 in range(n):
        i = i2 - n_half
        for j2 in range(n):
            j = j2 - n_half
            for k in range(n/2):
                if i==0 and j==0 and k==0:
                    continue
                #print('i, j, k: ', i, j, k)
                #print('i2, j2, k2: ', i2, j2, k2)
                kr = np.sqrt(i**2 + j**2 + k**2)
                #print('kr: ', kr)
                slot = int(np.rint(kr)) - 1
                #print('slot: ', slot)
                if not (0 <= slot < n_bins):
                    #print('NO!!!')
                    continue
                bin_count[slot] += 1.0
                bin_sum[slot] += (cells_P[i2, j2, k])
    
    power = bin_sum / bin_count
    k = np.arange(1, n_bins+1, dtype=np.float_)
    
    k_log_average = 10.0**(0.5 * np.log10(float(n)))
    k_rint = max(1, int(np.rint(k_log_average)))
    k_rint = min(k_rint, n)
    P_0 = power[k_rint-1]
    
    C = P_0 * k_log_average**4
    
    func = lambda x: C * x**-4
    extra_funcs = [(func, 'k^{-4.0}')]
    
    k_log_min = int(np.floor(np.log10(k[0])))
    k_log_max = int(np.ceil(np.log10(k[-1])))
    k_ticks = list(range(k_log_min, k_log_max+1))
    
    return [k, power, {'extra_funcs': extra_funcs,
                       'xticks': k_ticks}]


def get_analysis_list():
    analysis_list = []
    
    PDF_props = {'name': 'PDF',
                 'file_ext': 'PDF',
                 'data_type': 'cell_data',
                 'plot_type': 'hist1d',
                 'title': 'Probability density function',
                 'data_axis': 'x',
                 'ylabel': 'Frequency density',
                 'extra_interactive': PDF_interactive,
                 'yticks': False}
    PDF = analysis_tool(calc_PDF, PDF_props)
    analysis_list.append(PDF)
    
    power_spectrum_props = {'name': 'Power spectrum',
                            'file_ext': 'powerspec',
                            'data_type': 'sample_data',
                            'plot_type': 'power_spectrum',
                            'title': 'Power spectrum',
                            'data_axis': None,
                            'xlabel': 'Wavenumber',
                            'xticks': 'extra',
                            'ylabel': 'Power',
                            'yticks': False}
    power_spectrum = analysis_tool(calc_power_spectrum, power_spectrum_props)
    analysis_list.append(power_spectrum)
    
    return analysis_list
    
    
    
    
    
    
    
    
    
    
