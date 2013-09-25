"""
This submodule organizes analysis tasks, such as calculating histograms, and
interfaces with wrapper modules to obtain data
"""

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
                    data_limits, step, shared):
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
    
    if x_pos:
        xlim = (np.array(draw_limits['x_axis']) * x_unit /
                (step.length_mks * box_length[x_index]))
    else:
        xlim = None
    
    if y_pos:
        ylim = (np.array(draw_limits['y_axis']) * y_unit /
                (step.length_mks * box_length[y_index]))
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
    
    # Plot limits
    xmin, xmax = draw_limits['x_axis']
    ymin, ymax = draw_limits['y_axis']
    
    if xmin == 'auto':
        xmin = x.min()
    elif x_transform is not None:
        xmin = x_transform[0](xmin)
    if xmax == 'auto':
        xmax = x.max()
    elif x_transform is not None:
        xmax = x_transform[0](xmax)
    
    if (x_transform is not None) and (xmin > xmax):
        xmin, xmax = xmax, xmin
    
    if ymin == 'auto':
        ymin = y.min()
    elif y_transform is not None:
        ymin = y_transform[0](ymin)
    if ymax == 'auto':
        ymax = y.max()
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
    
    return [xedges, yedges, counts], xy_limits


def get_render_plot(x_field, x_index, x_unit,
                    y_field, y_index, y_unit,
                    render_field, render_index, render_unit,
                    vector_field, vector_unit, proj, z_slice,
                    resolution, plot_transforms, draw_limits,
                    data_limits, step, shared):
    
    """
    Obtain rendered plot of arbitrary quantity
    """
    from . import wrapper_functions as wf
    import numpy as np
    
    # Box length and transforms
    box_length = step.box_length
    render_transform = plot_transforms['render_transform']
    
    # get code units
    render_fac = render_field.code_mks / render_unit
    if vector_field is not None:
        vector_fac = vector_field.code_mks / vector_unit
    else:
        vector_fac = None
    
    if (x_unit != y_unit):
        raise ValueError('different units on coordinate axes!')
    
    xlim = (np.array(draw_limits['x_axis']) * x_unit /
                (step.length_mks * box_length[x_index]))
    ylim = (np.array(draw_limits['y_axis']) * y_unit /
                (step.length_mks * box_length[y_index]))
    
    grid_data = wf.get_grid_data(
            x_field, x_index, xlim, y_field, y_index, ylim,
            render_field, render_index, render_fac,
            plot_transforms['render_transform'],
            vector_field, vector_fac, data_limits,
            proj, resolution, z_slice, step, shared)
    
    if proj:
        # account for integral over 0->1 instead of physical units
        xy_fac = step.length_mks / x_unit
        if xy_fac != 1.0:
            grid_data = grid_data * xy_fac
    
    # Plot limits
    xmin, xmax = draw_limits['x_axis']
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

    if np.allclose(cmin, cmax, rtol=1e-20, atol=1e-100):
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


def calc_PDF(data_array, weights):
    import numpy as np
    
    n = len(data_array)
    minval, lq, uq, maxval = np.percentile(data_array,
                                           (0.0, 25.0, 75.0, 100.0))
    IQR = uq - lq
    h = 2.0 * IQR / float(n)**(1.0/3.0)
    
    num_bins = int(np.ceil((maxval - minval) / h))
    
    counts, bins = np.histogram(data_array, bins=num_bins, weights=weights)
    
    return [counts, bins, {}]


def calc_power_spectrum(data_array, weights):
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
    
    
    
    
    
    
    
    
    
    
