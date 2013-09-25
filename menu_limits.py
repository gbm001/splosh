"""
This submodule implements the limits submenu.
"""

from __future__ import print_function
import ast

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass

def set_limits(shared, config_section, limit_type):
    """
    Manually set limits
    """
    from numpy import isfinite
    
    if limit_type=='plot':
        limits_section = 'limits'
        default_string = 'auto'
    elif limit_type=='data':
        limits_section = 'restrict'
        default_string = 'none'
    else:
        raise ValueError('Unknown limit type!')
    
    while True:
        # Print current limits
        print_limits(shared, limit_type)
        
        # Take an input (select a limit):
        prompt = 'Select a limit to change (press enter to exit): '
        input_string = input(prompt).strip()
        if not input_string:
            return
        if not input_string.isdigit():
            print(' >> Invalid input string!')
            continue
        if not (0 < int(input_string) <= len(shared.field_mappings)):
            print(' >> Invalid choice!')
            continue
        
        # Find existing limits
        fm = shared.field_mappings[int(input_string) - 1]
        if shared.limits.has_option(limits_section, fm.title):
            limits_str = shared.limits.get(limits_section, fm.title)
            limits = ast.literal_eval(limits_str)
        else:
            limits = (default_string, default_string)
        
        # Offer to change limit
        prompt = ("Enter minimum value or "
                  "'{}' [default={}]: ".format(default_string, limits[0]))
        while True:
            input_string = input(prompt).strip()
            if not input_string:
                new_limit_left = limits[0]
                break
            if input_string == default_string:
                new_limit_left = default_string
                break
            try:
                new_limit_left = float(input_string)
            except ValueError:
                print(' >> Not a valid number!')
                continue
            if not isfinite(new_limit_left):
                print(' >> Not a valid number!')
                continue
            break
        
        if new_limit_left == default_string:
            new_limits = (default_string, default_string)
        else:
            prompt = "Enter maximum value [default={}]: ".format(limits[1])
            while True:
                input_string = input(prompt).strip()
                if not input_string:
                    new_limits_right = limits[1]
                    break
                try:
                    new_limit_right = float(input_string)
                except ValueError:
                    print(' >> Not a valid number!')
                    continue
                if not isfinite(new_limit_right):
                    print(' >> Not a valid number!')
                    continue
                break
            if new_limit_right <= new_limit_left:
                print(' >> Limits are not valid! (min >= max)')
                continue
            new_limits = (new_limit_left, new_limit_right)
        
        # Save new limits to limits configparser
        limits_str = repr(new_limits)
        shared.limits.set(limits_section, fm.title, limits_str)
    
    return


def print_limits(shared, limit_type):
    """
    Print the current list of plot or data limits to the screen
    """
    from .interactive import window_width
    field_width = (window_width / 2)
    titles = []
    min_strs = []
    max_strs = []
    
    if limit_type=='plot':
        limits_section = 'limits'
        default_string = 'auto'
        print('Plot limits (min : max)')
    elif limit_type=='data':
        limits_section = 'restrict'
        default_string = 'none'
        print('Data limits (min : max)')
    else:
        raise ValueError('Unknown limit type!')
    
    for field_mapping in shared.field_mappings:
        titles.append(field_mapping.title)
        if shared.limits.has_option(limits_section, field_mapping.title):
            limits_str = shared.limits.get(limits_section, field_mapping.title)
            limits = ast.literal_eval(limits_str)
            min_strs.append(str(limits[0]))
            max_strs.append(str(limits[1]))
        else:
            min_strs.append(default_string)
            max_strs.append(default_string)
    
    # Find the maximum length (limits to field_width) of titles,
    # and then maximum min/max length, limited to
    # (window_width - field_width - punctuation length) /2
    max_length_titles = max(len(x) for x in titles)
    title_len = min(field_width, max_length_titles)
    min_max_width = (window_width - title_len - 13) / 2
    max_length_min_strs = max(len(x) for x in min_strs)
    max_length_max_strs = max(len(x) for x in max_strs)
    min_max_len = max(max_length_min_strs, max_length_max_strs)
    min_max_len = min(min_max_len, min_max_width)
    
    for i in range(len(titles)):
        title = titles[i].ljust(title_len)
        min_str = min_strs[i].ljust(min_max_len)
        max_str = max_strs[i].ljust(min_max_len)
        print('({}) {} : ( {} : {} )'.format(i+1, title, min_str, max_str))
    
    return


def reset_limits(shared, *args):
    """
    Remove all limits from the 'limits' configparser
    """
    shared.limits.remove_section('limits')
    shared.limits.add_section('limits')
    
    return


def reset_restriction_limits(shared, *args):
    """
    Remove all limits from the 'restrict' configparser
    """
    shared.limits.remove_section('restrict')
    shared.limits.add_section('restrict')
    
    return


