"""
This submodule implements limits.
"""

import numpy as np


def set_current_limits(x_axis, y_axis, render, vector,
                       plot_limits, plot_type, shared):
    """
    Given a set of limits from a current plot, save to config
    """
    
    coord_changed = False
    quantity_changed = False
    
    if hasattr(plot_type, 'limits'):
        special_limits = plot_type.properties['special_limits']
    else:
        special_limits = [False, False]
    
    # x axis limits
    if special_limits[0]:
        if not plot_limits['x_axis'] == ['auto', 'auto']:
            plot_type.limits[0] = plot_limits['x_axis']
            coord_changed = True
    else:
        x_title = shared.field_mappings[x_axis].title
        if shared.limits.has_option('limits', x_title):
            # existing limits
            old_x_limits = shared.limits.get_literal('limits', x_title)
            if not np.allclose(old_x_limits, plot_limits['x_axis']):
                # set new limits
                shared.limits.set('limits', x_title, repr(plot_limits['x_axis']))
                coord_changed = True
        else:
            # no existing limits
            if not plot_limits['x_axis'] == ['auto', 'auto']:
                # set new limits
                shared.limits.set('limits', x_title, repr(plot_limits['x_axis']))
                coord_changed = True
    
    # y axis limits
    if special_limits[1]:
        if not plot_limits['y_axis'] == ['auto', 'auto']:
            plot_type.limits[1] = plot_limits['y_axis']
            coord_changed = True
    else:
        y_title = shared.field_mappings[y_axis].title
        if shared.limits.has_option('limits', y_title):
            # existing limits
            old_y_limits = shared.limits.get_literal('limits', y_title)
            if not np.allclose(old_y_limits, plot_limits['y_axis']):
                # set new limits
                shared.limits.set('limits', y_title, repr(plot_limits['y_axis']))
                coord_changed = True
        else:
            # no existing limits
            if not plot_limits['y_axis'] == ['auto', 'auto']:
                # set new limits
                shared.limits.set('limits', y_title, repr(plot_limits['y_axis']))
                coord_changed = True
    
    # render axis limits
    if render is not None:
        render_title = shared.field_mappings[render].title
        if shared.limits.has_option('limits', render_title):
            # existing limits
            old_render_limits = shared.limits.get_literal(
                'limits', render_title)
            if not np.allclose(old_render_limits, plot_limits['render']):
                # set new limits
                shared.limits.set('limits', render_title,
                                  repr(plot_limits['render']))
                quantity_changed = True
        else:
            # no existing limits
            if not plot_limits['render'] == ['auto', 'auto']:
                # set new limits
                shared.limits.set('limits', render_title,
                                  repr(plot_limits['render']))
                quantity_changed = True
    
    # vector limits
    if vector is not None:
        vector_title = shared.field_mappings[vector].title
        if shared.limits.has_option('limits', vector_title):
            # existing limits
            old_vector_limits = shared.limits.get_literal(
                'limits', vector_title)
            if not np.allclose(old_vector_limits, plot_limits['vector']):
                # set new limits
                shared.limits.set('limits', vector_title,
                                  repr(plot_limits['vector']))
                quantity_changed = True
        else:
            # no existing limits
            if not plot_limits['vector'] == ['auto', 'auto']:
                # set new limits
                shared.limits.set('limits', vector_title,
                                  repr(plot_limits['vector']))
                quantity_changed = True
    
    if coord_changed:
        shared.config.set('limits', 'adaptive_coords', 'fixed')
    if quantity_changed:
        shared.config.set('limits', 'adaptive', 'fixed')


def get_current_limits(x_axis, x_index, y_axis, y_index, render,
                        render_index, vector, plot_type, shared):
    """
    Find the current limits, based on options set and limits in use
    """
    
    plot_limits = {'x_axis': ['auto', 'auto'], 'y_axis': ['auto', 'auto'],
                    'render': ['auto', 'auto'], 'vector': ['auto', 'auto']}
    data_limits = []
    
    # Obtain options
    option = shared.config.get('limits', 'adaptive')
    adaptive = True if option=='adapt' else False
    
    option = shared.config.get('limits', 'adaptive_coords')
    adaptive_coords = True if option=='adapt' else False
    
    option = shared.config.get('limits', 'filter_all')
    filter_all = True if option=='on' else False
    
    # Plot limits
    if not adaptive_coords:
        if x_axis is not None:
            x_title = shared.field_mappings[x_axis].title
            plot_limits['x_axis'] = shared.limits.get_safe_literal(
                'limits', x_title, default=plot_limits['x_axis'])
        if y_axis is not None:
            y_title = shared.field_mappings[y_axis].title
            plot_limits['y_axis'] = shared.limits.get_safe_literal(
                'limits', y_title, default=plot_limits['y_axis'])
    
    if render is not None:
        r_title = shared.field_mappings[render].title
        plot_limits['render'] = shared.limits.get_safe_literal(
            'limits', r_title, default=plot_limits['render'])

    if vector is not None:
        v_title = shared.field_mappings[vector].title
        plot_limits['vector'] = shared.limits.get_literal(
            'limits', v_title, default=plot_limits['vector'])
    
    # Data limits
    if filter_all:
        for i, field_mapping in enumerate(shared.field_mappings):
            f_title = shared.field_mappings[i].title
            if shared.limits.has_option('restrict', f_title):
                f_limits = list(shared.limits.get_literal('restrict', f_title))
                field = shared.field_mappings[i].field
                f_name = shared.field_mappings[i].field.name
                f_index = shared.field_mappings[i].index
                f_width = shared.field_mappings[i].field.width
                if (shared.config.get_safe('data', 'use_units') == 'on' and
                        shared.config.has_option('units', '_' + field.name)):
                    unit, unit_str = shared.config.get_literal('units',
                                                               '_'+field.name)
                    if f_limits[0] != 'none':
                        f_limits[0] = f_limits[0] * unit
                    if f_limits[1] != 'none':
                        f_limits[1] = f_limits[1] * unit
                data_limits.append({'name': f_name,
                                    'field': field,
                                    'index': f_index,
                                    'limits': f_limits,
                                    'width': f_width})
    
    if hasattr(plot_type, 'limits'):
        special_limits = plot_type.properties['special_limits']
        if special_limits[0]:
            plot_limits['x_axis'] = plot_type.limits[0]
        if special_limits[1]:
            plot_limits['y_axis'] = plot_type.limits[1]
    
    return plot_limits, data_limits


def snap_to_grid(xlim, ylim, x_pos, y_pos, box_length, minmax_res):
    """
    Given x and/or y limits for position axes, snap to grid...
    """
    
    # Get minimum and maximum resolution
    coarse_grid = minmax_res[0]
    fine_grid = minmax_res[1]
    min_cells = 4.0
    
    if x_pos:
        xlim_sc = np.array(xlim) / box_length[0]
        dx = xlim_sc[1] - xlim_sc[0]
        idx = 1.0 / dx
        x_level = np.floor(np.log2(idx)).astype(int)
        x_snap = min(coarse_grid * 2**x_level, fine_grid)
        dx_snap = 1.0 / x_snap
        x_min = dx_snap * np.rint(xlim_sc[0] * x_snap)
        x_len = dx_snap * max(np.rint(dx * x_snap), min_cells)
        x_min = min(x_min, 1.0 - x_len)
        x_new_lim = (x_min * box_length[0], (x_min + x_len) * box_length[0])
    else:
        x_new_lim = None
    
    if y_pos:
        ylim_sc = np.array(ylim) / box_length[1]
        dy = ylim_sc[1] - ylim_sc[0]
        idy = 1.0 / dy
        y_level = np.floor(np.log2(idy)).astype(int)
        y_snap = min(coarse_grid * 2**y_level, fine_grid)
        dy_snap = 1.0 / y_snap
        y_min = dy_snap * np.rint(ylim_sc[0] * y_snap)
        y_len = dy_snap * max(np.rint(dy * y_snap), min_cells)
        y_min = min(y_min, 1.0 - y_len)
        y_new_lim = (y_min * box_length[1], (y_min + y_len) * box_length[1])
    else:
        y_new_lim = None
    
    return x_new_lim, y_new_lim        
    
    
    