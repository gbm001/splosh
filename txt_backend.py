"""
This submodule implements the TXT backend.
"""

from __future__ import print_function
import numpy as np
from stream_backend import BackendStream

class BackendTXT(BackendStream):
    """
    Backend for writing to text files
    """
    
    def __init__(self):
        BackendStream.__init__(self)
        self.name = '\TXT'
        self.long_name = 'TXT ascii file backend'
        self.extension = '.txt'
        
    def output_canvas(self):
        """
        Output canvas
        """
        import numpy as np
        filename = self.output_filename + self.extension
        print('Writing to file {}...'.format(filename))
        with open(filename, 'wt') as f:
            np.savetxt(f, self.data_array)
