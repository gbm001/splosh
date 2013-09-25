"""
This submodule implements the units submenu.
"""

from __future__ import print_function
import ast

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass


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
        if not input_string.isdigit():
            print(' >> Invalid input string!')
            continue
        unit_index = int(input_string)
        if not (0 <= unit_index <= len(fields)):
            print(' >> Invalid choice!')
            continue
        
        # Find existing limits
        if unit_index == 0:
            if shared.config.has_option('units', 'time'):
                unit_tuple_str = shared.config.get('units', 'time')
                val, unit_str = ast.literal_eval(unit_tuple_str)
            else:
                val = 1.0
                unit_str = ''
        else:
            field = fields[unit_index - 1]
            if shared.config.has_option('units', '_'+field.name):
                unit_tuple_str = shared.config.get('units', '_'+field.name)
                val, unit_str = ast.literal_eval(unit_tuple_str)
            else:
                val = 1.0
                unit_str = ''
        
        # Offer to change limit
        prompt = ("Enter multiplier (number to multiply values by) "
                  "[default={}]: ".format(val))
        while True:
            input_string = input(prompt).strip()
            if not input_string:
                new_val = val
                break
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
        if unit_index == 0:
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
    
    titles.append('time')
    if shared.config.has_option('units', 'time'):
        unit_tuple_str = shared.config.get('units', 'time')
        val, unit_str = ast.literal_eval(unit_tuple_str)
        val_strs.append(str(val))
        unit_strs.append(unit_str)
    else:
        val_strs.append('1.0')
        unit_strs.append('NONE')
    
    for field in fields:
        if field.name == 'position':
            name = 'x/y/z'
        else:
            name = field.name
        titles.append(name)
        if shared.config.has_option('units', '_' + field.name):
            unit_tuple_str = shared.config.get('units', '_' + field.name)
            val, unit_str = ast.literal_eval(unit_tuple_str)
            val_strs.append(str(val))
            unit_strs.append(unit_str)
        else:
            val_strs.append('1.0')
            unit_strs.append('NONE')
    
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
        print('({}) {} : ( {} : {} )'.format(i, title, val_str, unit_str))
    
    return


def reset_units(shared, *args):
    """
    Remove all units from the 'units' section
    """
    shared.config.remove_section('units')
    shared.config.add_section('units')
    
    return


