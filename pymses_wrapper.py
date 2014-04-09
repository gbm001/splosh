"""
This submodule implements wrapper functions for dealing with pymses.
"""

from __future__ import print_function
import pymses
import os
import gc
import numpy as np


def convert_dir_to_RAMSES_args(out_dir):
    """
    Takes a directory which should have format 'XXX/YYY/output_ZZZZZ'.
    Return the base path (/XXX/YYY) and output number (ZZZZZ)
    """
    base_path, base_dir = os.path.split(out_dir)
    output_OK = True
    # Check name is valid
    if not base_dir.startswith('output_'):
        output_OK = False
    elif base_dir.count('_') != 1:
        output_OK = False
    else:
        output_number = base_dir.split('_')[1]
        if not output_number.isdigit():
            output_OK = False
    if not output_OK:
        print('Output directory {} not in RAMSES '
                '(output_XXXXX) format!'.format(out_dir))
        raise ValueError()
    output_number = int(output_number)
    
    return base_path, output_number


def get_output_id(output_dir):
    """
    Find the output ID number for an output - for RAMSES this is unique
    """

    base_path, output_number = convert_dir_to_RAMSES_args(output_dir)
    
    return output_number


def load_output(output_dir):
    import ast
    from pymses.sources.ramses.output import Vector, Scalar
    """
    Load a RAMSES output and return the RamsesOutput object
    """
    base_path, output_number = convert_dir_to_RAMSES_args(output_dir)
    
    ro = pymses.RamsesOutput(base_path, output_number)
    
    ndim_str = str(ro.ndim)+'D'
    
    format_file = os.path.join(output_dir, 'data_info.txt')
    if os.path.isfile(format_file):
        with open(format_file) as f:
            field_descrs_str = f.readline()
        
        field_descr_in = ast.literal_eval(field_descrs_str)
        field_descr = {}
        for file_type, info_list in field_descr_in.items():
            new_info_list = []
            for item in info_list:
                if item[0] == 'Scalar':
                    new_item = Scalar(*item[1:])
                elif item[0] == 'Vector':
                    new_item = Vector(*item[1:])
                else:
                    raise ValueError('Unknown entry type '
                                     '(not Scalar or Vector)!')
                new_info_list.append(new_item)
            field_descr[file_type] = new_info_list
        
        ro.amr_field_descrs_by_file = {ndim_str: field_descr}
    
    # Read the info file ourselves because pymses does a crappy job
    # and misses interesting things
    info_file = os.path.join(
        output_dir, 'info_{0:05d}.txt'.format(output_number))
    
    with open(info_file) as f:
        lines = f.readlines()
    
    renamed_by_pymses = ['unit_l', 'unit_d', 'unit_t']
    
    for line in lines:
        if line.count('=') == 1:
            left, right = line.split('=', 1)
            if (' ' not in left.strip()) and (' ' not in right.strip()):
                name = left.strip()
                value = ast.literal_eval(right.strip())
                if (name not in ro.info) and (name not in renamed_by_pymses):
                    ro.info[name] = value
    
    return ro


def get_time(ro):
    """
    Take a RAMSES object and return the time
    """
    return ro.info['time']


def get_ndim(ro):
    """
    Take a RAMSES object and return the number of dimensions
    """
    return ro.info['ndim']


def get_units(ro):
    """
    Take a RAMSES object and return a dictionary of units
    """
    units = {}
    for key, val in ro.info.iteritems():
        if key.startswith('unit_'):
            newkey = key[5:]
            units[newkey] = val
    return units


def get_code_mks(units, field_name):
    """
    Use the dictionary returned by get_units and a field name to make
    an educated guess at the 'physical units' required to get back to mks.
    Calls get_code_units_guess and returns 'mks' magnitude of unit
    """
    guess = get_code_units_guess(units, field_name)
    return guess.val


def get_code_units_guess(units, field_name):
    """
    Use the dictionary returned by get_units and a field name to make
    an educated guess at the 'physical units' required to get back to mks
    """
    from pymses.utils import constants as C
    
    if field_name == 'time':
        code_mks = units['time']
    elif field_name == 'position':
        code_mks = units['length']
    elif field_name == 'rho':
        code_mks = units['density']
    elif field_name == 'vel':
        code_mks = units['velocity']
    elif field_name == 'P':
        code_mks = units['pressure']
    elif field_name == 'g':
        code_mks = (units['length'] / units['time']**2)
    else:
        print('Unknown data type: {}'.format(field_name))
        code_mks = pymses.utils.constants.Unit((0,0,0,0,0,0), 1.0)
    
    return code_mks


def get_data_constants(ro):
    """
    Take a RAMSES object and return a dictionary of data constants
    """
    
    # List of constants, and default values if missing
    constants_list = [('mu_gas', 2.0)]
    
    constants_dict = {}
    for const_name, const_default in constants_list:
        if const_name in ro.info:
            constants_dict[const_name] = ro.info[const_name]
        else:
            constants_dict[const_name] = const_default
    
    return constants_dict


def get_minmax_res(ro):
    """
    Take a RAMSES object and return the min/maximum resolution
    """
    min_level = ro.info['levelmin']
    max_level = ro.info['levelmax']
    return 2**min_level, 2**max_level


def get_box_limits(ro):
    """
    Take a RAMSES object and get the box size
    """
    
    boxlen = ro.info['boxlen']
    #min_vals = np.zeros(ro.ndim)
    max_vals = np.zeros(ro.ndim)
    max_vals[:] = boxlen
    
    #return (min_vals, max_vals)
    return max_vals


def get_fields(ro):
    """
    Take a RAMSES object and return the list of fields
    """
    from .data import DataField
    from .data import test_field_name
    # Find possible field (depends on RAMSES format and NOT the output)
    ndim = ro.ndim
    field_descr = ro.amr_field_descrs_by_file['{}D'.format(ndim)]
    files = ro.output_files
    
    ramses_fields = []
    for file_type in field_descr:
        # Looping over 'hydro', 'grav' files
        if file_type in files:
            for field in field_descr[file_type]:
                # Looping over 'x', 'vel' etc
                new_name = field.name
                if not test_field_name(new_name):
                    new_name = new_name + '__'
                new_field = DataField(new_name)
                new_field.width = len(field.ivars)
                if len(field.ivars) == ndim:
                    new_field.flags = ['vector']
                ramses_fields.append(new_field)
    
    # Add x(,y,z) virtual fields
    new_field = DataField('position', width=ndim, flags=['position'])
    ramses_fields.insert(0, new_field)
    
    return ramses_fields


def create_field_list(fields):
    """
    Create a field list from a list of fields
    """
    from . import extra_quantities
    field_set = set()
    
    # Add field names
    for field in fields:
        if field.extra is None:
            field_set.add(field.name)
        else:
            field_set.update(extra_quantities.get_field_names(field.extra))
    
    # We don't want 'position' in our field_list
    field_set.discard('position')
    if not field_set:
        field_list = []
    else:
        field_list = list(field_set)

    return field_list


def get_cell_data(x_field, x_index, y_field, y_index,
                  data_limits, step, shared):
    """
    Obtain cell data for x_axis and y_axis, filtering with data_limits
    Neither axis is a coordinate axis
    """
    from . import extra_quantities

    # First, construct region filter - check for 'position' limits
    
    fields = []
    if x_field is not None:
        fields.append(x_field)
    if y_field is not None:
        fields.append(y_field)
    
    # If we are going to filter on a field, we need it!
    for limit in data_limits:
        fields.append(limit['field'])
    
    field_list = create_field_list(fields)
    
    mass_weighted = (shared.config.get('opts', 'weighting') == 'mass')
    if y_field.name == 'rho':
        mass_weighted = False
    if mass_weighted and not 'rho' in field_list:
        field_list.append('rho')
    
    # Get min/max region from boxlen
    box_length = step.box_length
    
    # Load data, running through box filter and then creating point dataset
    amr = step.data_set.amr_source(field_list)
    region = get_region_filter(box_length, data_limits, step)
    amr_region = pymses.filters.RegionFilter(region, amr)
    cell_source = pymses.filters.CellsToPoints(amr_region)
    
    # Now, construct function filter stack
    filter_stack = function_filter_stack(cell_source, data_limits)
    
    data_array_list = []
    weights_list = []
    
    # Flatten and calculate
    for cells in filter_stack[-1].iter_dsets():
    
        # Collect data
        if x_field is None and y_field is None:
            raise ValueError('No x or y fields!')
        elif x_field is None or y_field is None:
            temp_data_array = np.zeros((cells.npoints))
            x_data_view = temp_data_array
            y_data_view = temp_data_array
        else:
            temp_data_array = np.zeros((cells.npoints, 2))
            x_data_view = temp_data_array[:, 0].view()
            y_data_view = temp_data_array[:, 1].view()
    
        if cells.npoints > 0:
            if x_field is not None:
                if x_field.extra is not None:
                    x_data_view[:] = extract_cell_func(x_field, cells)()
                else:
                    scalar = (cells[x_field.name].ndim == 1)
                    if scalar:
                        x_data_view[:] = cells[x_field.name]
                    else:
                        x_data_view[:] = cells[x_field.name][:, x_index]
            
            if y_field is not None:
                if y_field.extra is not None:
                    y_data_view[:] = extract_cell_func(y_field, cells)()
                else:
                    scalar = (cells[y_field.name].ndim == 1)
                    if scalar:
                        y_data_view[:] = cells[y_field.name]
                    else:
                        y_data_view[:] = cells[y_field.name][:, y_index]
        
        data_array_list.append(temp_data_array)
        
        if mass_weighted:
            weights_list.append(cells.get_sizes()**3 * cells['rho'])
        else:
            weights_list.append(cells.get_sizes()**3)
        
        cells = None
    
    step.data_set = None
    
    if x_field is None or y_field is None:
        data_array = np.concatenate(data_array_list)
    else:
        data_array = np.vstack(data_array_list)
    data_array_list = None
    weights = np.concatenate(weights_list)
    weights_list = None
    
    return data_array, weights


def get_sample_data(x_field, x_index, xlim,
                    y_field, y_index, ylim,
                    resolution, data_limits, step, shared):
    """
    Obtain sample data for x_axis and y_axis, filtering with data_limits
    """
    from . import extra_quantities
    
    multiprocessing = (shared.config.get('opts', 'multiprocessing') == 'on')

    # First, construct region filter - check for 'position' limits
    
    fields = []
    x_pos, y_pos = False, False
    if x_field is not None:
        if x_field.name == 'position':
            x_pos = True
        fields.append(x_field)
    if y_field is not None:
        if y_field.name == 'position':
            y_pos = True
        fields.append(y_field)
    
    # If we are going to filter on a field, we need it!
    for limit in data_limits:
        fields.append(limit['field'])
    
    field_list = create_field_list(fields)
    
    mass_weighted = (shared.config.get('opts', 'weighting') == 'mass')
    if y_field.name == 'rho':
        mass_weighted = False
    if mass_weighted and not 'rho' in field_list:
        field_list.append('rho')
    
    # Get box length, coarse and fine resolution
    box_length = step.box_length
    coarse_res, fine_res = get_minmax_res(step.data_set)
    if resolution > fine_res:
        raise ValueError('Asking for more resolution than exists!')
    
    # Set up sampling points
    one_d_points = []
    for i in (0, 1, 2):
        one_d_points.append(np.linspace(0.5, resolution-0.5, resolution) /
                            resolution)
    
    if x_pos:
        dx = (xlim[1] - xlim[0]) / box_length[x_index]
        dx_fine = dx*fine_res
        x_max_points = min(dx_fine, resolution)
        if dx_fine < 1.0:
            raise ValueError('too small to sample!')
        x_step = int(2.0**np.ceil(np.log2(dx_fine/x_max_points)))
        x_res = fine_res / x_step
        x_points_full = np.linspace(0.5, x_res-0.5, x_res) * x_step / fine_res
        x_use = np.logical_and(xlim[0] <= x_points_full,
                               x_points_full < xlim[1])
        x_axis_points = x_points_full[x_use]
        one_d_points[x_index] = x_axis_points
        bins_x = np.empty(len(x_axis_points) + 1)
        bins_x[0:-1] = x_axis_points - (0.5 * x_step / fine_res)
        bins_x[-1] = x_axis_points[-1] + (0.5 * x_step / fine_res)
    else:
        bins_x = None
    
    if y_pos:
        dy = (ylim[1] - ylim[0]) / box_length[y_index]
        dy_fine = dy*fine_res
        y_max_points = min(dy_fine, resolution)
        if dy_fine < 1.0:
            raise ValueError('too small to sample!')
        y_step = int(2.0**np.ceil(np.log2(dy_fine/y_max_points)))
        y_res = fine_res / x_step
        y_points_full = np.linspace(0.5, y_res-0.5, y_res) * y_step / fine_res
        y_use = np.logical_and(ylim[0] <= y_points_full,
                               y_points_full < ylim[1])
        y_axis_points = y_points_full[y_use]
        one_d_points[y_index] = y_axis_points
        bins_y = np.empty(len(y_axis_points) + 1)
        bins_y[0:-1] = y_axis_points - (0.5 * y_step / fine_res)
        bins_y[-1] = y_axis_points[-1] + y_step / fine_res
    else:
        bins_y = None
    
    x_points = one_d_points[0]
    y_points = one_d_points[1]
    z_points = one_d_points[2]
    
    points = np.vstack(np.meshgrid(x_points,
                                   y_points,
                                   z_points)).reshape(3,-1).T
    
    # Load data, running through box filter and then creating point dataset
    amr = step.data_set.amr_source(field_list)
    region = get_region_filter(box_length, data_limits, step)
    amr_region = pymses.filters.RegionFilter(region, amr)
    
    # Now, construct function filter stack
    filter_stack = function_filter_stack(amr_region, data_limits)
    
    # Calculate sampled points
    sampled_dset = pymses.analysis.sample_points(filter_stack[-1], points,
                                                 add_cell_center=True)
                           # NOTE stupid bug in pymses means this doesn't work
                           # properly unless you have add_cell_center=True even
                           # if you don't use it
    
    step.data_set = None
    gc.collect()
    
    # Collect data
    if x_field is None and y_field is None:
        raise ValueError('No x or y fields!')
    elif x_field is None or y_field is None:
        data_array = np.zeros((sampled_dset.npoints))
        x_data_view = data_array
        y_data_view = data_array
    else:
        data_array = np.zeros((sampled_dset.npoints, 2))
        x_data_view = data_array[:, 0].view()
        y_data_view = data_array[:, 1].view()
    
    if sampled_dset.npoints > 0:
        if x_field is not None:
            if x_field.name=='position':
                x_data_view[:] = sampled_dset.points[:, x_index]
            elif x_field.extra is not None:
                x_data_view[:] = extract_cell_func(x_field, sampled_dset)()
            else:
                scalar = (sampled_dset[x_field.name].ndim == 1)
                if scalar:
                    x_data_view[:] = sampled_dset[x_field.name]
                else:
                    x_data_view[:] = sampled_dset[x_field.name][:, x_index]
        
        if y_field is not None:
            if y_field.name=='position':
                y_data_view[:] = sampled_dset.points[:, y_index]
            elif y_field.extra is not None:
                y_data_view[:] = extract_cell_func(y_field, sampled_dset)()
            else:
                scalar = (sampled_dset[y_field.name].ndim == 1)
                if scalar:
                    y_data_view[:] = sampled_dset[y_field.name]
                else:
                    y_data_view[:] = sampled_dset[y_field.name][:, y_index]
    
    if mass_weighted:
        weights = sampled_dset['rho']
    else:
        weights = np.ones(sampled_dset.npoints) #cells.get_sizes()
    
    return data_array, weights, (bins_x, bins_y)


def get_grid_data(x_field, x_index, xlim, y_field, y_index, ylim,
                  render_field, render_index, render_fac, render_transform,
                  vector_field, vector_fac, data_limits,
                  proj, resolution, z_slice, step, shared):
    """
    Obtain grid data for x_axis and y_axis, filtering with data_limits.
    """
    
    multiprocessing = (shared.config.get('opts', 'multiprocessing') == 'on')
    
    # First, construct region filter - check for 'position' limits
    axes = [0,1,2]
    axes.remove(x_index)
    axes.remove(y_index)
    z_axis = axes[0]
    z_axis_name = ['x', 'y', 'z'][z_axis]
    up_axis_name = ['x', 'y', 'z'][y_index]
    
    if x_field.name != 'position':
        raise ValueError('x field is not a position axis!')
    if y_field.name != 'position':
        raise ValueError('y field is not a position axis!')
    
    fields = [x_field, y_field, render_field]
    if vector_field is not None:
        fields.append(vector_field)
    
    # If we are going to filter on a field, we need it!
    for limit in data_limits:
        fields.append(limit['field'])
    
    field_list = create_field_list(fields)
    
    # Get box size region from boxlen
    box_length = step.box_length
    
    # Load data, running through box filter and then creating point dataset
    amr = step.data_set.amr_source(field_list)
    region = get_region_filter(box_length, data_limits, step)
    amr_region = pymses.filters.RegionFilter(region, amr)
    
    # Now, construct function filter stack
    filter_stack = function_filter_stack(amr_region, data_limits)
    
    # Set up box for camera
    box_min = np.zeros_like(box_length)
    #box_max = np.array(box_length)
    box_max = np.ones_like(box_length)
    
    box_min[x_index] = xlim[0] / box_length[x_index]
    box_max[x_index] = xlim[1] / box_length[x_index]
    box_min[y_index] = ylim[0] / box_length[y_index]
    box_max[y_index] = ylim[1] / box_length[y_index]
    box_centre = (box_max + box_min) / 2.0
    box_size = (box_max - box_min)
    box_size_xy = [box_size[x_index], box_size[y_index]]
    
    from pymses.analysis.visualization import Camera, ScalarOperator
    if render_field.width == 1:
        render_scalar = True
    else:
        render_scalar = False
    if render_field.extra is not None:
        render_func = extract_data_func(render_field)
        if render_transform is None:
            render_op = ScalarOperator(
                lambda dset: render_func(dset) * render_fac)
        else:
            render_op = ScalarOperator(
                lambda dset: render_transform[0](render_func(dset)*render_fac))
    else:
        if render_fac != 1.0:
            if render_scalar:
                if render_transform is None:
                    render_op = ScalarOperator(
                        lambda dset: render_fac * dset[render_field.name])
                else:
                    render_op = ScalarOperator(
                        lambda dset: render_transform[0](render_fac *
                            dset[render_field.name]))
            else:
                if render_transform is None:
                    render_op = ScalarOperator(
                        lambda dset: render_fac *
                            dset[render_field.name][..., render_index])
                else:
                    render_op = ScalarOperator(
                        lambda dset: render_transform[0](render_fac * 
                            dset[render_field.name][..., render_index]))
        else:
            if render_scalar:
                if render_transform is None:
                    render_op = ScalarOperator(
                        lambda dset: dset[render_field.name])
                else:
                    render_op = ScalarOperator(
                        lambda dset: render_transform[0](
                            dset[render_field.name]))
            else:
                if render_transform is None:
                    render_op = ScalarOperator(
                        lambda dset: dset[render_field.name][..., render_index])
                else:
                    render_op = ScalarOperator(
                        lambda dset: render_transform[0](
                            dset[render_field.name][..., render_index]))
    
    if proj:
        # Raytraced integrated plot
        # distance=0.5, far_cut_depth=0.5,
        cam = Camera(center=box_centre, line_of_sight_axis=z_axis_name,
                    region_size=box_size_xy, up_vector=up_axis_name,
                    map_max_size=resolution, log_sensitive=False)
        from pymses.analysis.visualization.raytracing import RayTracer
        rt = RayTracer(step.data_set, field_list)
        mapped_data = rt.process(render_op, cam,
                                 multiprocessing=multiprocessing)
    else:
        # Slice map
        z_slice = z_slice / box_length[z_axis]
        cam = Camera(center=box_centre, line_of_sight_axis=z_axis_name,
                    region_size=box_size_xy, up_vector=up_axis_name,
                    map_max_size=resolution, log_sensitive=False)
        from pymses.analysis.visualization import SliceMap
        mapped_data = SliceMap(amr_region, cam, render_op, z=z_slice)

    step.data_set = None
    gc.collect()

    return mapped_data.T


def get_region_filter(box_length, data_limits, step):
    """
    Create a region filter based on boxlen and data_limits
    """
    
    box_min = np.zeros_like(box_length)
    box_max = np.array(box_length)
    region_limits = (box_min, box_max)
    
    if not 'position' in [x['name'] for x in data_limits]:
        return pymses.utils.regions.Box(region_limits)
    
    for limit in data_limits:
        if limit['name'] == 'position':
            index = limit['index']
            min_limit, max_limit = limit['limits']
            if min_limit != 'none':
                region_limits[0][index] = max(region_limits[0][index],
                                              min_limit)
            if max_limit != 'none':
                region_limits[1][index] = min(region_limits[1][index],
                                              max_limit)
    
    return pymses.utils.regions.Box(region_limits)


def function_filter_stack(source, data_limits):
    """
    Construct a filter stack from data limits
    """
    filter_stack = [source]
    function_filters = []
    
    for limit in data_limits:
        if limit['name'] != 'position':
            name = limit['name']
            index = limit['index']
            min_f, max_f = limit['limits']
            code_mks = limit['field'].code_mks
            min_f = min_f / code_mks
            max_f = max_f / code_mks
            # Determine if field is scalar or vector
            if limit['width'] == 1:
                # scalar filters
                if min_f != 'none' and max_f != 'none':
                    filt_func = lambda dset: np.logical_and(min_f <= dset[name],
                                             dset[name] <= max_f)
                elif min_f != 'none':
                    filt_func = lambda dset: (min_f <= dset[name])
                elif max_f != 'none':
                    filt_func = lambda dset: (dset[name] <= max_f)
            else:
                # vector filters
                if min_f != 'none' and max_f != 'none':
                    filt_func = lambda dset: np.logical_and(
                        min_f <= dset[name][index], dset[name][index] <= max_f)
                elif min_f != 'none':
                    filt_func = lambda dset: (min_f <= dset[name][index])
                elif max_f != 'none':
                    filt_func = lambda dset: (dset[name][index] <= max_f)
            function_filters.append(filt_func)

    for filt_func in function_filters:
        new_source = pymses.filters.PointFunctionFilter(
            filt_func, filter_stack[-1])
        filter_stack.append(new_source)

    return filter_stack


def extract_cell_func(field, cells):
    """
    Extract cell data for extra quantities
    """
    from . import extra_quantities
    from . import python_math_parser
    
    # cell.points is position data
    # cell[field][:[,1:vec]] is field data
    
    lookup_table = []
    parsed = field.extra
    field_tuples = extra_quantities.get_field_tuples(parsed)
    for name, index, width in field_tuples:
        parse_string = str((name, index, width))
        if name=='position':
            parse_value = cells.points[:, index]
        else:
            #scalar = (cells[name].ndim == 1)
            if width==1:
                parse_value = cells[name]
            else:
                parse_value = cells[name][:, index]
        lookup_table.append((parse_string, parse_value))

    return python_math_parser.gen_calc(parsed, lookup_table)


def extract_data_func(field):
    """
    Extract data for extra quantities
    """
    from . import extra_quantities
    from . import python_math_parser
    
    # cell.points is position data
    # cell[field][:[,1:vec]] is field data
    
    #lambda dset: dset[render_field_name] * render_fac)
    
    lookup_table = []
    parsed = field.extra
    field_tuples = extra_quantities.get_field_tuples(parsed)
    for name, index, width in field_tuples:
        parse_string = str((name, index, width))
        if name=='position':
            def parse_value(dset, index=index):
                return dset.points[:, index]
        else:
            #scalar = (cells[name].ndim == 1)
            if width==1:
                def parse_value(dset, name=name):
                    return dset[name]
            else:
                def parse_value(dset, name=name):
                    return dset[name][..., index]
        lookup_table.append((parse_string, parse_value))

    return python_math_parser.gen_calc(parsed, lookup_table)


def add_subtract_unit(a, b):
    """
    Utility function for unit calculations: can only add or subtract
    identical quantities
    """
    if isinstance(a, float) :
        if isinstance(b, float):
            return pymses.utils.constants.Unit((0,0,0,0,0,0), 1.0)
        else:
            return b
    elif isinstance(b, float):
        return a
    elif any(a.dimensions != b.dimensions) or a.val != b.val:
        raise ValueError('Invalid unit operation: add/subtract '
                         '{} and {}!'.format(a, b))
    else:
        return a


def multiply_unit(a, b):
    """
    Utility function for unit calculations: multiply
    """
    if isinstance(a, float):
        if isinstance(b, float):
            return pymses.utils.constants.Unit((0,0,0,0,0,0), 1.0)
        else:
            return b
    elif isinstance(b, float):
        return a
    else:
        return a * b


def divide_unit(a, b):
    """
    Utility function for unit calculations: divide
    """
    if isinstance(a, float):
        if isinstance(b, float):
            return pymses.utils.constants.Unit((0,0,0,0,0,0), 1.0)
        else:
            return b
    elif isinstance(b, float):
        return a
    else:
        return a / b


def calc_units_mks(shared, field):
    """
    Run over parsed, substituting in code_mks for each field
    """
    from . import python_math_parser
    from . import extra_quantities
    
    unit_unary_dict = {'-': (lambda x: x),
                       '|': (lambda x: x)}
    unit_binary_dict = {'+': (lambda x, y: add_subtract_unit(x, y)),
                        '-': (lambda x, y: add_subtract_unit(x, y)),
                        '*': (lambda x, y: multiply_unit(x, y)),
                        '/': (lambda x, y: divide_unit(x, y)),
                        '^': (lambda x, y: x**y)}

    lookup_table = []
    parsed = field.extra
    field_tuples = extra_quantities.get_field_tuples(parsed)
    for name, index, width in field_tuples:
        parse_string = str((name, index, width))
        parse_value = get_code_units_guess(shared.sim_step_list[0].units, name)
        lookup_table.append((parse_string, parse_value))

    mks = python_math_parser.gen_calc(
        parsed, lookup_table, unary_dict=unit_unary_dict,
        binary_dict=unit_binary_dict)()
    field.code_mks = mks.val

