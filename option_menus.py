"""
This submodule implements the option menus.
"""

from __future__ import print_function
import sys
import ast

from . import data
from . import menu_limits
from . import menu_units
from . import transforms
from . import plots
from . import extra_quantities

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass

class Option():
    """
    A single option in an option menu; contains information such as
    the name of the option and the function to call
    """
    def __init__(self, title, long_title=None, call=None,
                 suboptions=None, config_section=None, method=None):
        self.title = title
        self.long_title = long_title
        self.call = call
        self.suboptions = suboptions
        self.config_section = config_section
        self.method = method


class SubOption():
    """
    A menu corresponding to a suboption within menu of a single option
    in the options menu; contains information such as the 
    """
    def __init__(self, title=None, call=None, info=None):
        self.title = title
        self.call = call
        self.info = info


def init_options(options, shared):
    """
    Initialize the complete options menu sets, with options and suboptions
    """
    from . import interactive
    # Data menu
    subopts = []
    #subopts.append(SubOption('read new data /re-read data'))
    #subopts.append(SubOption('change number of timesteps used'))
    #subopts.append(SubOption('plot selected steps only'))
    #subopts.append(SubOption('buffering of data on/off'))
    #subopts.append(SubOption('turn calculate extra quantities on/off'))
    info = {'config_item': 'use_units', 'flip_opts': ['off', 'on'],
            'print_call': lookup_single}
    subopts.append(SubOption('use physical units', single_flip_option, info))
    subopts.append(SubOption('change physical unit settings',
                              menu_units.set_units))
    subopts.append(SubOption('reset units for all columns',
                             menu_units.reset_units))
    subopts.append(SubOption('edit list of calculated quantities',
                   extra_quantities.set_quantities))
    options['d'] = Option('(d)ata', 'Data read options', option_menu,
                          subopts, 'data')
    # Page menu
    subopts = []
    info = {'config_item': 'equal_scales', 'flip_opts': ['off', 'on'],
            'print_call': lookup_single}
    subopts.append(SubOption('equal scales on spatial axes',
                             single_flip_option, info))
    options['p'] = Option('(p)age', 'Page setup options',
                          option_menu, subopts, 'page')
    # Particle plot options
    subopts = []
    info = {'config_item': 'show_sinks', 'flip_opts': ['off', 'on'],
            'print_call': lookup_single}
    subopts.append(SubOption('Show sink particles on rendered plots',
                             single_flip_option, info))
    info = {'config_item': 'sink_marker',
            'string_list': ['point', 'star', 'pixel', 'x', 'plus', 'circle',
                            'square', 'pentagon', 'hexagon1', 'hexagon2',
                            'diamond', 'thin diamond', '<no value>'],
            'prompt': "Select a sink particle symbol (or '<no value>'"
                      " for backend default option): ",
            'print_call': lookup_single}
    subopts.append(SubOption("set sink particle symbol",
                             single_string_option, info))
    info = {'config_item': 'sink_face_colour',
            'prompt': 'Select a sink particle face colour',
            'print_call': lookup_single}
    subopts.append(SubOption('set sink particle face colour',
                             colour_option, info))
    info = {'config_item': 'sink_edge_colour',
            'prompt': 'Select a sink particle edge colour',
            'print_call': lookup_single}
    subopts.append(SubOption('set sink particle edge colour',
                             colour_option, info))
    info = {'config_item': 'sink_marker_size', 'type':'float',
            'non_numeric': ['<no value>'],
            'prompt': "Enter sink particle symbol size (or '<no value>'"
                      " for backend default)\n"
                      "Negative numbers are in terms of the backend default",
                      'print_call': lookup_single}
    subopts.append(SubOption('set sink particle symbol size',
                             single_numeric_option, info))
    info = {'config_item': 'sink_marker_edge_width', 'type':'float',
            'non_numeric': ['<no value>'],
            'prompt': "Enter sink particle symbol edge width (or '<no value>'"
                      " for backend default)\n"
                      "Negative numbers are in terms of the backend default",
                      'print_call': lookup_single}
    subopts.append(SubOption('set sink particle symbol edge width',
                             single_numeric_option, info))
    info = {'config_item': 'weighting', 'flip_opts': ['volume', 'mass'],
            'print_call': lookup_single}
    subopts.append(SubOption('Weighting of histograms (not y-axis density)',
                             single_flip_option, info))
    info = {'config_item': 'multiprocessing', 'flip_opts': ['off', 'on'],
            'print_call': lookup_single}
    subopts.append(SubOption('use multiprocessing',
                             single_flip_option, info))
    options['o'] = Option('(o)pts', 'Plot options',
                          option_menu, subopts, 'opts')
    # Limits menu
    subopts = []
 #1) use adaptive/fixed limits                  ( ADAPT, FIXED )
 #2) set limits manually
 #3) xy limits/radius relative to particle           ( 0 )
 #4) auto-adjust limits to match device aspect ratio ( OFF )
 #5) apply log/other transformations to columns
 #6) reset limits for all columns
 #7) use subset of data restricted by parameter range     ( OFF )
    info = {'config_item': 'adaptive', 'flip_opts': ['adapt', 'fixed'],
            'print_call': lookup_single}
    subopts.append(SubOption('use adaptive/fixed limits on quantities',
                             single_flip_option, info))
    info = {'config_item': 'adaptive_coords', 'flip_opts': ['adapt', 'fixed'],
            'print_call': lookup_single}
    subopts.append(SubOption('use adaptive/fixed limits on plot axes',
                             single_flip_option, info))
    subopts.append(SubOption('set plot limits manually',
                              menu_limits.set_limits, 'plot'))
    subopts.append(SubOption('set data limits manually',
                              menu_limits.set_limits, 'data'))
    subopts.append(SubOption('reset plot limits for all columns',
                             menu_limits.reset_limits))
    subopts.append(SubOption('reset data limits for all columns',
                             menu_limits.reset_restriction_limits))
    info = {'config_item': 'aspect_ratio', 'flip_opts': ['off', 'on'],
            'print_call': lookup_single}
    subopts.append(SubOption('auto-adjust limits to match '
                             'device aspect ratio', single_flip_option, info))
    subopts.append(SubOption('apply log/other transformation to columns',
                             transforms.set_transforms))
    subopts.append(SubOption('reset transforms for all columns',
                             transforms.reset_transforms))
    info = {'config_item': 'filter_all', 'flip_opts': ['off', 'on'],
            'print_call': lookup_single}
    subopts.append(SubOption('restrict using data limits',
                             single_flip_option, info))
    options['l'] = Option('(l)imits', 'Limits options', option_menu, subopts,
                          'limits')
    # Legend and titles menu
    options['g'] = Option('le(g)end', 'Legend and title options',
                          option_menu, subopts, 'legend')
    # Help option
    options['h'] = Option('(h)elp', call=instructions)
    # Render plot menu
 #1) set number of pixels               ( AUTO )
 #2) change colour scheme               ( 2 )
 #3) 2nd render/contour prompt          ( OFF )
 #4) change number of contours          ( 30 )
 #5) colour bar options                 (  1 )
 #6) use particle colours not pixels    ( OFF )
 #7) normalise interpolations           ( OFF )
 #8) use accelerated rendering          ( OFF )
 #9) use density weighted interpolation ( OFF )
 #10) customize label on projection plots (  )
 #11) change kernel         ( default [cubic] )
    subopts = []
    info = {'config_item': 'resolution', 'type':'int',
            'numeric_limits': (1,1024), 'non_numeric': ['auto'],
            'prompt': 'Enter number of pixels', 'print_call': lookup_single}
    subopts.append(SubOption('set number of pixels',
                             single_numeric_option, info))
    info = {'config_item': 'cmap', 'string_list': shared.cmaps,
            'prompt': 'Select a colour map', 'print_call': lookup_single}
    subopts.append(SubOption('change colour scheme',
                             single_string_option, info))
    info = {'config_item': 'invert', 'flip_opts': ['yes', 'no'],
            'print_call': lookup_single}
    subopts.append(SubOption('invert colour scheme',
                             single_flip_option, info))
    options['r'] = Option('(r)ender', 'Rendering options',
                          option_menu, subopts, 'render')
    # Vector plot menu
    options['v'] = Option('(v)ector', 'Vector plot options',
                          option_menu, subopts, 'vector')
    # Xsec/rotation menu
    subopts = []
    info = {'config_item': 'plot_type', 'flip_opts': ['proj', 'cross'],
            'print_call': lookup_single}
    subopts.append(SubOption('switch between cross-section and projection',
                             single_flip_option, info))
    options['x'] = Option('(x)sec/rotate',
                          'Cross section / 3D plotting options',
                          option_menu, subopts, 'xsec')
    # Saving and quitting options
    options['s'] = Option('(s)ave', method='save_config')
    options['S'] = Option('(S)ave with limits',
                          method='save_config_and_limits')
    options['q'] = Option('(q)uit', call=exit_option)
    
    return None


def option_menu(shared, option, second_option):
    """
    Load an options menu, print to screen and process input
    """
    from .interactive import window_width
    l_col_width = int(float(window_width) * 2.0 / 3.0)
    
    if not second_option:
        print('='*window_width)
        print(option.long_title.center(window_width))
    suboptions = option.suboptions
    num_options = len(suboptions) + 1
    
    # Print the menu
    if not second_option:
        print('(0) exit submenu')
        for i, subopt in enumerate(suboptions):
            if subopt.info is not None and 'print_call' in subopt.info:
                pc = subopt.info['print_call']
                extra_string = pc(shared, option.config_section, subopt.info)
            else:
                extra_string = ''
            
            l_str = '({}) {}'.format(i+1, subopt.title).ljust(l_col_width)
            print(l_str + extra_string)
    
    # Check second option
    if second_option is not None:
        # check second option is OK
        if not (0 <= second_option < num_options):
            print(' >> Invalid second option!')
            return
    else:
        while True:
            input_string = input('Enter selection: ').strip()
            if not input_string:
                return
            if input_string.isdigit():
                if 0 <= int(input_string) < num_options:
                    break
            print(' >> Invalid option!')
        second_option = int(input_string)
    
    # If 'exit' selected, return
    if second_option == 0:
        return
    
    selected_subopt = suboptions[second_option-1]
    
    call = selected_subopt.call
    if call is None:
        raise NotImplementedError("Haven't implemented this suboption!")
    call(shared, option.config_section, selected_subopt.info)


def lookup_single(shared, config_section, info):
    """
    Lookup a single option from the config, and return it
    formatted as a string
    """
    cur_value = shared.config.get_safe(config_section, info['config_item'])
    if cur_value is None:
        cur_value = '<no value>'
    return '[ {} ]'.format(cur_value)


def single_flip_option(shared, config_section, info):
    """
    Flip a single option in the config file between two allowed values
    """
    config = shared.config
    cur_value = config.get(config_section, info['config_item'])
    values = info['flip_opts']
    if cur_value == info['flip_opts'][0]:
        set_value = info['flip_opts'][1]
    else:
        set_value = info['flip_opts'][0]
    config.set(config_section, info['config_item'], set_value)

    print(' >> Option set to {}'.format(set_value))

    return


def single_numeric_option(shared, config_section, info):
    """
    Set a single numeric option in the config file
    """
    from numpy import isfinite
    config = shared.config
    cur_value = config.get_safe(config_section, info['config_item'])
    if cur_value is None:
        cur_value = '<no value>'
    
    non_numeric = []
    if 'non_numeric' in info:
        for item in info['non_numeric']:
            non_numeric.append(item)
    
    if 'prompt' in info:
        input_string = input(info['prompt']+' [default={}]: '.format(cur_value))
    else:
        input_string = input('Enter value [default={}]: '.format(cur_value))
    input_string = input_string.strip()
    
    if input_string in non_numeric:
        new_value = input_string
    elif info['type'] == 'int':
        try:
            new_value = int(input_string)
        except ValueError:
            print('Invalid number!')
            return
        if 'numeric_limits' in info:
            min_val, max_val = info['numeric_limits']
            if min_val is None:
                if not (new_value <= max_val):
                    print('Out of range!')
                    return
            if max_val is None:
                if not (min_val <= new_value):
                    print('Out of range!')
                    return
            else:
                if not (min_val <= new_value <= max_val):
                    print('Out of range!')
                    return
    elif info['type'] == 'float':
        try:
            new_value = float(input_string)
        except ValueError:
            print('Invalid number!')
            return
        if 'numeric_limits' in info:
            min_val, max_val = info['numeric_limits']
            if min_val is None:
                if not (new_value <= max_val):
                    print('Out of range!')
                    return
            if max_val is None:
                if not (min_val <= new_value):
                    print('Out of range!')
                    return
            else:
                if not (min_val <= new_value <= max_val):
                    print('Out of range!')
                    return
    else:
        raise ValueError('Unknown type to set in single_numeric_option!')
    
    if (input_string == '<no value>'):
        # Can only happen if '<no value>' in non_numeric list
        config.remove_safe(config_section, info['config_item'])
    else:
        config.set(config_section, info['config_item'], str(new_value))
    
    print(' >> Option set to {}'.format(new_value))
    
    return


def single_string_option(shared, config_section, info):
    """
    Set a single string option in the config file
    """
    
    if 'string_list' in info:
        print('Acceptable values:')
        print(', '.join(info['string_list']))
    
    cur_value = shared.config.get_safe(config_section, info['config_item'])
    if cur_value is None:
        cur_value = '<no value>'
    if 'prompt' in info:
        input_string = input(info['prompt']+' [default={}]: '.format(cur_value))
    else:
        input_string = input('Enter value [default={}]: '.format(cur_value))
    input_string = input_string.strip()
    
    if not input_string:
        if cur_value == '<no value>':
            return
        else:
            input_string = cur_value
    
    if 'string_list' in info:
        if not input_string in info['string_list']:
            print('Invalid value!')
            return
    
    if (input_string == '<no value>'):
        # this can only happen if 'no value' is 
        shared.config.remove_safe(config_section, info['config_item'])
    else:
        shared.config.set(config_section, info['config_item'], str(input_string))
    
    print(' >> Option set to {}'.format(input_string))


def colour_option(shared, config_section, info):
    """
    Accept a colour specification in either colour name, hex code or RGB(A)
    tuple form
    """
    import ast
    
    colour_list = ['default', 'none', 'blue', 'green', 'red', 'cyan',
                   'magenta', 'yellow', 'black', 'white']
    
    cur_value = shared.config.get_safe(config_section, info['config_item'],
                                       default='<no value>')
    
    print('Enter a colour using either a colour name, RBG(A) tuple or hex code')
    print('Valid colours: blue, green, red, cyan, magenta, yellow, black, white')
    print('Enter RGB(A) colours as e.g. (0, 127, 255) or (0, 127, 255, 127)')
    print('Enter hex colours as e.g. #00CCFF')
    print("Enter '<no value>' to use backend default")
    
    if 'prompt' in info:
        input_string = input(info['prompt']+' [default={}]: '.format(cur_value))
    else:
        input_string = input('Enter value [default={}]: '.format(cur_value))
    
    input_string = input_string.strip()
    
    if not input_string:
        if cur_value == '<no value>':
            return
        input_string = cur_value
    
    if input_string == '<no value>':
        shared.config.remove_safe(config_section, info['config_item'])
        print(' >> Colour option removed')
        return
    elif input_string in colour_list:
        pass # colour code
    elif input_string[0] == '#':
        # Hex colour code
        if len(input_string) != 7:
            print(' >> Invalid hex code!')
            return
        for char in input_string[1:]:
            if char not in '0123456789ABCDEF':
                print(' >> Invalid hex code!')
                return
    elif input_string[0] == '(' or input_string[0] == '[':
        # RGB(A) tuple
        try:
            colour_tuple = ast.literal_eval(input_string)
        except SyntaxError:
            print(' >> Invalid RGB(A) tuple!')
            return
        if not isinstance(colour_tuple, (list, tuple)):
            print(' >> Invalid RGB(A) tuple!')
            return
        if not (3 <= len(colour_tuple) <= 4):
            print(' >> Invalid RGB(A) tuple!')
            return
        for item in colour_tuple:
            if isinstance(item, (int, long)) and (0 <= item <= 255):
                pass
            else:
                print('RBG(A) colour out of range (0->255)!')
                return
        input_string = str(tuple(colour_tuple))
                
    else:
        print(' >> Invalid colour choice!!')
        return
    
    shared.config.set(config_section, info['config_item'], input_string)
    
    print(' >> Colour set to {}'.format(input_string))


def instructions(*args):
    """
    Helpful instructions go here
    """
    
    help_string="""
    To make a plot, enter a number corresponding to a field. This will
    be selected as the y-axis, and you can then choose the x-axis (and
    if desired, rendered quantities and vector quantities).
    
    To select an option, enter the character indicated in brackets
    in the name of an option menu. The option menu will have a list of
    numeric options; these options can be selected directly from the
    main menu by entering both the option menu character and the number
    of the numeric option.
    
    Press enter to continue...
    """
    print(help_string)
    input()
    
    return False


def exit_option(*args):
    """
    Wrapper for exit_program
    """
    from . import interactive
    interactive.exit_program()