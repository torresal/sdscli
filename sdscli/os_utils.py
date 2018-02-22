from __future__ import absolute_import
from __future__ import print_function

import os

from sdscli.log_utils import logger


def makedirs(d, mode=0777):
    """Make directory along with any parent directory that may be needed."""

    try: os.makedirs(d, mode)
    except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(d): pass
        else: raise

    
def validate_dir(d, mode=0755, noExceptionRaise=False):
    """Validate that a directory can be written to by the current process and return 1.
       Otherwise, try to create it.  If successful, return 1.  Otherwise return None."""

    if os.path.isdir(d):
        if os.access(d, 7): return 1
        else: return None
    else:
        try:
            makedirs(d, mode)
            os.chmod(d, mode)
        except:
            if noExceptionRaise: pass
            else: raise
        return 1
