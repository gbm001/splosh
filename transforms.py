"""
This submodule implements transforms, including the transforms submenu
"""

from __future__ import print_function
import numpy as np
from collections import OrderedDict

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass


def get_transform_dict():
    ten_to = np.frompyfunc(lambda x: 10.0**x, 1, 1)
    transform_dict = OrderedDict([('none', None),
                                  ('log(x)', (np.log10, ten_to)),
                                  ('ln(x)', (np.log, np.exp)),
                                  ('|x|', (np.fabs, np.array)),
                                  ('1/x', (np.reciprocal, np.reciprocal)),
                                  ('sqrt(x)', (np.sqrt, np.square)),
                                  ('x^2', (np.square, np.sqrt))])
    return transform_dict


def set_transforms(shared, config_section, *args):
    """
    Manually set transforms
    """
    
    while True:
        # Print current transforms
        print_transforms(shared)
        
        # Take an input (select a limit):
        print('x-axis and y-axis are used when the axis is not a data column')
        prompt = 'Select a limit to change (press enter to exit): '
        input_string = input(prompt).strip()
        if not input_string:
            return
        if input_string == 'x':
            field_key = False
            key_id = 'x'
        elif input_string == 'y':
            field_key = False
            key_id = 'y'
        elif not input_string.isdigit():
            print(' >> Invalid input string!')
            continue
        else:
            field_key = True
            key_id = int(input_string)
            if not (0 < key_id <= len(shared.field_mappings)):
                print(' >> Invalid choice!')
                continue
            if 'position' in shared.field_mappings[key_id-1].field.flags:
                print(' >> Transform of coordinate axes not implemented!')
                continue
        
        # Find existing transforms
        if field_key:
            fm = shared.field_mappings[int(input_string) - 1]
            transform_name = fm.title
        else:
            transform_name = 'q' + key_id + '_transform'
        transform_str = shared.config.get_safe('transforms', transform_name,
                                               default='none')
        
        # Offer to change limit
        transform_keys = list(shared.transform_dict.keys())
        cur_key_index = transform_keys.index(transform_str)
        available_transforms = []
        for i, trans in enumerate(transform_keys):
            available_transforms.append('({}) {}'.format(i, trans))
        
        print('Available transforms: {}'.format(
            ', '.join(available_transforms)))
        prompt = ("Enter transform [default={}]: ".format(cur_key_index))
        while True:
            input_string = input(prompt).strip()
            if not input_string:
                new_transform = transform_str
                break
            if not input_string.isdigit():
                print(' >> Not a valid selection!')
                continue
            key_id = int(input_string)
            if not (0 <= key_id < len(available_transforms)):
                print(' >> Invalid selection!')
                continue
            new_transform = transform_keys[key_id]
            break
        
        # Save new transform to configparser
        if new_transform == 'none':
            shared.config.remove_option('transforms', transform_name)
        else:
            shared.config.set('transforms', transform_name, new_transform)
    
    return


def print_transforms(shared):
    """
    Print the current list of plot or data transforms to the screen
    """
    from .interactive import window_width
    field_width = (window_width / 2)
    titles = []
    transform_titles = []
    
    for field_mapping in shared.field_mappings:
        titles.append(field_mapping.title)
        if 'position' in field_mapping.field.flags:
            transform_titles.append('(coordinate axis)')
            continue
        transform_titles.append(shared.config.get_safe(
            'transforms', field_mapping.title, default='none'))
    
    titles.append('x-axis')
    transform_titles.append(shared.config.get_safe(
        'transforms', 'qx_transform', default='none'))
    titles.append('y-axis')
    transform_titles.append(shared.config.get_safe(
        'transforms', 'qy_transform', default='none'))
    
    # Find the maximum length (limits to field_width) of titles,
    # and then transform title length, limited to
    # (window_width - field_width - punctuation length)
    num_len = len(str(len(titles))) + 2
    max_length_titles = max(len(x) for x in titles)
    title_len = min(field_width, max_length_titles)
    width = (window_width - title_len - 6)
    max_length_transform = max(len(x) for x in transform_titles)
    transform_len = min(max_length_transform, width)
    
    for i in range(len(titles)-2):
        num = ('(' + str(i+1) + ')').ljust(num_len)
        title = titles[i].ljust(title_len)
        transform_str = transform_titles[i].ljust(transform_len)
        print('{} {} : {}'.format(num, title, transform_str))
    
    num = '(x)'.ljust(num_len)
    title = titles[-2].ljust(title_len)
    transform_str = transform_titles[-2].ljust(transform_len)
    print('{} {} : {}'.format(num, title, transform_str))
    
    num = '(y)'.ljust(num_len)
    title = titles[-1].ljust(title_len)
    transform_str = transform_titles[-1].ljust(transform_len)
    print('{} {} : {}'.format(num, title, transform_str))
    
    return


def reset_transforms(shared, *args):
    """
    Remove all transforms from the configparser
    """
    shared.config.remove_section('transforms')
    shared.config.add_section('transforms')
    
    return


def get_plot_transforms(x_axis, y_axis, render, plot_type, shared):
    """
    Return the transform keys and plot_transforms
    """
    # Get any transforms for the render axis
    transform_keys = {'x_transform': None,
                      'y_transform': None,
                      'render_transform': None,
                      'hist_transform': None,
                      'qx_transform': None,
                      'qy_transform': None}
    plot_transforms = {'x_transform': None,
                        'y_transform': None,
                        'render_transform': None,
                        'hist_transform': None,
                        'qx_transform': None,
                        'qy_transform': None}
    
    if plot_type == 'hist2d':
        # x and y axes
        x_fm_title = shared.field_mappings[x_axis].title
        x_transform_key = shared.config.get_safe('transforms', x_fm_title)
        if x_transform_key is not None:
            x_transform = shared.transform_dict[x_transform_key]
            transform_keys['x_transform'] = x_transform_key
            plot_transforms['x_transform'] = x_transform
        y_fm_title = shared.field_mappings[y_axis].title
        y_transform_key = shared.config.get_safe('transforms', y_fm_title)
        if y_transform_key is not None:
            y_transform = shared.transform_dict[y_transform_key]
            transform_keys['y_transform'] = y_transform_key
            plot_transforms['y_transform'] = y_transform
    elif plot_type == 'render':
        # render axis only
        render_fm_title = shared.field_mappings[render].title
        render_transform_key = shared.config.get_safe('transforms',
                                                      render_fm_title)
        if render_transform_key is not None:
            render_transform = shared.transform_dict[render_transform_key]
            transform_keys['render_transform'] = render_transform_key
            plot_transforms['render_transform'] = render_transform
    elif plot_type == 'time':
        # time: y_axis only
        y_fm_title = shared.field_mappings[y_axis].title
        y_transform_key = shared.config.get_safe('transforms', y_fm_title)
        if y_transform_key is not None:
            y_transform = shared.transform_dict[y_transform_key]
            transform_keys['y_transform'] = y_transform_key
            plot_transforms['y_transform'] = y_transform
        qx_transform_key = shared.config.get_safe('transforms', 'qx_transform')
        if qx_transform_key is not None:
            qx_transform_key = shared.config.get('transforms', 'qx_transform')
            qx_transform = shared.transform_dict[qx_transform_key]
            transform_keys['qx_transform'] = qx_transform_key
            plot_transforms['qx_transform'] = qx_transform
    else:
        # single axis plot: x_axis only
        x_fm_title = shared.field_mappings[x_axis].title
        x_transform_key = shared.config.get_safe('transforms', x_fm_title)
        if x_transform_key is not None:
            x_transform = shared.transform_dict[x_transform_key]
            transform_keys['x_transform'] = x_transform_key
            plot_transforms['x_transform'] = x_transform
        qx_transform_key = shared.config.get_safe('transforms', 'qx_transform')
        if qx_transform_key is not None:
            qx_transform = shared.transform_dict[qx_transform_key]
            transform_keys['qx_transform'] = qx_transform_key
            plot_transforms['qx_transform'] = qx_transform
        qy_transform_key = shared.config.get_safe('transforms', 'qy_transform')
        if qy_transform_key is not None:
            qy_transform = shared.transform_dict[qy_transform_key]
            transform_keys['qy_transform'] = qy_transform_key
            plot_transforms['qy_transform'] = qy_transform
    
        
    return transform_keys, plot_transforms