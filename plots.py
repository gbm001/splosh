"""
This submodule organizes plotting, combining the data wrapper with
the backend drawing package
"""

def get_cmaps():
    """
    Get a list of colour maps
    """
    import matplotlib.cm
    cmap_list = [x for x in matplotlib.cm.cmap_d.keys() if not x.endswith('_r')]
    cmap_list.sort()
    return cmap_list


def plot_fields(x_axis, x_index, y_axis, y_index, render, render_index,
                vector, plot_type, z_slice, backend, shared):
    """
    Plot a 2D histogram plot with one point per grid cell, or
    plot a rendered plot, with optional vector plot
    """
    from . import __code_name
    from . import limits
    from . import transforms
    from . import plots_interactive
    
    if not backend.interactive:
        # Loop over all timesteps
        
        for i, step in enumerate(shared.sim_step_list):
            print ('Loading output {}...'.format(step.output_dir))
            
            file_no = step.get_output_id()
            if file_no is None:
                file_no = i + 1
            
            if plot_type == 'render':
                base_filename = '{}_render_{}_{:05d}'.format(
                    __code_name.lower(), shared.field_mappings[render].title,
                    file_no)
            elif plot_type == 'hist2d':
                base_filename = '{}_hist2d_{}_{:05d}'.format(
                    __code_name.lower(), shared.field_mappings[y_axis].title,
                    file_no)
            else:
                base_filename = '{}_{}_{}_{:05d}'.format(
                    __code_name.lower(), plot_type.properties['file_ext'],
                    shared.field_mappings[x_axis].title,
                    file_no)
            backend.set_output_filename(base_filename)
            
            # Find limits
            plot_limits, data_limits = limits.get_current_limits(
                x_axis, x_index, y_axis, y_index, render, render_index, vector,
                plot_type, shared)
            
            # Find transforms
            transform_keys, plot_transforms = transforms.get_plot_transforms(
                x_axis, y_axis, render, plot_type, shared)
            
            cmap = shared.config.get('render', 'cmap')
            cmap_invert = shared.config.get('render', 'invert')
            
            plot_args = {'x_axis': x_axis, 'x_index': x_index,
                        'y_axis': y_axis, 'y_index': y_index,
                        'render': render, 'render_index': render_index,
                        'vector': vector, 'plot_type': plot_type,
                        'z_slice': z_slice, 'step_no': i,
                        'cmap': cmap, 'cmap_invert': cmap_invert,
                        'plot_limits': plot_limits, 'data_limits': data_limits,
                        'transform_keys': transform_keys,
                        'plot_transforms': plot_transforms,
                        'backend': backend, 'shared': shared}
            
            data_list, draw_limits, plot_options = single_plot_data(**plot_args)
            
            backend.data_list = data_list
            backend.draw_limits = draw_limits
            backend.transform_keys = transform_keys
            backend.plot_transforms = plot_transforms
            backend.plot_options = plot_options
            
            backend.init_figure()
            backend.plot_data()
    
    else:
        # Interactive plot; start with first timestep
        plots_interactive.init_key_dict(backend)
        
        step_no = 0
        step = shared.sim_step_list[step_no]
        print ('Loading output {}'.format(step.output_dir))
        
        # Find limits
        plot_limits, data_limits = limits.get_current_limits(
            x_axis, x_index, y_axis, y_index, render, render_index, vector,
            plot_type, shared)
        
        # Find transforms
        transform_keys, plot_transforms = transforms.get_plot_transforms(
            x_axis, y_axis, render, plot_type, shared)
        
        cmap = shared.config.get('render', 'cmap')
        cmap_invert = shared.config.get('render', 'invert')
        
        plot_args = {'x_axis': x_axis, 'x_index': x_index,
                     'y_axis': y_axis, 'y_index': y_index,
                     'render': render, 'render_index': render_index,
                     'vector': vector, 'plot_type': plot_type,
                     'z_slice': z_slice, 'step_no': step_no,
                     'cmap': cmap, 'cmap_invert': cmap_invert,
                     'plot_limits': plot_limits, 'data_limits': data_limits,
                     'transform_keys': transform_keys,
                     'plot_transforms': plot_transforms,
                     'backend': backend, 'shared': shared}
        
        data_list, draw_limits, plot_options = single_plot_data(**plot_args)
        
        backend.plot_args = plot_args
        backend.step_no = step_no
        if plot_options['plot_type'] in backend.key_dicts:
            backend.key_dict = backend.key_dicts[plot_options['plot_type']]
        else:
            backend.key_dict = backend.key_dicts['single_axis']
        backend.key_press_event = plots_interactive.key_press_interactive
        backend.zoom_main_event = plots_interactive.mouse_zoom_main
        backend.zoom_cbar_event = plots_interactive.mouse_zoom_cbar
        
        backend.data_list = data_list
        backend.draw_limits = draw_limits
        backend.transform_keys = transform_keys
        backend.plot_transforms = plot_transforms
        backend.plot_options = plot_options
        backend.plot_type = plot_type
        
        backend.init_figure()
        backend.plot_data()
    
    return


def plot_time(axis, index, time_operation, backend, shared):
    """
    Create simple line plot of properties against time
    """
    from . import __code_name
    from . import limits
    from . import transforms
    from . import plots_interactive
    
    # Find limits
    plot_limits, data_limits = limits.get_current_limits(
        None, None, axis, index, None, None, None, 'time', shared)
    
    # Find transforms
    transform_keys, plot_transforms = transforms.get_plot_transforms(
        None, axis, None, 'time', shared)
    
    plot_args = {'x_axis': None, 'x_index': None,
                 'y_axis': axis, 'y_index': index,
                 'render': None, 'render_index': None,
                 'vector': None, 'plot_type': 'time',
                 'z_slice': None, 'step_no': None,
                 'cmap': None, 'cmap_invert': None,
                 'plot_limits': plot_limits, 'data_limits': data_limits,
                 'transform_keys': transform_keys,
                 'plot_transforms': plot_transforms,
                 'backend': backend, 'shared': shared}
    
    if not backend.interactive:
        base_filename = '{}_{}_{}'.format(__code_name.lower(),
                                        shared.field_mappings[axis].title,
                                        time_operation[1])
        backend.set_output_filename(base_filename)
    
    plot_args['time_operation'] = time_operation
    #plot_args['weight'] = weight
    
    data_list, draw_limits, plot_options = time_plot_wrapper(**plot_args)
    
    backend.plot_args = plot_args
    
    backend.step_no = None
    if backend.interactive:
        plots_interactive.init_key_dict(backend)
        backend.key_dict = backend.key_dicts['time']
        backend.key_press_event = plots_interactive.key_press_interactive
        backend.zoom_main_event = plots_interactive.mouse_zoom_main
        backend.zoom_cbar_event = plots_interactive.mouse_zoom_cbar
    
    backend.data_list = data_list
    backend.draw_limits = draw_limits
    backend.transform_keys = transform_keys
    backend.plot_transforms = plot_transforms
    backend.plot_options = plot_options
    backend.plot_type = 'time'
    
    backend.init_figure()
    backend.plot_data()


def time_plot_wrapper(**plot_args):
    """
    Wrap up single_plot_data; run over each step and collate the results
    Note this is very slightly badly behaved function! It both returns
    a value and makes (minor) alterations to plot_args
    """
    import numpy as np
    
    shared = plot_args['shared']
    nstep = len(shared.sim_step_list)
    
    time_data = np.zeros((nstep, 2))
    
    for i, step in enumerate(shared.sim_step_list):
        print ('Loading output {}...'.format(step.output_dir))
        step.load_dataset()
        
        # load data
        if i==0:
            plot_args['plot_options'] = None
        else:
            plot_args['plot_options'] = plot_options
        
        plot_args['step_no'] = i
        
        data_list, plot_options = single_plot_data(**plot_args)
        
        time, cell_data, weights = data_list
        #if not plot_args['weight']:
            #weights = np.ones_like(cell_data)
        
        single_result = plot_args['time_operation'][2](cell_data, weights)
        time_data[i, 0] = time
        time_data[i, 1] = single_result
        del data_list
        del cell_data
        del weights

    plot_args['step_no'] = None
    
    tmin = min(time_data[:, 0])
    tmax = max(time_data[:, 0])
    qmin = min(time_data[:, 1])
    qmax = max(time_data[:, 1])
    
    draw_limits = dict(plot_args['plot_limits'])
    draw_limits['xy_limits'] = [[tmin, tmax], [qmin, qmax]]
    
    return [time_data], draw_limits, plot_options


def update_plot_data(backend, use_old_data=False):
    """
    Reload data and replot, under the assumption that the saved data in backend
    has been changed or updated
    """
    plot_args = dict(backend.plot_args)
    plot_args['use_old_data'] = use_old_data
    
    if backend.plot_args['plot_type'] == 'time':
        (data_list, draw_limits, plot_options) = time_plot_wrapper(**plot_args)
    else:
        (data_list, draw_limits, plot_options) = single_plot_data(**plot_args)
    
    backend.data_list = data_list
    backend.draw_limits = draw_limits
    backend.plot_options = plot_options
    backend.plot_type = backend.plot_args['plot_type']
    
    backend.update_plot()


def single_plot_data(x_axis, x_index, y_axis, y_index, render, render_index,
                     vector, plot_type, z_slice, step_no, cmap, cmap_invert,
                     plot_limits, data_limits, transform_keys, plot_transforms,
                     backend, shared, plot_options=None, use_old_data=False,
                     **kwargs):
    """
    Data for plotting to file or screen
    """
    from . import data
    from . import wrapper_functions
    from . import text_helpers
    from . import transforms
    from . import limits
    from . import analysis
    from . import menu_units
    import numpy as np
    
    draw_limits = dict(plot_limits)
    data_limits = list(data_limits)
    
    # Get fields
    if x_axis is not None:
        x_field = shared.field_mappings[x_axis].field
    if y_axis is not None:
        y_field = shared.field_mappings[y_axis].field
    if render is not None:
        render_field = shared.field_mappings[render].field
    else:
        render_field = None
    if vector is not None:
        vector_field = shared.field_mappings[vector].field
    else:
        vector_field = None
    
    # Get units
    if x_axis is not None:
        x_unit, x_unit_str = menu_units.get_unit(shared, '_'+x_field.name)
    else:
        x_unit, x_unit_str = (1.0, '')
    if y_axis is not None:
        y_unit, y_unit_str = menu_units.get_unit(shared, '_'+y_field.name)
    else:
        y_unit, y_unit_str = (1.0, '')
    if render is not None:
        render_unit, render_unit_str = menu_units.get_unit(
            shared, '_'+render_field.name)
    else:
        render_unit, render_unit_str = (1.0, '')
    if vector is not None:
        vector_unit, vector_unit_str = menu_units.get_unit(
            shared, '_'+render_field.name)
    else:
        vector_unit, vector_unit_str = (1.0, '')
    time_unit, time_unit_str = menu_units.get_unit(shared, 'time')
    sink_mass_unit, sink_mass_unit_str = menu_units.get_unit(
        shared, 'sink_mass')
    position_unit, position_unit_str = menu_units.get_unit(
        shared, '_position')
    velocity_unit, velocity_unit_str = menu_units.get_unit(shared, '_vel')
    
    # Cross section or projection plot?
    if plot_type == 'render':
        proj = (shared.config.get('xsec', 'plot_type') == 'proj')
    
    # Set options for plot (title, axes etc)
    step = shared.sim_step_list[step_no]
    if step.data_set is None:
        # Load data if we do not already have a dataset
        step.load_dataset()
    time = step.time * step.time_mks / time_unit
    if plot_options is None:
        # Set up default plot options
        plot_options = {}
        plot_options['data_axis'] = None
        plot_options['sink_data'] = None
        #plot_options['title'] = 'Plot title here'
        if x_axis is not None:
            x_fm_title = shared.field_mappings[x_axis].title
            plot_options['xlabel'] = (x_fm_title + x_unit_str)
            if plot_transforms['x_transform'] is not None:
                plot_options['xlabel'] = (
                    transform_keys['x_transform'].replace(
                        'x', plot_options['xlabel']))
        if y_axis is not None:
            y_fm_title = shared.field_mappings[y_axis].title
            plot_options['ylabel'] = (y_fm_title + y_unit_str)
            if plot_transforms['y_transform'] is not None:
                plot_options['ylabel'] = (
                    transform_keys['y_transform'].replace(
                        'x', plot_options['ylabel']))
        
        # Time labels
        if plot_type == 'time':
            plot_options['xlabel'] = 'Time [{}]'.format(time_unit_str)
            plot_options['time_label'] = ''
        else:
            rounded_time = text_helpers.round_to_n(time)
            time_string = str(rounded_time) + ' ' + time_unit_str
            plot_options['time_label'] = 't={}'.format(time_string)
        
        # Colourbar options
        if cmap is not None:
            if cmap_invert == 'yes':
                plot_options['cmap'] = cmap + '_r'
            else:
                plot_options['cmap'] = cmap
            if plot_type == 'hist2d':
                plot_options['colourbar'] = True
                plot_options['colourbar_label'] = 'Frequency density'
                if plot_transforms['hist_transform'] is None:
                    plot_options['colourbar_ticks'] = [0.0]
                else:
                    plot_options['colourbar_label'] = (
                        transform_keys['hist_transform'].replace(
                            'x', plot_options['colourbar_label']))
                    plot_options['colourbar_ticks'] = []
            elif plot_type == 'render':
                plot_options['colourbar'] = True
                clabel = shared.field_mappings[render].title
                if proj:
                    c_unit_str = shared.config.get_safe_literal(
                        'units', 'column', default=(1.0,position_unit_str))[1]
                    
                    clabel = (r'\int ' + clabel + r' dz' + ' [' +
                              render_unit_str[2:-1] + r' \times ' +
                              c_unit_str[2:-1] + ']')
                else:
                    clabel = clabel + render_unit_str
                
                plot_options['colourbar_label'] = clabel
                if plot_transforms['render_transform'] is not None:
                    plot_options['colourbar_label'] = (
                        transform_keys['render_transform'].replace(
                            'x', plot_options['colourbar_label']))
            else:
                plot_options['colourbar'] = False
        else:
            plot_options['colourbar'] = False
        
        # Check for position axes
        if plot_type == 'render':
            x_pos = True
            x_pos_index = shared.field_mappings[x_axis].index
            y_pos = True
            y_pos_index = shared.field_mappings[y_axis].index
        elif plot_type == 'hist2d':
            x_flags = shared.field_mappings[x_axis].field.flags
            x_pos = 'position' in x_flags
            x_pos_index = shared.field_mappings[x_axis].index
            y_flags = shared.field_mappings[y_axis].field.flags
            y_pos = 'position' in y_flags
            y_pos_index = shared.field_mappings[y_axis].index
        elif plot_type == 'time':
            x_pos = False
            x_pos_index = 0
            y_flags = shared.field_mappings[y_axis].field.flags
            y_pos = 'position' in y_flags
            y_pos_index = shared.field_mappings[y_axis].index
        else:
            # single axis plot
            y_pos = False
            y_pos_index = 0
            x_flags = shared.field_mappings[x_axis].field.flags
            x_pos = 'position' in x_flags
            x_pos_index = shared.field_mappings[x_axis].index
        plot_options['x_pos'] = x_pos
        plot_options['y_pos'] = y_pos
        
        # Equal scales plot?
        plot_options['aspect'] = 'square_plot'
        if shared.config.get_safe('page', 'equal_scales') == 'on':
            if x_pos and y_pos:
                plot_options['aspect'] = 'equal'
    
        # find box length, set resolution
        if x_pos:
            box_len_x = step.length_mks / x_unit
        else:
            box_len_x = None
        if y_pos:
            box_len_y = step.length_mks / y_unit
        else:
            box_len_y = None
        plot_options['box_length'] = (box_len_x, box_len_y)
        resolution = shared.config.get('render', 'resolution')
        if resolution == 'auto':
            # identify resolution
            plot_options['minmax_res'] = step.minmax_res
            backend_resolution = backend.max_auto_resolution
            dataset_resolution = step.minmax_res[1]
            resolution = min(backend_resolution, dataset_resolution)
        else:
            resolution = int(resolution)
        plot_options['resolution'] = resolution
        
        # Deal with sink data, if present and if we are using it
        if plot_type == 'render':
            if (shared.config.get_safe('opts', 'show_sinks') == 'on'):
                sink_data = np.array(step.sink_data)
                sink_options = {}
                sink_data['age'] = (sink_data['age'] * step.time_mks /
                                     time_unit)
                sink_x = (sink_data['position'][:, x_index] *
                          step.length_mks / (box_len_x * x_unit))
                sink_y = (sink_data['position'][:, y_index] *
                          step.length_mks / (box_len_y * y_unit))
                if plot_transforms['x_transform'] is not None:
                    sink_x[:] = plot_transforms['x_transform'][0](sink_x)
                if plot_transforms['y_transform'] is not None:
                    sink_y[:] = plot_transforms['y_transform'][0](sink_y)
                
                if x_unit != y_unit:
                    raise AssertionError('x_unit != y_unit for rendered plot!')
                sink_data['position'] = (sink_data['position']*step.length_mks /
                                         (step.box_length * position_unit))
                sink_data['velocity'] = (sink_data['velocity'] *
                                         step.velocity_mks / velocity_unit)
                sink_data['mass'] = (sink_data['mass'] * step.sink_mass_mks /
                                     sink_mass_unit)
                plot_options['sink_data'] = sink_data
                sink_options['sink_xy'] = (sink_x, sink_y)
                sink_options['mass_str'] = sink_mass_unit_str
                sink_options['age_str'] = time_unit_str
                sink_options['position_str'] = position_unit_str
                sink_options['velocity_str'] = velocity_unit_str
                plot_options['sink_options'] = sink_options
    
    # We now have a set of plot options (cached or newly created), set up plots
    x_pos = plot_options['x_pos']
    y_pos = plot_options['y_pos']
    box_length = plot_options['box_length']
    minmax_res = plot_options['minmax_res']
    resolution = plot_options['resolution']
    
    # Plot limits
    if x_pos:
        xlim = [0.0, box_length[0]]
        if plot_limits['x_axis'][0] != 'auto':
            xlim[0] = plot_limits['x_axis'][0]
        if plot_limits['x_axis'][1] != 'auto':
            xlim[1] = plot_limits['x_axis'][1]
        
    if y_pos:
        ylim = [0.0, box_length[1]]
        if plot_limits['y_axis'][0] != 'auto':
            ylim[0] = plot_limits['y_axis'][0]
        if plot_limits['y_axis'][1] != 'auto':
            ylim[1] = plot_limits['y_axis'][1]
    
    # Adjust limits if we are (approximately) maintaining an aspect ratio
    if (shared.config.get('limits', 'aspect_ratio') == 'on' and
        x_pos and y_pos):
        x_len = xlim[1] - xlim[0]
        y_len = ylim[1] - ylim[0]
        if x_len > y_len and x_len <= box_length[1]:
            y_centre = 0.5 * (ylim[1] + ylim[0])
            ylim[0] = max(0.0, y_centre - 0.5*x_len)
            ylim[1] = max(x_len, y_centre + 0.5*x_len)
            ylim[0] = min(ylim[0], box_length[0] - x_len)
            ylim[1] = min(ylim[1], box_length[0])
        elif y_len > x_len and y_len <= box_length[0]:
            x_centre = 0.5 * (xlim[1] + xlim[0])
            xlim[0] = max(0.0, x_centre - 0.5*y_len)
            xlim[1] = max(y_len, x_centre + 0.5*y_len)
            xlim[0] = min(xlim[0], box_length[0] - y_len)
            xlim[1] = min(xlim[1], box_length[0])
    
    # Snap position limits to grid
    if x_pos:
        xlim_snap = limits.snap_to_grid(xlim, None, True, False,
                                        box_length, minmax_res)[0]
        draw_limits['x_axis'] = xlim_snap
    
    if y_pos:
        ylim_snap = limits.snap_to_grid(None, ylim, False, True,
                                        box_length, minmax_res)[1]
        draw_limits['y_axis'] = ylim_snap
    
    # Get data
    if plot_type == 'hist2d':
        if use_old_data:
            data_list_pass = backend.data_list
        else:
            data_list_pass = None
        # Data from analysis function
        data_list, xy_limits = analysis.get_histogram2d(
            x_field, x_index, x_unit, x_pos,
            y_field, y_index, y_unit, y_pos,
            resolution, plot_transforms,
            draw_limits, data_limits, step, shared, data_list_pass)
        
        draw_limits['xy_limits'] = xy_limits
        plot_options['plot_type'] = 'hist2d'
        
        ret_tuple = (data_list, draw_limits, plot_options)
        
    elif plot_type == 'render':
        # Data from analysis function
        
        if use_old_data:
            data_list_pass = backend.data_list
        else:
            data_list_pass = None
        data_list, xy_limits, render_limits = analysis.get_render_plot(
                x_field, x_index, x_unit,
                y_field, y_index, y_unit,
                render_field, render_index, render_unit,
                vector_field, vector_unit, proj, z_slice,
                resolution, plot_transforms, draw_limits,
                data_limits, step, shared, data_list_pass)
        
        draw_limits['xy_limits'] = xy_limits
        draw_limits['render'] = render_limits
        plot_options['plot_type'] = 'render'
        
        ret_tuple = (data_list, draw_limits, plot_options)
    elif plot_type == 'time':
        # Data from analysis function
        cell_data, weights = analysis.get_single_data(
            y_field, y_index, y_unit, plot_transforms['y_transform'],
            data_limits, step, shared)
        
        plot_options['plot_type'] = 'time'
        
        ret_tuple = ([time, cell_data, weights], plot_options)
    else:
        # Data for general-purpose analysis function; see get_analysis_list
        # in analysis.py
        if plot_type.properties['data_type'] == 'cell_data':
        
            data_array, weights = analysis.get_single_data(
                    x_field, x_index, x_unit, plot_transforms['x_transform'],
                    data_limits, step, shared)
        
        elif plot_type.properties['data_type'] == 'sample_data':
            
            data_array, weights = analysis.get_box_data(
                x_field, x_index, x_unit, resolution,
                plot_transforms['x_transform'], data_limits, step, shared)
        else:
            raise ValueError('Unknown plot type!')
        
        data_list = plot_type.func(data_array, weights, shared)
        
        props = plot_type.properties
        plot_options['plot_type'] = plot_type
        #plot_options['plot_type'] = props['plot_type']
        if 'title' in props:
            plot_options['title'] = props['title']
        if 'xlabel' in props:
            plot_options['xlabel'] = props['xlabel']
        if 'xticks' in props:
            plot_options['xticks'] = props['xticks']
        if 'ylabel' in props:
            plot_options['ylabel'] = props['ylabel']
        if 'yticks' in props:
            plot_options['yticks'] = props['yticks']
        
        if ('data_axis' in props) and (props['data_axis'] is not None):
                x_fm_title = shared.field_mappings[x_axis].title
                label = (x_fm_title + x_unit_str)
                if plot_transforms['x_transform'] is not None:
                    label = transform_keys['x_transform'].replace(
                        'x', label)
                if props['data_axis'] == 'x':
                    plot_options['xlabel'] = label
                    plot_options['data_axis'] = 'x'
                elif props['data_axis'] == 'y':
                    plot_options['ylabel'] = label
                    plot_options['data_axis'] = 'y'
        else:
            plot_options['data_axis'] = None
        
        draw_limits['xy_limits'] = [['auto', 'auto'], ['auto', 'auto']]
        
        if plot_options['data_axis'] != 'x':
            qx_transform = plot_transforms['qx_transform']
        else:
            qx_transform = None
            draw_limits['xy_limits'][0] = plot_limits['x_axis']
        
        if plot_options['data_axis'] != 'y':
            qy_transform = plot_transforms['qy_transform']
        else:
            qy_transform = None
            draw_limits['xy_limits'][1] = plot_limits['y_axis']
        
        if qx_transform is None:
            pass
        elif (qx_transform[0] is np.log10 and not ('xticks' in props and
                not props['xticks'])):
            pass # special treatment
        else:
            plot_options['xlabel'] = (
                transform_keys['qx_transform'].replace(
                    'x', plot_options['xlabel']))
        
        if qy_transform is None:
            pass
        elif (qy_transform[0] is np.log10 and not ('yticks' in props and
                not props['yticks'])):
            pass # special treatment
        else:
            plot_options['ylabel'] = (
                transform_keys['qy_transform'].replace(
                    'x', plot_options['ylabel']))
        
        ret_tuple = (data_list, draw_limits, plot_options)

    return ret_tuple

