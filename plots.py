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
                shared)
            
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
            shared)
        
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
        None, None, axis, index, None, None, None, shared)
    
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
    import numpy as np
    import ast
    
    draw_limits = dict(plot_limits)
    data_limits = list(data_limits)
    
    # Get fields and test for units
    if x_axis is not None:
        x_field = shared.field_mappings[x_axis].field
        has_x_unit = shared.config.has_option('units', '_'+x_field.name)
    else:
        has_x_unit = False
    if y_axis is not None:
        y_field = shared.field_mappings[y_axis].field
        has_y_unit = shared.config.has_option('units', '_'+y_field.name)
    else:
        has_y_unit = False
    if render is not None:
        render_field = shared.field_mappings[render].field
        has_render_unit = shared.config.has_option(
            'units', '_'+render_field.name)
    else:
        has_render_unit = False
    if vector is not None:
        vector_field = shared.field_mappings[vector].field
        has_vector_unit = shared.config.has_option(
            'units', '_'+vector_field.name)
    else:
        vector_field = None
        has_vector_unit = False
    has_time_unit = shared.config.has_option('units', 'time')
    if shared.config.get('data', 'use_units') == 'OFF':
        has_x_unit = False
        has_y_unit = False
        has_render_unit = False
        has_vector_unit = False
        has_time_unit = False
    
    # Get units
    if has_x_unit and x_axis is not None:
        unit_tuple_str = shared.config.get('units', '_'+x_field.name)
        x_unit, x_unit_str = ast.literal_eval(unit_tuple_str)
        x_unit_str = ' [' + x_unit_str + ']'
    else:
        x_unit = 1.0
        x_unit_str = ''
    if has_y_unit and y_axis is not None:
        unit_tuple_str = shared.config.get('units', '_'+y_field.name)
        y_unit, y_unit_str = ast.literal_eval(unit_tuple_str)
        y_unit_str = ' [' + y_unit_str + ']'
    else:
        y_unit = 1.0
        y_unit_str = ''
    if has_render_unit:
        unit_tuple_str = shared.config.get('units', '_'+render_field.name)
        render_unit, render_unit_str = ast.literal_eval(unit_tuple_str)
    else:
        render_unit = 1.0
        render_unit_str = ''
    if has_vector_unit:
        unit_tuple_str = shared.config.get('units', '_'+vector_field.name)
        vector_unit, vector_unit_str = ast.literal_eval(unit_tuple_str)
        vector_unit_str = ' [' + vector_unit_str + ']'
    else:
        vector_unit = 1.0
        vector_unit_str = ''
    if has_time_unit:
        unit_tuple_str = shared.config.get('units', 'time')
        time_unit, time_unit_str = ast.literal_eval(unit_tuple_str)
    else:
        time_unit = 1.0
        time_unit_str = ''
    
    if plot_type == 'render':
        proj = (shared.config.get('xsec', 'plot_type') == 'proj')
    
    # Set options for plot (title, axes etc)
    step = shared.sim_step_list[step_no]
    if step.data_set is None:
        step.load_dataset()
    time = step.time * step.time_mks / time_unit
    if plot_options is None:
        plot_options = {}
        plot_options['data_axis'] = None
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
        
        if plot_type == 'time':
            plot_options['xlabel'] = 'Time [{}]'.format(time_unit_str)
            plot_options['time_label'] = ''
        else:
            rounded_time = text_helpers.round_to_n(time)
            time_string = str(rounded_time) + ' ' + time_unit_str
            plot_options['time_label'] = 't={}'.format(time_string)
        
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
                    if shared.config.has_option('units', 'column'):
                        unit_tuple_str = shared.config.get('units', 'column')
                        c_unit_str = ast.literal_eval(unit_tuple_str)[1]
                    else:
                        c_unit_str = render_unit_str
                    
                    clabel = (r'\int ' + clabel + r' dz' + ' [' +
                              render_unit_str + r' \times ' + c_unit_str + ']')
                else:
                    clabel = clabel + '[' + render_unit_str + ']'
                
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
        
        plot_options['aspect'] = 'square_plot'
        if shared.config.get('page', 'equal_scales') == 'on':
            if x_pos and y_pos:
                plot_options['aspect'] = 'equal'
    
        # find box length
        if x_pos:
            box_len_x = step.box_length[x_pos_index] * step.length_mks
            if has_x_unit:
                box_len_x = box_len_x / x_unit
        else:
            box_len_x = None
        if y_pos:
            box_len_y = step.box_length[y_pos_index] * step.length_mks
            if has_y_unit:
                box_len_y = box_len_y / y_unit
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
    
    x_pos = plot_options['x_pos']
    y_pos = plot_options['y_pos']
    box_length = plot_options['box_length']
    minmax_res = plot_options['minmax_res']
    resolution = plot_options['resolution']
    
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
    
    if x_pos:
        xlim_snap = limits.snap_to_grid(xlim, None, True, False,
                                        box_length, minmax_res)[0]
        draw_limits['x_axis'] = xlim_snap
        
        xdata = list(xlim)
        dx_res = box_length[0] / minmax_res[0]
        xdata[0] = min(xlim_snap[0], xlim[0])
        xdata[1] = max(xlim_snap[1], xlim[1])
        xdata[0] = max(0.0, xdata[0] - 1.1*dx_res)
        xdata[1] = min(box_length[0], xdata[1] + 1.1*dx_res)
        data_limits.append({'name': x_field.name,
                            'field': x_field,
                            'width': x_field.width,
                            'index': x_index,
                            'limits': xdata})
    
    if y_pos:
        ylim_snap = limits.snap_to_grid(None, ylim, False, True,
                                        box_length, minmax_res)[1]
        draw_limits['y_axis'] = ylim_snap
        
        ydata = list(ylim)
        dy_res = box_length[1] / minmax_res[0]
        ydata[0] = min(ylim_snap[0], ylim[0])
        ydata[1] = max(ylim_snap[1], ylim[1])
        ydata[0] = max(0.0, ydata[0] - 1.1*dy_res)
        ydata[1] = min(box_length[1], ydata[1] + 1.1*dy_res)
        data_limits.append({'name': y_field.name,
                            'field': y_field,
                            'width': x_field.width,
                            'index': y_index,
                            'limits': ydata})
    
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
        
        data_list = plot_type.func(data_array, weights)
        
        props = plot_type.properties
        plot_options['plot_type'] = props['plot_type']
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
        
        draw_limits['xy_limits'] = None
        
        if plot_options['data_axis'] != 'x':
            qx_transform = plot_transforms['qx_transform']
        else:
            qx_transform = None
        if plot_options['data_axis'] != 'y':
            qy_transform = plot_transforms['qy_transform']
        else:
            qy_transform = None
        
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









