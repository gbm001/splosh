"""
This submodule implements the calculation of extra quantities
"""

from __future__ import print_function
from . import python_math_parser

# input and xrange, Python 3 style
try:
    range = xrange
    input = raw_input
except NameError:
    pass

def set_quantities(shared, config_section, *args):
    """
    Set extra quantities to view
    """
    
    while True:
        print_quantities(shared)
        print('(a) Add/edit quantity; (r) Remove quantity; (c) Clear all')
        input_string = input('Select an action (press enter to exit): ').strip()
        if not input_string:
            return
        elif input_string == 'a':
            add_quantity(shared)
        elif input_string == 'r':
            remove_quantity(shared)
        elif input_string == 'c':
            clear_quantities(shared)
        else:
            print(' >> Invalid input string!')
            continue
       

def print_quantities(shared):
    """
    Print currently set extra quantities to screen
    """
    from .interactive import window_width
    field_width = (window_width / 2)
    titles = []
    
    print('Extra quantities:')
    
    are_any = False
    for i, field_mapping in enumerate(shared.field_mappings):
        if field_mapping.extra is not None:
            are_any = True
            title = field_mapping.title
            expression = field_mapping.extra
            print(' {}) {} = {}'.format(i+1, title, expression))
    if not are_any:
        print('  None')
    print()


def add_quantity(shared, name=None, expression=None, no_save=False):
    """
    Add a quantity to the extra quantity list
    """
    from . import data
    from . import wrapper_functions as wf
    if name is None and expression is None:
        print('Enter form of quantity '
              '(e.g. |r| = (x^2 + y^2 + z^2)^0.5)')
        input_string = input('[leave blank to cancel]: ').strip()
        if not input_string:
            return
        
        if not input_string.count('=') == 1:
            print(' >> Use one equals sign!')
            return
        
        name, sign, expression = input_string.partition('=')
        name = name.strip()
        expression = expression.strip()
    elif name is None or expression is None:
        raise ValueError('Set both name and expression, or neither!')
    
    extras_list = []
    locals_list = []
    for field_mapping in shared.field_mappings:
        if field_mapping.extra is None:
            extras_list.append('')
            locals_list.append(field_mapping.title)
        else:
            extras_list.append(field_mapping.title)
            locals_list.append('')
    
    if name in locals_list:
        print(' >> Cannot edit datafile quantity!')
        return
    
    if name in extras_list:
        exists = True
        slot = extras_list.index(name)
    else:
        exists = False
    
    parser = python_math_parser.PythonMathParser()
    parser.set_locals(locals_list)
    try:
        parsed = parser.parse(expression)
    except ValueError:
        print('Invalid expression!')
        return
    
    for item in python_math_parser.walk(parsed):
        if isinstance(item[0], str):
            fm_slot = locals_list.index(item[0])
            fm = shared.field_mappings[fm_slot]
            field_tuple_str = str((fm.field.name, fm.index, fm.field.width))
            item[0] = field_tuple_str
    
    fm = data.FieldMapping(name)
    fm.field = data.DataField(name, width=1, flags=['extra'])
    fm.field.extra = parsed
    fm.index = 1
    fm.extra = expression
    fm.code_mks = wf.calc_units_mks(shared, fm.field)
    if exists:
        shared.field_mappings[slot] = fm
    else:
        shared.field_mappings.append(fm)
    
    if not no_save:
        shared.config.set('extra', name, expression)

    
def remove_quantity(shared):
    """
    Remove an extra quantity for field_mappings and config
    """
    
    not_done = True
    while not_done:
        input_string = input('Enter name of quantity to remove '
                             '[leave blank to cancel]: ').strip()
        if not input_string:
            return
        
        for i, fm in enumerate(shared.field_mappings):
            if fm.title == input_string:
                if fm.extra is not None:
                    not_done = False
                    slot = i
                    break
                else:
                    print ('  >> Cannot remove datafile quantity!')
                    return
        else:
            print('  >> Unknown quantity!')
            return

    shared.config.remove_option('extra', input_string)
    del shared.field_mappings[slot]


def clear_quantities(shared):
    """
    Clear all extra quantities from field_mappings and config
    """
    
    del_list = [i for i, fm in enumerate(shared.field_mappings)
                if fm.extra is not None]
    for index in reversed(del_list):
        del shared.field_mappings[index]
    
    shared.config.remove_section('extra')
    shared.config.add_section('extra')
    

def get_field_names(parsed):
    """
    Run over parsed, extracting all field names and return
    """
    from ast import literal_eval
    field_names = set()
    for item in python_math_parser.walk(parsed):
        if isinstance(item[0], str):
            name, index, width = literal_eval(item[0])
            field_names.add(name)

    return list(field_names)
    

def get_field_tuples(parsed):
    """
    Run over parsed, extracting all field names, indexes and widths and return
    """
    from ast import literal_eval
    field_tuples = set()
    for item in python_math_parser.walk(parsed):
        if isinstance(item[0], str):
            name, index, width = literal_eval(item[0])
            field_tuples.add((name, index, width))

    return list(field_tuples)




