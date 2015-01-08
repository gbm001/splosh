"""
This submodule implements the units submenu.
"""

from __future__ import print_function

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass


def get_unit(shared, unit_name):
    """
    Get a single unit (unit and string) - helper function
    """
    if (shared.config.get_safe('data', 'use_units') != 'off'):
        unit_val, unit_str = shared.config.get_safe_literal('units', unit_name,
                                                            default=(1.0, ''))
        if unit_str:
            unit_str = ' [' + unit_str + ']'
    else:
        unit_val = 1.0
        unit_str = ''
    
    return unit_val, unit_str


def set_units(shared, *args):
    """
    Manually set units
    """
    from numpy import isfinite
    
    fields = []
    fields.extend(shared.fields_list)
    
    for fm in shared.field_mappings:
        if fm.extra is not None:
            fields.append(fm.field)
    
    while True:
        # Print current limits
        print_units(shared, fields)
        
        # Take an input (select a limit):
        prompt = 'Select a unit to change (press enter to exit): '
        input_string = input(prompt).strip()
        if not input_string:
            return
        if not (input_string.isdigit() or input_string == '-1' or
                input_string == '-2'):
            print(' >> Invalid input string!')
            continue
        unit_index = int(input_string)
        if not (-2 <= unit_index <= len(fields)):
            print(' >> Invalid choice!')
            continue
        
        # Find existing limits
        if unit_index == -1:
            val, unit_str = shared.config.get_safe_literal('units', 'column',
                                                           default=('SAME', ''))
            prompt = ("Enter multiplier (number to multiply values by),\n"
                      "or SAME to use same units as x/y/z "
                      "[default={}]: ".format(val))
            
        else:
            if unit_index == -2:
                val, unit_str = shared.config.get_safe_literal(
                    'units', 'sink_mass', default=(1.0, ''))
            elif unit_index == 0:
                val, unit_str = shared.config.get_safe_literal(
                    'units', 'time', default=(1.0, ''))
            else:
                field = fields[unit_index - 1]
                val, unit_str = shared.config.get_safe_literal(
                    'units', '_'+field.name, default=(1.0, ''))
            prompt = ("Enter multiplier (number to multiply values by) "
                      "[default={}]: ".format(val))
        
        while True:
            input_string = input(prompt).strip()
            if not input_string:
                if unit_index == -1 and val == 'SAME':
                    shared.config.remove_safe('units', 'column')
                    return
                else:
                    new_val = val
                    break
            if unit_index == -1 and input_string == 'SAME':
                shared.config.remove_safe('units', 'column')
                return
            try:
                new_val = float(input_string)
            except ValueError:
                print(' >> Not a valid number!')
                continue
            if not isfinite(new_val):
                print(' >> Not a valid number!')
                continue
            break
        
        prompt = ("Enter unit suffix string or NONE for blank "
                  "[default={}]: ".format(unit_str))
        input_string = input(prompt).strip()
        if not input_string:
            new_unit_str = unit_str
        elif input_string == 'NONE':
            new_unit_str = ''
        else:
            new_unit_str = input_string
        
        # Save new limits to configparser
        new_unit_tuple_str = repr((new_val, new_unit_str))
        if unit_index == -2:
            shared.config.set('units', 'sink_mass', new_unit_tuple_str)
        elif unit_index == -1:
            shared.config.set('units', 'column', new_unit_tuple_str)
        elif unit_index == 0:
            shared.config.set('units', 'time', new_unit_tuple_str)
        else:
            shared.config.set('units', '_'+field.name, new_unit_tuple_str)
    
    return


def print_units(shared, fields):
    """
    Print the current list of plot or data limits to the screen
    """
    from .interactive import window_width
    field_width = (window_width / 2)
    titles = []
    val_strs = []
    unit_strs = []
    
    opt_width = len(str(len(fields))) + 3
    opt_width = max(opt_width, 5)
    
    titles.append('sink mass')
    val, unit_str = shared.config.get_safe_literal('units', 'sink_mass',
                                                   default=(1.0, 'NONE'))
    val_strs.append(str(val))
    unit_strs.append(unit_str)
    
    titles.append('integrated column length')
    val, unit_str = shared.config.get_safe_literal(
        'units', 'column', default=('same as x/y/z', 'NONE'))
    val_strs.append(str(val))
    unit_strs.append(unit_str)
    
    titles.append('time')
    val, unit_str = shared.config.get_safe_literal(
        'units', 'time', default=(1.0, 'NONE'))
    val_strs.append(str(val))
    unit_strs.append(unit_str)
    
    for field in fields:
        if field.name == 'position':
            name = 'x/y/z'
        else:
            name = field.name
        titles.append(name)
        val, unit_str = shared.config.get_safe_literal(
            'units', '_' + field.name, default=(1.0, 'NONE'))
        val_strs.append(str(val))
        unit_strs.append(unit_str)
    
    # Find the maximum length (limits to field_width) of titles,
    # and then maximum min/max length, limited to
    # (window_width - field_width - punctuation length) /2
    max_length_titles = max(len(x) for x in titles)
    title_len = min(field_width, max_length_titles)
    min_max_width = (window_width - title_len - 13) / 2
    max_length_val_strs = max(len(x) for x in val_strs)
    max_length_unit_strs = max(len(x) for x in unit_strs)
    min_max_len = max(max_length_val_strs, max_length_unit_strs)
    min_max_len = min(min_max_len, min_max_width)
    
    print('Units ( multiplier : unit suffix )')
    
    for i in range(len(titles)):
        title = titles[i].ljust(title_len)
        val_str = val_strs[i].ljust(min_max_len)
        unit_str = unit_strs[i].ljust(min_max_len)
        opt_no = '({})'.format(i-2).ljust(opt_width)
        print(' {}{} : ( {} : {} )'.format(opt_no, title, val_str, unit_str))
    
    return


def reset_units(shared, *args):
    """
    Remove all units from the 'units' section
    """
    shared.config.remove_section('units')
    shared.config.add_section('units')
    
    return


def post_units_flip(shared, *args):
    import numpy as np
    """
    After 'use_units' option has been changed, reset last_z_slice
    """
    
    first_step = shared.sim_step_list[0]
    
    box_max = np.ones((shared.ndim,))
    x_unit, x_unit_str = shared.config.get_safe_literal('units', '_position',
                                                        default=(1.0, ''))
    if (shared.config.get_safe('data', 'use_units') != 'off'):
        shared.temp_config['last_z_slice'] = (
            box_max * first_step.length_mks / (2.0 * x_unit))
    else:
        shared.temp_config['last_z_slice'] = first_step.box_length / 2.0
    
    return
