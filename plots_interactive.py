"""
This submodule organizes the interactive part of plotting
"""

from __future__ import print_function

class KeyOption():
    """
    A menu corresponding to a keypress in interactive mode
    """
    def __init__(self, keys=None, title=None, call=None, info=None):
        self.keys = keys
        self.title = title
        self.call = call
        self.info = info


def init_key_dict(backend):
    """
    Define the key press dictionary for this backend
    """
    
    backend.key_dicts = {}
    
    key_dict = {}
    number_opt = KeyOption('1-9', 'Multiply next zoom/step by number',
                           key_factor)
    for i in range(1, 10):
        key_dict[str(i)] = number_opt
    zoom_opt = KeyOption('z/Z', 'Multiply/divide next zoom/step by 10',
                         key_mult)
    key_dict['z'] = zoom_opt
    key_dict['Z'] = zoom_opt
    zoom_in_out = KeyOption('+/-', 'Zoom in/out 10%', key_zoom, 'in')
    key_dict['+'] = zoom_in_out
    key_dict['-'] = zoom_in_out
    key_dict['a'] = KeyOption(
        'a', 'Autoscale (x/y axis, main figure or colourbar)', key_zoom, 'auto')
    key_dict['h'] = KeyOption('h', 'Show this help', key_help_menu)
    key_dict['l'] = KeyOption('l', 'Toggle logarithmic rendered plot', key_log)
    save_opt = KeyOption('s/S', 'Save details of plot/plot and limits to '
                         'memory', key_save)
    key_dict['s'] = save_opt
    key_dict['S'] = save_opt
    key_dict['q'] = KeyOption('q', 'Close plot', backend.close_plot)
    key_dict['p'] = KeyOption('p', 'Show cursor position', key_print_position)
    
    backend.key_dicts['time'] = dict(**key_dict)
    
    key_dict['b'] = KeyOption('b', 'Previous timestep', key_next_prev, -1)
    key_dict['n'] = KeyOption('n', 'Next timestep', key_next_prev, 1)
    
    backend.key_dicts['single_axis'] = dict(**key_dict)
    
    cbar_opt = KeyOption(
        'm/M', 'Step forwards/backwards through colour schemes', key_cbar)
    key_dict['m'] = cbar_opt
    key_dict['M'] = cbar_opt
    render_opt = KeyOption(
        'f/F', 'Step forwards/backwards through rendered quantities',
        key_render)
    key_dict['f'] = render_opt
    key_dict['F'] = render_opt
    key_dict['i'] = KeyOption('h', 'Invert colour scheme', key_cbar_invert)
    
    backend.key_dicts['hist2d'] = key_dict
    backend.key_dicts['render'] = key_dict


def key_press_interactive(backend, key, axes_name, x, y):
    """
    Handle certain key press events that require data to be updated
    """
    
    if key in backend.key_dict:
        info = backend.key_dict[key].info
        backend.key_dict[key].call(backend, axes_name, x, y, key, info)


def mouse_zoom_main(backend, xlim, ylim):
    """
    Handle zooming of the main figure by the mouse
    """
    from . import plots
    from . import limits
    x_transform = backend.plot_transforms['x_transform']
    y_transform = backend.plot_transforms['y_transform']
    if x_transform is None:
        backend.plot_args['plot_limits']['x_axis'] = xlim
    else:
        backend.plot_args['plot_limits']['x_axis'] = x_transform[1](xlim)
    if y_transform is None:
        backend.plot_args['plot_limits']['y_axis'] = ylim
    else:
        backend.plot_args['plot_limits']['y_axis'] = y_transform[1](ylim)
    config = backend.plot_args['shared'].config
    if config.get('render', 'resolution') == 'auto':
        x_pos = backend.plot_options['x_pos']
        y_pos = backend.plot_options['y_pos']
        box_length = backend.plot_options['box_length']
        xlim, ylim = limits.snap_to_grid(xlim, ylim, x_pos, y_pos, box_length,
                                         backend.plot_options['minmax_res'])
    plots.update_plot_data(backend)


def mouse_zoom_cbar(backend, clim):
    """
    Handle zooming of the colourbar by the mouse
    """
    from . import plots
    render_transform = backend.plot_transforms['render_transform']
    if render_transform is None:
        backend.plot_args['plot_limits']['render'] = clim
    else:
        backend.plot_args['plot_limits']['render'] = render_transform[1](clim)
    plots.update_plot_data(backend, True)


def key_help_menu(backend, *args):
    """
    Print the list of possible keyboard commands
    """
    print('\nKeyboard options:')
    keyoption_list = []
    for key, keyoption in sorted(backend.key_dict.items()):
        if not keyoption in keyoption_list:
            keyoption_list.append(keyoption)
            print(' {}: {}'.format(keyoption.keys, keyoption.title))
    print()
    print('Mouse usage:')
    print('Click and drag on the figure or colourbar to zoom')
    print()


def key_log(backend, axes_name, *args):
    """
    Toggle the current plot, if a rendered plot, between log10 and not log10
    """
    from . import plots
    from numpy import log10, frompyfunc
    plot_type = backend.plot_options['plot_type']
    data_axis = backend.plot_options['data_axis']
    plot_transforms = backend.plot_transforms
    transform_keys = backend.transform_keys
    if plot_type == 'render':
        key = 'render_transform'
    else:
        if axes_name == 'main_axes':
            if plot_type in ['hist2d', 'time']:
                key = 'y_transform'
            else:
                key = 'x_transform'
        elif axes_name == 'x-axis':
            if plot_type in ['time', 'hist2d']:
                key = 'x_transform'
            else:
                if data_axis == 'x':
                    key = 'x_transform'
                else:
                    key = 'qx_transform'
        elif axes_name == 'y-axis':
            if plot_type in ['time', 'hist2d']:
                key = 'y_transform'
            else:
                if data_axis == 'y':
                    key = 'y_transform'
                else:
                    key = 'qy_transform'
        elif axes_name == 'cbar':
            key = 'hist_transform'
        if key == 'x_transform' and backend.plot_options['x_pos']:
            return
        if key == 'y_transform' and backend.plot_options['y_pos']:
            return
    
    if (plot_transforms[key] is not None and
            plot_transforms[key][0] is log10):
        transform_keys[key] = 'none'
        plot_transforms[key] = None
        print('Non-logarithmic')
    else:
        ten_to = frompyfunc(lambda x: 10.0**x, 1, 1)
        transform_keys[key] = 'log(x)'
        plot_transforms[key] = (log10, ten_to)
        print('Logarithmic')
        
    plots.update_plot_data(backend)


def key_save(backend, axes_name, x, y, key, info):
    """
    Save details of plot (and possibly limits) to memory
    """
    from . import limits
    plot_args = backend.plot_args
    config = plot_args['shared'].config
    if plot_args['cmap'] is not None:
        config.set('render', 'cmap', plot_args['cmap'])
        config.set('render', 'cmap_invert', plot_args['cmap_invert'])
    
    plot_type = backend.plot_options['plot_type']
    short_only = plot_type not in ['hist2d', 'render']
    if key == 's' or short_only:
        print('Plot options saved to memory')
        return
    # and limits:
    x_axis = plot_args['x_axis']
    y_axis = plot_args['y_axis']
    render = plot_args['render']
    vector = plot_args['vector']
    plot_limits = plot_args['plot_limits']
    shared = plot_args['shared']
    
    limits.set_current_limits(x_axis, y_axis, render,
                              vector, plot_limits, shared)
    print('Plot options and limits saved to memory')


def key_print_position(backend, axes_name, x, y, key, info):
    """
    Print the current cursor position on the main figure
    """
    if axes_name == 'main_axes':
        print(' >> x, y: ', x, y)


def key_next_prev(backend, axes_name, x, y, key, info):
    """
    Step backwards/forwards through timesteps
    """
    from . import plots
    step_no = backend.plot_args['step_no']
    num_steps = len(backend.plot_args['shared'].sim_step_list)
    
    if key == 'n':
        step_direction = backend.zoom_factor * backend.zoom_mult
    else:
        step_direction = -backend.zoom_factor * backend.zoom_mult
    
    if (info < 0) and (step_no == 0):
        print(' >> Reached first timestep')
    elif (info > 0) and (step_no == num_steps - 1):
        print(' >> Reached last timestep')
    else:
        step_no = step_no + step_direction
        step_no = max(step_no, 0)
        step_no = min(step_no, num_steps - 1)
        
        step = backend.plot_args['shared'].sim_step_list[step_no]
        print ('Loading output {}...'.format(step.output_dir))
        step.load_dataset()
        
        backend.plot_args['step_no'] = step_no
        
        plots.update_plot_data(backend)
    backend.zoom_factor = 1
    backend.zoom_mult = 1


def key_render(backend, axes_name, x, y, key, info):
    """
    Step backwards/forwards through rendered quantities
    """
    from . import plots
    from . import limits
    field_mappings = backend.plot_args['shared'].field_mappings
    render = backend.plot_args['render']
    
    if render is None:
        return
    
    if key == 'f':
        step_direction = 1
    else:
        step_direction = -1
    
    while True:
        render = render + step_direction
        if render >= len(field_mappings):
            render = 0
        if render < 0:
            render = len(field_mappings) - 1
        if not 'position' in field_mappings[render].field.flags:
            break
    
    print(" >> Plotting quantity '{}'".format(field_mappings[render].title))
    
    backend.plot_args['render'] = render
    backend.plot_args['render_index'] = field_mappings[render].index
    
    # Find new data and render limits
    x_axis = backend.plot_args['x_axis']
    x_index = backend.plot_args['x_index']
    y_axis = backend.plot_args['y_axis']
    y_index = backend.plot_args['y_index']
    render = backend.plot_args['render']
    render_index = backend.plot_args['render_index']
    vector = backend.plot_args['vector']
    shared = backend.plot_args['shared']
    
    plot_limits, data_limits = limits.get_current_limits(
        x_axis, x_index, y_axis, y_index, render, render_index, vector,
        shared)
    
    backend.plot_args['plot_limits']['render'] = plot_limits['render']
    backend.plot_args['data_limits'] = data_limits
    
    plots.update_plot_data(backend)


def key_cbar(backend, axes_name, x, y, key, info):
    """
    Step backwards/forwards through colour schemes
    """
    from . import plots
    cmap_list = backend.plot_args['shared'].cmaps
    
    if key == 'm':
        step_direction = 1
    else:
        step_direction = -1
    
    cur_cmap = backend.plot_args['cmap']
    cur_cmap_index = cmap_list.index(cur_cmap)
    next_cmap_index = cur_cmap_index + step_direction
    
    if next_cmap_index < 0:
        next_cmap_index = len(cmap_list) - 1
    elif next_cmap_index >= len(cmap_list):
        next_cmap_index = 0
    
    new_cmap = cmap_list[next_cmap_index]
    print("Using colour scheme '{}'".format(new_cmap))
    
    backend.plot_args['cmap'] = new_cmap
    
    
    plots.update_plot_data(backend, True)


def key_cbar_invert(backend, axes_name, x, y, key, info):
    """
    Change whether colour scheme is inverted
    """
    from . import plots
    if backend.plot_args['cmap_invert'] == 'yes':
        backend.plot_args['cmap_invert'] = 'no'
        print('Colour scheme not inverted')
    else:
        backend.plot_args['cmap_invert'] = 'yes'
        print('Colour scheme inverted')
    
    plots.update_plot_data(backend, True)


def key_factor(backend, axes_name, x, y, key, info):
    """
    Adjust backend.zoom_factor
    """
    backend.zoom_factor = int(key)
    print('Zoom/steps multiplied by {}'.format(
        backend.zoom_factor * backend.zoom_mult))


def key_mult(backend, axes_name, x, y, key, info):
    """
    Adjust backend.zoom_mult
    """
    mult = backend.zoom_mult
    if key == 'Z':
        if mult == 1000000:
            mult = 1
        else:
            mult = mult * 10
    else:
        if mult == 1:
            mult = 1000000
        else:
            mult = mult / 10
    
    backend.zoom_mult = mult
    print('Zoom/steps multiplied by {}'.format(
        backend.zoom_factor * backend.zoom_mult))


def key_zoom(backend, axes_name, x, y, key, info):
    """
    Zoom in/out or autoscale
    """
    from . import plots
    from . import limits
    plot_limits = backend.plot_args['plot_limits']
    config = backend.plot_args['shared'].config
    zoom_x = False
    zoom_y = False
    zoom_c = False
    x_pos = backend.plot_options['x_pos']
    y_pos = backend.plot_options['y_pos']
    box_length = backend.plot_options['box_length']
    
    if axes_name == 'main_axes':
        zoom_x = True
        zoom_y = True
    elif axes_name == 'x-axis':
        zoom_x = True
    elif axes_name == 'y-axis':
        zoom_y = True
    elif axes_name == 'cbar':
        zoom_c = True
    check_aspect = (config.get('limits', 'aspect_ratio') == 'on' and
                    config.get('page', 'equal_scales') == 'on')
    if (x_pos and y_pos) and (zoom_x or zoom_y) and check_aspect:
        aspect_protection = True
        zoom_x, zoom_y = True, True
    else:
        aspect_protection = False
    if info=='auto':
        if zoom_x:
            plot_limits['x_axis'] = ('auto', 'auto')
        if zoom_y:
            plot_limits['y_axis'] = ('auto', 'auto')
        if zoom_c:
            plot_limits['render'] = ('auto', 'auto')
    else:
        base_zoom = float(backend.zoom_factor * backend.zoom_mult)
        zoom_cycle = 4.0 # zooms to double
        zoom_factor = (2.0**(1.0/zoom_cycle))**base_zoom
        if key == '+':
            zoom_factor = 1.0 / zoom_factor
        elif key == '-':
            pass
        else:
            raise ValueError('Unknown type of zoom!')
        
        if zoom_x:
            x_transform = backend.plot_transforms['x_transform']
            x_min, x_max = plot_limits['x_axis']
            if x_min == 'auto':
                x_min = backend.current_xylimits[0][0]
                if x_transform is not None:
                    x_min = x_transform[1](x_min)
            if x_max == 'auto':
                x_max = backend.current_xylimits[0][1]
                if x_transform is not None:
                    x_transform = backend.plot_transforms['x_transform']
                    x_max = x_transform[1](x_max)
            x_centre = (x_min + x_max) / 2.0
            if x_pos:
                x_width = min(box_length[0], (x_max - x_min) * zoom_factor)
                x_half_width = x_width / 2.0
                x_centre = max(x_half_width, x_centre)
                x_centre = min(box_length[0] - x_half_width, x_centre)
                
                x_min_new = x_centre - x_half_width
                x_max_new = x_centre + x_half_width
                
                x_min_new = max(0.0, x_min_new)
                x_max_new = min(box_length[0], x_max_new)
                xlim = (x_min_new, x_max_new)
            else:
                x_min_new = (x_min - x_centre) * zoom_factor + x_centre
                x_max_new = (x_max - x_centre) * zoom_factor + x_centre
                xlim = (x_min_new, x_max_new)
            plot_limits['x_axis'] = xlim
        
        if zoom_y:
            y_transform = backend.plot_transforms['y_transform']
            y_min, y_max = plot_limits['y_axis']
            if y_min == 'auto':
                y_min = backend.current_xylimits[1][0]
                if y_transform is not None:
                    y_min = y_transform[1](y_min)
            if y_max == 'auto':
                y_max = backend.current_xylimits[1][1]
                if y_transform is not None:
                    y_max = y_transform[1](y_max)
            y_centre = (y_min + y_max) / 2.0
            if y_pos:
                y_width = min(box_length[1], (y_max - y_min) * zoom_factor)
                y_half_width = y_width / 2.0
                y_centre = max(y_half_width, y_centre)
                y_centre = min(box_length[1] - y_half_width, y_centre)
                
                y_min_new = y_centre - y_half_width
                y_max_new = y_centre + y_half_width
                
                y_min_new = max(0.0, y_min_new)
                y_max_new = min(box_length[1], y_max_new)
                ylim = (y_min_new, y_max_new)
            else:
                y_min_new = (y_min - y_centre) * zoom_factor + y_centre
                y_max_new = (y_max - y_centre) * zoom_factor + y_centre
                ylim = (y_min_new, y_max_new)
            plot_limits['y_axis'] = ylim
            
        if zoom_c:
            c_min, c_max = backend.current_clim
            c_centre = (c_min + c_max) / 2.0
            c_min_new = (c_min - c_centre) * zoom_factor + c_centre
            c_max_new = (c_max - c_centre) * zoom_factor + c_centre
            render_transform = backend.plot_transforms['render_transform']
            if render_transform is not None:
                c_min_new = render_transform[1](c_min_new)
                c_max_new = render_transform[1](c_max_new)
            plot_limits['render'] = (c_min_new, c_max_new)
        backend.zoom_factor = 1
        backend.zoom_mult = 1
        
    plots.update_plot_data(backend, zoom_c)
    
    
    
    
    
    
    
    
    
    