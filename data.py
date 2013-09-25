"""
This submodule implements the main data store.
"""

import os
import ast

# configparser, Python 3 style
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class SharedData():
    """
    Main shared object for storing runtime information
    """
    def __init__(self):
        self.cwd = ''
        self.fields_list = []
        self.sim_step_list = []
        self.ndim = 0
        self.last_x_axis = -5
        self.last_time_axis = -5
        self.last_render = -1
        self.last_vector = -1
        self.last_backend_index = 0
        self.config = ConfigOptions()
        self.limits = configparser.SafeConfigParser()
        self.limits.add_section('limits')
        self.limits.add_section('restrict')
        self.field_mappings = []
        self.extra_field_mappings = []

    def init_data_store(self, output_list):
        """
        Set up the initial data store, having been given a list of outputs
        Examine only the first for speed
        """
        from . import wrapper_functions as wf
        from . import plots
        from . import transforms
        
        # Create the sim_list by loading the output_list directory
        for d in output_list:
            sim_step = SimStep()
            sim_step.output_dir = d
            self.sim_step_list.append(sim_step)
        
        # Load the first data set
        first_step = self.sim_step_list[0]
        first_step.load_dataset()
        
        # Determine the available variables
        self.fields_list = wf.get_fields(first_step.data_set)
        
        for field in self.fields_list:
            field.code_mks = wf.get_code_mks(first_step.units, field.name)
        
        # Set some basics
        self.ndim = wf.get_ndim(first_step.data_set)
        if not 1 <= self.ndim <= 3:
            raise ValueError('Invalid number of dimensions!')
        
        self.transform_dict = transforms.get_transform_dict()
        
        #self.box_limits = wf.get_box_limits(self.sim_step_list[0].data_set)
        #box_min, box_max = self.box_limits
        #self.last_z_slice = (box_max + box_min) / 2.0
        box_max = wf.get_box_limits(first_step.data_set)
        if self.config.has_option('units', '_position'):
            unit_tuple_str = self.config.get('units', '_position')
            x_unit, x_unit_str = ast.literal_eval(unit_tuple_str)
        else:
            x_unit = 1.0
        self.last_z_slice = box_max * first_step.length_mks / (2.0 * x_unit)
        
        self.cmaps = plots.get_cmaps()
        
        return None
        
    def load_config(self):
        """
        Check for config and limits files in this directory,
        and load them if they exist
        """
        
        self.config = ConfigOptions() # Reset to defaults
        
        home_conf_dir = os.path.expanduser('~' + os.path.sep + '.splosh')
        global_defaults = os.path.join(home_conf_dir, 'splosh.defaults')
        global_limits = os.path.join(home_conf_dir, 'splosh.limits')
        
        defaults_file = os.path.join(self.cwd, 'splosh.defaults')
        # load defaults (no change if none found)
        self.config.read([ global_defaults, defaults_file])
        
        limits_file = os.path.join(self.cwd, 'splosh.limits')
        # load limits (no change if none found)
        self.limits.read([global_limits, limits_file])


    def save_config(self, *args):
        """
        Save the config file splosh.defaults in the current directory
        """
        defaults_file = os.path.join(self.cwd, 'splosh.defaults')
        with open(defaults_file, 'w') as f:
            self.config.write(f)
        print ('Config saved to {}'.format(defaults_file))


    def save_config_and_limits(self, *args):
        """
        Save the config file splosh.defaults, then save the
        limits file splosh.limits in the current directory
        """
        self.save_config()
        limits_file = os.path.join(self.cwd, 'splosh.limits')
        with open(limits_file, 'w') as f:
            self.limits.write(f)
        print ('Limits saved to {}'.format(limits_file))


class SimStep():
    """
    Data for one snapshot
    """
    def __init__(self, time=0.0, output_dir=None, data_set=None, time_mks=1.0):
        self.time = time
        self.time_mks = time_mks
        self.output_dir = output_dir
        self.data_set = data_set
        self.data_constants = {}
    
    def __repr__(self):
        return 'SimStep({}, {}, {}, {})'.format(self.time, self.output_dir,
                                            self.data_set, self.time_mks)

    def get_output_id(self):
        """
        If we have an output_dir set yet, get an output id
        """
        from . import wrapper_functions
        if self.output_dir is None:
            output_id = None
        else:
            output_id = wrapper_functions.get_output_id(self.output_dir)
        
        return output_id
            

    def load_dataset(self):
        """
        Modify a sim_step in the sim_step_list, loading the output
        and updating quantities
        """
        from . import wrapper_functions
        # Load the output
        output_dir = self.output_dir
        snapshot = wrapper_functions.load_output(output_dir)
        
        # Update quantities
        self.units = wrapper_functions.get_units(snapshot)
        self.time = wrapper_functions.get_time(snapshot)
        self.data_constants = wrapper_functions.get_data_constants(snapshot)
        self.time_mks = wrapper_functions.get_code_mks(self.units, 'time')
        self.box_length = wrapper_functions.get_box_limits(snapshot)
        self.length_mks = wrapper_functions.get_code_mks(self.units, 'position')
        self.ndim = wrapper_functions.get_ndim(snapshot)
        self.minmax_res = wrapper_functions.get_minmax_res(snapshot)
        self.data_set = snapshot
        
        return


class DataField():
    """
    Information for one data field type
    """
    def __init__(self, name=None, width=1, flags=None):
        self.name = name
        self.width = width
        self.extra = None # Parsed expression for extra quantities
        if flags is None:
            self.flags = []
        else:
            self.flags = flags  # special flags for the wrapper to set
                                # 'position' indicates position-type field,
                                # 'vector' can be vector plotted
    
    def __repr__(self):
        return 'DataField({}, {}, {})'.format(self.name, self.width,
                                              self.flags)


class FieldMapping():
    """
    Information for one mapping of command line option to field type
    """
    def __init__(self, title, index=0, field=None, code_mks=1.0,
                 unit_name='', unit_value=1.0, extra=None):
        self.title = title
        self.index = index
        self.field = field
        self.code_mks = code_mks
        self.unit_name = unit_name
        self.unit_value = unit_value
        self.extra = extra
    
    def __repr__(self):
        return 'FieldMapping({}, {}, {}, {}, {}, }{)'.format(
            self.title, self.index, self.field, self.code_mks, self.unit_name,
            self.unit_value, self.extra)


class ConfigOptions(configparser.SafeConfigParser):
    """
    Class that extends the SafeConfigParser; adds default options
    """
    def __init__(self):
        """
        Set up default options
        """
        configparser.SafeConfigParser.__init__(self)
        self.add_section('data')
        self.set('data', 'use_units', 'off')
        
        self.add_section('page')
        self.set('page', 'equal_scales', 'on')
        
        self.add_section('opts')
        self.set('opts', 'weighting', 'volume')
        self.set('opts', 'multiprocessing', 'off')
        
        self.add_section('limits')
        self.set('limits', 'adaptive', 'adapt')
        self.set('limits', 'adaptive_coords', 'adapt')
        self.set('limits', 'filter_all', 'off')
        self.set('limits', 'aspect_ratio', 'on')
        
        self.add_section('legend')
        
        self.add_section('render')
        self.set('render', 'resolution', 'auto')
        self.set('render', 'cmap', 'OrRd')
        self.set('render', 'invert', 'no')
        
        self.add_section('vector')
        
        self.add_section('xsec')
        self.set('xsec', 'plot_type', 'proj')
        
        self.add_section('units')
        
        self.add_section('extra')
        
        self.add_section('transforms')
        

def test_field_name(field_name):
    """
    Field names are stored using suffixes of an underscore followed by x, y, z
    or numbers. If the field name will interfere with this, return False. Also
    x, y, z and 'position' are special 'position' fields and are not permitted.
    """
    forbidden_field_names=['x', 'y', 'z']
    OK = True
    
    if field_name in forbidden_field_names or field_name=='position':
        OK = False
    
    if '_' in field_name:
        last_sec = field_name.rsplit('_', 1)[-1]
        if last_sec.isdigit() or last_sec in forbidden_field_names:
            OK = False
    
    return OK
