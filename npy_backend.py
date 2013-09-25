"""
This submodule implements the NPY backend.
"""

from __future__ import print_function
import numpy as np
from stream_backend import BackendStream

class BackendNPY(BackendStream):
    """
    Backend for writing to Numpy binary files
    """
    
    def __init__(self):
        BackendStream.__init__(self)
        self.name = '\NPY'
        self.long_name = 'Numpy binary file backend'
        self.extension = '.npy'
        
    def output_canvas(self):
        """
        Output canvas
        """
        import numpy as np
        filename = self.output_filename + self.extension
        print('Writing to file {}...'.format(filename))
        with open(filename, 'wb') as f:
            np.save(f, self.data_array)
