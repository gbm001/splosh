"""
This submodule implements limits.
"""

import ast
import numpy as np


def set_current_limits(x_axis, y_axis, render, vector, plot_limits, shared):
    """
    Given a set of limits from a current plot, save to config
    """
    
    coord_changed = False
    quantity_changed = False
    
    # x axis limits
    x_title = shared.field_mappings[x_axis].title
    if shared.limits.has_option('limits', x_title):
        # existing limits
        limits_string = shared.limits.get('limits', x_title)
        old_x_limits = ast.literal_eval(limits_string)
        if not np.allclose(old_x_limits != plot_limits['x_axis']):
            # set new limits
            shared.limits.set('limits', x_title, repr(plot_limits['x_axis']))
            coord_changed = True
    else:
        # no existing limits
        if not plot_limits['x_axis'] == ('auto', 'auto'):
            # set new limits
            shared.limits.set('limits', x_title, repr(plot_limits['x_axis']))
            coord_changed = True
    
    # y axis limits
    y_title = shared.field_mappings[y_axis].title
    if shared.limits.has_option('limits', y_title):
        # existing limits
        limits_string = shared.limits.get('limits', y_title)
        old_y_limits = ast.literal_eval(limits_string)
        if not np.allclose(old_y_limits, plot_limits['y_axis']):
            # set new limits
            shared.limits.set('limits', y_title, repr(plot_limits['y_axis']))
            coord_changed = True
    else:
        # no existing limits
        if not plot_limits['y_axis'] == ('auto', 'auto'):
            # set new limits
            shared.limits.set('limits', y_title, repr(plot_limits['y_axis']))
            coord_changed = True
    
    # render axis limits
    if render is not None:
        render_title = shared.field_mappings[render].title
        if shared.limits.has_option('limits', render_title):
            # existing limits
            limits_string = shared.limits.get('limits', render_title)
            old_render_limits = ast.literal_eval(limits_string)
            if not np.allclose(old_render_limits, plot_limits['render']):
                # set new limits
                shared.limits.set('limits', render_title,
                                  repr(plot_limits['render']))
                quantity_changed = True
        else:
            # no existing limits
            if not plot_limits['render'] == ('auto', 'auto'):
                # set new limits
                shared.limits.set('limits', render_title,
                                  repr(plot_limits['render']))
                quantity_changed = True
    
    # vector limits
    if vector is not None:
        vector_title = shared.field_mappings[vector].title
        if shared.limits.has_option('limits', vector_title):
            # existing limits
            limits_string = shared.limits.get('limits', vector_title)
            old_vector_limits = ast.literal_eval(limits_string)
            if not np.allclose(old_vector_limits, plot_limits['vector']):
                # set new limits
                shared.limits.set('limits', vector_title,
                                  repr(plot_limits['vector']))
                quantity_changed = True
        else:
            # no existing limits
            if not plot_limits['vector'] == ('auto', 'auto'):
                # set new limits
                shared.limits.set('limits', vector_title,
                                  repr(plot_limits['vector']))
                quantity_changed = True
    
    if coord_changed:
        shared.config.set('limits', 'adaptive_coords', 'fixed')
    if quantity_changed:
        shared.config.set('limits', 'adaptive', 'fixed')

def get_current_limits(x_axis, x_index, y_axis, y_index, render,
                        render_index, vector, shared):
    """
    Find the current limits, based on options set and limits in use
    """
    
    plot_limits = {'x_axis': ('auto', 'auto'), 'y_axis': ('auto', 'auto'),
                    'render': ('auto', 'auto'), 'vector': ('auto', 'auto')}
    data_limits = []
    
    # Obtain options
    option = shared.config.get('limits', 'adaptive')
    adaptive = True if option=='adapt' else False
    
    option = shared.config.get('limits', 'adaptive_coords')
    adaptive_coords = True if option=='adapt' else False
    
    option = shared.config.get('limits', 'filter_all')
    filter_all = True if option=='on' else False
    
    #option = shared.config.get('xsec', 'plot_type')
    #projection = True if option=='proj' else False
    
    # Plot limits
    if not adaptive_coords:
        if x_axis is not None:
            x_title = shared.field_mappings[x_axis].title
            if shared.limits.has_option('limits', x_title):
                limits_string = shared.limits.get('limits', x_title)
                plot_limits['x_axis'] = ast.literal_eval(limits_string)
        if y_axis is not None:
            y_title = shared.field_mappings[y_axis].title
            if shared.limits.has_option('limits', y_title):
                limits_string = shared.limits.get('limits', y_title)
                plot_limits['y_axis'] = ast.literal_eval(limits_string)
    
    if render is not None:
        r_title = shared.field_mappings[render].title
        if shared.limits.has_option('limits', r_title):
            limits_string = shared.limits.get('limits', r_title)
            plot_limits['render'] = ast.literal_eval(limits_string)

    if vector is not None:
        v_title = shared.field_mappings[vector].title
        if shared.limits.has_option('limits', v_title):
            limits_string = shared.limits.get('limits', v_title)
            plot_limits['vector'] = ast.literal_eval(limits_string)
    
    # Data limits
    if filter_all:
        for i, field_mapping in enumerate(shared.field_mappings):
            f_title = shared.field_mappings[i].title
            if shared.limits.has_option('restrict', f_title):
                f_limits_str = shared.limits.get('restrict', f_title)
                f_limits = ast.literal_eval(f_limits_str)
                field = shared.field_mappings[i].field
                f_name = shared.field_mappings[i].field.name
                f_index = shared.field_mappings[i].index
                f_width = shared.field_mappings[i].field.width
                data_limits.append({'name': f_name,
                                    'field': field,
                                    'index': f_index,
                                    'limits': f_limits,
                                    'width': f_width})
    
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
        dx = (xlim[1] - xlim[0]) / box_length[0]
        idx = 1.0 / dx # box_length[0] / (xlim[1] - xlim[0])
        x_level = np.floor(np.log2(idx)).astype(int)
        x_snap = min(coarse_grid * 2**x_level, fine_grid)
        #x_scaled = np.array(xlim) / box_length[0]
        #x_new_lim = box_length[0] * np.rint(x_scaled * x_snap) / x_snap
        dx_snap = box_length[0] / x_snap
        x_min = dx_snap * np.rint(xlim[0] * x_snap / box_length[0])
        x_len = dx_snap * max(np.rint(dx * x_snap), min_cells)
        x_min = min(x_min, box_length[0] - x_len)
        x_new_lim = (x_min, x_min + x_len)
    else:
        x_new_lim = None
    
    if y_pos:
        dy = (ylim[1] - ylim[0]) / box_length[1]
        idy = 1.0 / dy # box_length[0] / (ylim[1] - ylim[0])
        y_level = np.floor(np.log2(idy)).astype(int)
        y_snap = min(coarse_grid * 2**y_level, fine_grid)
        #y_scaled = np.array(ylim) / box_length[1]
        #y_new_lim = box_length[1] * np.rint(y_scaled * y_snap) / y_snap
        dy_snap = box_length[1] / y_snap
        y_min = dy_snap * np.rint(ylim[0] * y_snap / box_length[1])
        y_len = dy_snap * max(np.rint(dy * y_snap), min_cells)
        y_min = min(y_min, box_length[1] - y_len)
        y_new_lim = (y_min, y_min + y_len)
    else:
        y_new_lim = None
    
    return x_new_lim, y_new_lim        
    
    
    