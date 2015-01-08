"""
This submodule implements the main interactive component.
"""

from __future__ import print_function
import argparse
import sys
import os
from collections import OrderedDict

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass


# Constant settings for this module
window_width = 80
option_dict = OrderedDict()


def run(argv):
    """
    Begin the viewer - check command line arguments, do some basic
    checking of outputs, initial data setup, and pass over command
    to the main interactive loop.
    """
    
    from . import data
    from . import wrapper_functions
    
    # Create shared object to store global options
    shared = data.SharedData()
    
    # Check for config, limits files and load
    shared.cwd = os.getcwd()
    shared.load_config()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run SPLOSH viewer for RAMSES')
    parser.add_argument('outputs', action='store', nargs='+',
                         help='Directories to load outputs from',
                         metavar='directory')
    
    args = parser.parse_args(argv[1:])
    
    output_list_preabs = vars(args)['outputs']
    
    output_list = []
    for d in output_list_preabs:
        output_list.append(os.path.abspath(d))
    
    # Check output directories exist
    for d in output_list:
        if not os.path.isdir(d):
            print(' >> Directory {} does not exist!'.format(d))
            exit_program(1)
    
    # Perform initial data setup from first output
    # Need to identify quantities available, time of snapshot, etc.
    shared.init_data_store(output_list)
    
    # Pass command to main interactive loop
    main_menu(shared)
    
    # Should never leave the program this way
    raise AssertionError('Left run unexpectedly!')


def exit_program(exit_code=0):
    """
    Leave the program
    """
    from . import __code_name
    from . import backend_list
    print('Leaving '+__code_name+'...')
    for backend in backend_list:
        backend.on_exit()
    sys.exit(exit_code)


def main_menu(shared):
    """
    Main menu - list available variables, list options
    and accept input
    """
    from . import __code_name
    from . import option_menus as om
    
    # Initialize options
    om.init_options(option_dict, shared)
    
    # Format fields
    create_field_mappings(shared)
    
    # Format options
    option_lines = format_options(option_dict)
    
    # Main loop
    while True:
        field_lines = format_fields(shared)
        # Plot the main window header and border
        #print('\n\n')
        print('='*window_width)
        header_string = __code_name + ' - a cheap knockoff of SPLASH for RAMSES'
        print(header_string.center(window_width))
        print('='*window_width)
        
        # Draw the fields
        for line in field_lines:
            print(line)
        print('='*window_width)
        
        # Draw the options
        for line in option_lines:
            print(line)
        print('='*window_width)
    
        in_string = input('Enter y axis or option: ').strip()
        process_input(in_string, option_dict, shared)
    
    # Should never leave the program this way
    raise AssertionError('Left main_menu unexpectedly!')


def create_field_mappings(shared):
    """
    Create field mappings which map individual scalar fields to data types
    Can also contain 'extra' quantities which map in a more complicated way
    """
    
    from . import data
    from . import extra_quantities
    fields_list = shared.fields_list
    field_mappings = shared.field_mappings
    ndim = shared.ndim
    
    for field in fields_list:
        if field.name == 'position':
            # Special case position vector
            position_names = ('x', 'y', 'z')[0:ndim]
            for i in range(field.width):
                fm = data.FieldMapping(position_names[i])
                fm.field = field
                fm.index = i
                field_mappings.append(fm)
        elif (field.width == 1):
            # If a scalar field
            fm = data.FieldMapping(field.name)
            fm.field = field
            fm.index = 1
            field_mappings.append(fm)
        else:
            # If a vector field
            if field.width == ndim:
                suffixes = ('x', 'y', 'z')[0:ndim]
            else:
                suffixes = [str(x) for x in range(field.width)]
            for i in range(field.width):
                fm = data.FieldMapping(field.name + '_' + suffixes[i])
                fm.field = field
                fm.index = i
                field_mappings.append(fm)
    
    for name, expression in shared.config.items('extra'):
        extra_quantities.add_quantity(shared, name, expression, no_save=True)
    
    return


def format_fields(shared, len_line=window_width):
    """
    Create list of strings laying fields onto the screen in a two column format
    """
    from . import text_helpers
    from text_helpers import two_columns_text
    
    field_mappings = shared.field_mappings
    fm_titles = []
    for fm in field_mappings:
        title = fm.title
        if shared.config.has_option('transforms', fm.title):
            transform_string = shared.config.get('transforms', fm.title)
            title = transform_string.replace('x', title)
        fm_titles.append(title)
    
    num_mappings = len(field_mappings) + 1
    right_col = num_mappings // 2
    left_col = num_mappings - right_col
    len_numbers = len(str(left_col))
    len_last_left_col = len(str(left_col))
    time_plot_indent = ' ' * (len_last_left_col - 1)
    
    field_lines = []
    for i in range(left_col):
        ii = i + left_col
        left_no = str(i).rjust(len_numbers)
        if i==0:
            left_string = '{}0) Time plots'.format(time_plot_indent)
        else:
            left_string = '{}) {}'.format(left_no, fm_titles[i-1])
        right_no = str(ii).rjust(len_numbers)
        if (ii < num_mappings):
            right_string = '{}) {}'.format(right_no, fm_titles[ii-1])
        else:
            right_string = ''
        field_lines.append(two_columns_text(left_string, right_string,
                                            len_line))

    return field_lines


def format_options(options, len_line=window_width, spacers=1):
    """
    Create list of strings laying out options evenly
    """
    from .text_helpers import find_best_spacing
    # Determine the length of each option, including spacers
    if not options:
        raise ValueError('No options!')
    sp = ' '*spacers
    option_strings = []
    for key, opt in options.items():
        opt_str = sp + opt.title
        option_strings.append(opt_str)
        if (len(opt_str) > len_line):
            raise ValueError('An option is too long!')
    
    # Identify the number of needed lines by constructing lines
    lines = []
    line = []
    line_len = 0
    i = 0
    for i, opt_str in enumerate(option_strings):
        # Loop over option strings
        if line_len + len(opt_str) > len_line:
            lines.append(line)
            line = [(i, len(opt_str))]
            line_len = len(opt_str)
        else:
            line.append((i, len(opt_str)))
            line_len += len(opt_str)
    if line:
        last_index = len(option_strings) - 1
        lines.append(line)
    
    # Space out options evenly
    lines = find_best_spacing(lines, len_line)
    
    option_lines = []
    # Print lines to screen
    for line in lines:
        line_str = ''
        for opt_item in line:
            opt_str = option_strings[opt_item[0]]
            line_str += opt_str
        option_lines.append((line_str))
        
    return option_lines


def process_input(string_input, options, shared):
    """
    Process an input string - either move to plotting,
    or move to an option menu
    """
    
    # Test for empty string:
    if not string_input:
        return
    
    # Test for invalid characters:
    if not string_input.isalnum():
        print(' >> Invalid input!')
        return
    
    if string_input[0].isdigit():
        # Test for a numerical option (plot choice):
        if not string_input.isdigit():
            print(' >> Invalid input!')
            return
        if not(0 <= int(string_input) <= len(shared.field_mappings)):
            print(' >> Data column does not exist!')
            return
        
        # find relevant mapping
        field_id = int(string_input) - 1
        plotting_options(field_id, shared)
    else:
        # Test for an option:
        if len(string_input) > 2:
            print(' >> Invalid input!')
            return
        if len(string_input) == 2:
            # Test for secondary choice:
            if not string_input[1].isdigit():
                print(' >> Invalid input!')
                return
            second_option = int(string_input[1])
        else:
            second_option = None
        option_key = string_input[0]
        
        if not option_key in options:
            print(' >> Unknown option!')
            return
        
        option = options[option_key]
        if option.method is not None:
            call = getattr(shared, option.method)
            call(option, second_option)
        elif option.call is not None:
            option.call(shared, option, second_option)
        else:
            raise NotImplementedError('This option not yet implemented!')


def plotting_options(y_axis, shared):
    """
    Prompt for remaining user options to select a plot type
    """
    from . import plots
    from numpy import isfinite
    
    # Find x axis
    if y_axis == -1:
        # time plots
        if len(shared.sim_step_list) == 1:
            print(' >> Need more than one timestep!')
            return
        elif shared.temp_config['last_time_axis'] == -5:
            prompt = 'Enter axis for time plots: '
        else:
            prompt = 'Enter axis for time plots [default={}]: '
            prompt = prompt.format(shared.temp_config['last_time_axis']+1)
    else:
        if shared.temp_config['last_x_axis'] == -5:
            prompt = 'Enter x axis (or 0 for 1D plots): '
        else:
            prompt = 'Enter x axis (or 0 for 1D plots) [default={}]: '.format(
                shared.temp_config['last_x_axis']+1)
    input_string = input(prompt).strip()
    if input_string:
        if not input_string.isdigit():
            print(' >> Invalid choice!')
            return
        x_axis = int(input_string) - 1
    else:
        if y_axis == -1:
            x_axis = shared.temp_config['last_time_axis']
        else:
            x_axis = shared.temp_config['last_x_axis']
    if not (-1 <= x_axis < len(shared.field_mappings)):
        print(' >> Invalid choice!')
        return
    if x_axis == y_axis:
        print (' >> x-axis and y-axis must be different!')
        return
    
    if y_axis == -1:
        # If doing time plots, leave here
        time_plotting(shared, x_axis)
        return 
    
    if x_axis == -1:
        # If doing single axis plots, leave here
        single_axis_plotting(shared, y_axis)
        return
    
    # Field properties
    field_x = shared.field_mappings[x_axis].field
    field_y = shared.field_mappings[y_axis].field
    x_index = shared.field_mappings[x_axis].index
    x_pos = 'position' in field_x.flags
    y_index = shared.field_mappings[y_axis].index
    y_pos = 'position' in field_y.flags
    
    # Check if we have two position coordinates, otherwise plot scatterplot
    if not (x_pos and y_pos):
        backend = prompt_for_backend(shared)
        if backend is None:
            return
        plots.plot_fields(x_axis, x_index, y_axis, y_index, None, None, None,
                          'hist2d', None, backend, shared)
        shared.temp_config['last_x_axis'] = x_axis
        return
    
    # Ask to render
    prompt = ('Enter quantity to render (0 for none) '+
              '[default={}]: ').format(shared.temp_config['last_render']+1)
    input_string = input(prompt).strip()
    if not input_string:
        render = shared.temp_config['last_render']
    else:
        if not input_string.isdigit():
            print(' >> Invalid choice!')
            return
        render = int(input_string) - 1
        if not (-1 <= render < len(shared.field_mappings)):
            print(' >> Invalid choice!')
            return
    
    # We have chosen not to render, plot scatterplot
    if render == -1:
        backend = prompt_for_backend(shared)
        if backend is None:
            return
        plots.plot_fields(x_axis, x_index, y_axis, y_index, None, None, None,
                          'hist2d', None, backend, shared)
        shared.temp_config['last_x_axis'] = x_axis
        shared.temp_config['last_render'] = -1
        return
    
    if 'position' in shared.field_mappings[render].field.flags:
        print(' >> Rendered quantity must not be a position!')
        return
    
    render_index = shared.field_mappings[render].index
    
    # Ask for vectors (on rendered plot)
    vector_fields = []
    for i, fm in enumerate(shared.field_mappings):
        if 'vector' in fm.field.flags and fm.index==0:
            vector_fields.append(str(i+1))
    
    if len(vector_fields) > 0:
        vector_fields_string = ', '.join(vector_fields)
        prompt = ('Enter vector plot quantity ({}; 0 for none)'+
                  '[default={}]: ').format(vector_fields_string,
                                         shared.temp_config['last_vector']+1)
        input_string = input(prompt).strip()
        if (not input_string) or (input_string == '0'):
            vector = None
        elif not input_string in vector_fields:
            print(' >> Invalid choice!')
            return
        else:
            vector = int(input_string) - 1
    else:
        vector = None
    
    # otherwise plot rendered plot, possibly with vector plot
    if shared.config.get('xsec', 'plot_type') == 'cross' and shared.ndim>2:
        # slice location
        z_index = (set((0, 1, 2)) - set((x_index, y_index))).pop()
        
        prompt = ('Enter cross-section position [default={}]: ').format(
            shared.temp_config['last_z_slice'][z_index])
        input_string = input(prompt).strip()
        if not input_string:
            # Use default
            z_slice = shared.temp_config['last_z_slice'][z_index]
        else:
            # Attempt float conversion, check for non-insane number
            try:
                z_slice = float(input_string)
            except ValueError:
                print(' >> Not a valid number!')
                return
            if not isfinite(z_slice):
                print(' >> Not a valid number!')
                return
            shared.temp_config['last_z_slice'][z_index] = z_slice
    else:
        z_slice = None
    
    # prompt for backend
    backend = prompt_for_backend(shared)
    if backend is None:
        return
    plots.plot_fields(x_axis, x_index, y_axis, y_index, render, render_index,
                      vector, 'render', z_slice, backend, shared)
    shared.temp_config['last_x_axis'] = x_axis
    if vector:
        shared.temp_config['last_vector'] = vector
    shared.temp_config['last_render'] = render
    return


def time_plotting(shared, axis):
    """
    Show menu for time-based plots (sum, mean, rms, max/min etc)
    """
    import numpy as np
    from . import plots
    
    operation_list = [('mean', 'mean', lambda x, w: np.sum(x*w)/np.sum(w)),
                      #('mean (* weights)', 'mean_times_weights',
                       #lambda x, w: np.mean(x)),
                      ('rms', 'rms',
                       lambda x, w: np.sqrt(np.sum(w*(x**2))/np.sum(w))),
                      #('rms (* weights)', 'rms_times_weights',
                       #lambda x, w: np.sqrt(np.sum(x**2))),
                      ('min', 'min', lambda x, w: np.min(x)),
                      ('max', 'max', lambda x, w: np.max(x)),
                      ('sum(value * weight)', 'sum', lambda x, w: np.sum(x*w))]
    
    # Field properties
    field = shared.field_mappings[axis].field
    index = shared.field_mappings[axis].index
    
    # Check if we do not have position coordinates
    if 'position' in field.flags:
        print('  >> Cannot do time plots for position axes!')
        return
    
    option_list = []
    for i in range(len(operation_list)):
        option_list.append('{}) {}'.format(i+1, operation_list[i][0]))
    print('  '.join(option_list))
    while True:
        input_string = input('Enter type of time-based plot: ').strip()
        if not input_string:
            return
        elif not input_string.isdigit():
            print('  >> Invalid entry!')
            continue
        time_type = int(input_string)
        if not (1 <= time_type <= len(operation_list)):
            print('  >> Invalid entry!')
            continue
        break
    
    # prompt for backend
    backend = prompt_for_backend(shared)
    if backend is None:
        return
    
    # move to plotting
    plots.plot_time(axis, index, operation_list[time_type-1],
                    backend, shared)
    return


def single_axis_plotting(shared, axis):
    """
    Show menu for single axis plotting
    """
    import numpy as np
    from . import plots
    from . import analysis
    
    operation_list = analysis.get_analysis_list()
    
    # Field properties
    field = shared.field_mappings[axis].field
    index = shared.field_mappings[axis].index
    
    # Check if we do not have position coordinates
    if 'position' in field.flags:
        print('  >> Cannot do single axis plots for position axes!')
        return
    
    option_list = []
    for i in range(len(operation_list)):
        operation_name = operation_list[i].properties['name']
        option_list.append('{}) {}'.format(i+1, operation_name))
    print('  '.join(option_list))
    while True:
        input_string = input('Enter type of 1D plot: ').strip()
        if not input_string:
            return
        elif not input_string.isdigit():
            print('  >> Invalid entry!')
            continue
        plot_choice = int(input_string)
        if not (1 <= plot_choice <= len(operation_list)):
            print('  >> Invalid entry!')
            continue
        break
    
    # Check for options
    operation = operation_list[plot_choice-1]
    if 'extra_interactive' in operation.properties:
        operation.properties['extra_interactive'](shared)
    
    # prompt for backend
    backend = prompt_for_backend(shared)
    if backend is None:
        return
    
    # move to plotting
    plots.plot_fields(axis, index, None, None, None, None,
                      None, operation, None,
                      backend, shared)
    return


def prompt_for_backend(shared):
    """
    Prompt the user for a backend
    """
    from . import backend_list
    
    while True:
        prompt = 'Enter backend (? for list) [default={}]: '.format(
            backend_list[shared.temp_config['last_backend_index']].name)
        input_string = input(prompt).strip()
        
        if input_string == '?' or input_string == '/?':
            for backend in backend_list:
                name_str = backend.name.ljust(8)
                print('{} : {}'.format(name_str, backend.long_name))
            continue
        if not input_string:
            return backend_list[shared.temp_config['last_backend_index']]
        for backend in backend_list:
            if (input_string.upper() == backend.name.upper() or
                    input_string.upper() == backend.name.upper().lstrip('\\')):
                return backend
        else:
            print(' >> Invalid backend!')
            return None
    
    return
