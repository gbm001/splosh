"""
This submodule implements a few string-related helpers
"""
from . import __significant_figures

def round_to_n(x, n=__significant_figures):
   # Stolen from Tim Peters
   if n < 1:
      raise ValueError("number of significant digits must be >= 1")
   # Use %e format to get the n most significant digits, as a string.
   format = "%." + str(n-1) + "e"
   as_string = format % x
   return float(as_string)


def find_best_spacing(lines_in, len_line):
    # Attempt to spread options more evenly
    
    lines = lines_in[:]
    
    num_lines = len(lines)
    total_length = sum([find_line_length(x) for x in lines])
    average_length = float(total_length) / float(num_lines)
    
    lsqd, residuals, residuals_sqd = least_squares_lines(lines, average_length)
    # Keep track of whether we have already considered doing something
    # with this column. Every change resets this.
    considered_column = [False]*num_lines
    while True:
        if all(considered_column):
            # we have considered all columns, give up
            break
        col = find_max_masked(residuals_sqd, considered_column)
        col_length = find_line_length(lines[col])
        push_left = False
        push_right = False
        pull_left = False
        pull_right = False
        # if residual is negative, we want to move things into this column from
        # a larger one, otherwise we want to move things out of this column
        # into a smaller one
        col_residual = residuals[col]
        
        if col==0:
            diff_left = 0
        else:
            diff_left = find_line_length(lines[col-1]) - col_length
        
        if col==num_lines-1:
            diff_right = 0
        else:
            diff_right = find_line_length(lines[col+1]) - col_length
        
        if col_residual == 0:
            # highly unlikely! somehow we are done.
            break
        elif col_residual < 0:
            # find the bigger column to move things from
            if diff_left <= 0 and diff_right <= 0:
                # both columns are smaller
                # no move would be sensible, give up on this column for now
                considered_column[col] = True
                continue
            elif diff_left > diff_right:
                # left column is bigger
                pull_left = True
            else:
                # right column is bigger
                pull_right = True
        elif col_residual > 0:
            # find the smaller column to move things into
            if diff_left >= 0 and diff_right >= 0:
                # both other columns are larger
                # no move would be sensible, give up on this column for now
                considered_column[col] = True
                continue
            elif diff_left < diff_right:
                # left column is smaller
                push_left = True
            else:
                # right column is smaller
                push_right = True
        
        # Attempt to move an item
        if pull_left or push_left:
            left_col = col - 1
            right_col = col
        else:
            left_col = col
            right_col = col + 1
        
        left = lines[left_col][:]
        right = lines[right_col][:]
        
        if pull_left or push_right:
            # move an item from the end of the left column to the 
            # start of the right column
            right.insert(0, left.pop())
        else:
            # move an item from the start of the right column to the
            # end of the left column
            left.append(right.pop(0))
        
        # Check that each line is now not too long
        if find_line_length(left) > len_line:
            considered_column[col] = True
            continue
        elif find_line_length(right) > len_line:
            considered_column[col] = True
            continue
        
        # Check we have reduced the total residuals
        new_lines = lines[:]
        new_lines[left_col] = left
        new_lines[right_col] = right
        lsqd_tuple = least_squares_lines(new_lines, average_length)
        if lsqd_tuple[0] >= lsqd:
            # we have not improved things
            considered_column[col] = True
            continue
        
        # Otherwise, update and continue
        lines = new_lines
        considered_column = [False]*num_lines
        
        lsqd, residuals, residuals_sqd = lsqd_tuple
    
    return lines
        

def find_max_masked(list_in, mask):
    if not list_in:
        raise ValueError('Nothing passed/empty list!')
    if all(mask):
        raise ValueError('All items masked!')
    cur_max = float('-inf')
    for i in range(len(list_in)):
        if mask[i]:
            continue
        item = list_in[i]
        if item > cur_max:
            max_col = i
            cur_max = item
    return max_col

    
def find_line_length(line):
    """
    Calculate the line length, where line is in
    [(option_id, length of option string), ...] format
    """
    return sum([x[1] for x in line])


def least_squares_lines(lines, average_length):
    """
    Calculate the least-squares distance to ideal line length for the lines
    provided in [line1, line2] format, where line is in
    [(option_id, length of option string), ...] format
    """
    residuals = []
    avg_sqd = average_length**2
    for line_tuple in lines:
        residuals.append(find_line_length(line_tuple) - average_length)
    
    residuals_sqd = [x**2 for x in residuals]
    
    return sum(residuals_sqd), residuals, residuals_sqd


def two_columns_text(string_left, string_right,
                     len_line, spacers=1):
    """
    Place a string 'string_left' and a string 'string_right' in two
    left-aligned columns, truncating if necessary, with a total line
    length of len_line. All columns spaced by 'spacers'.
    """
    
    sp = ' '*spacers
    available_line = len_line - spacers*2
    col_width = available_line // 2
    
    if (len(string_left) >= col_width):
        left_col = string_left[0:col_width]
    else:
        left_col = string_left.ljust(col_width)
        
    if (len(string_right) >= col_width):
        right_col = string_right[0:col_width]
    else:
        right_col = string_right.ljust(col_width)
    
    return '{}{}{}{}'.format(sp, left_col, sp, right_col)