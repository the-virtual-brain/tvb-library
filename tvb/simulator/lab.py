
"""
tvb.simulator.lab is a umbrella module designed to make console and scripting
work easier by importing all the simulator pieces at once.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import os
from time import time
import pdb

from numpy import * # for load & save not available in pylab
import numpy as np

import tvb.basic.config.settings
tvb.basic.config.settings.BaseProfile.TRAITS_CONFIGURATION.use_storage = 0
from tvb.simulator import (
        simulator, models, coupling, integrators, monitors, noise
        )
from tvb.datatypes import connectivity, surfaces, equations, patterns

from tvb.simulator.common import get_logger
LOG = get_logger(__name__)


"""
As an alternative, we change the profile as follows:

    from tvb.basic.profile import TvbProfile as tvb_profile
    tvb_profile.set_profile("CONSOLE_PROFILE")

"""

PDB = lambda : pdb.set_trace()

def file_exists(fname):
    """
    file_exists(fname) is a convenience function to test whether a file
    already exists or not. Returns True if we can stat the file, otherwise
    False.

    """
    try:
        os.stat(fname)
        return True
    except OSError:
        return False


def timed(fn, t=time):
    fn.times = []
    @functools.wraps(fn)
    def wrapper(*args, **kwds):
        tic = t()
        ret = fn(*args, **kwds)
        toc = t()
        fn.times.append(toc - tic)
        return ret
    return wrapper


# try to import plotting tools and matplotlib
if 'DISPLAY' in os.environ:
    try:
        from tvb.simulator.plot.tools import *
        from matplotlib.pyplot import *
    except ImportError as exc:
        LOG.warning("Plotting tools will not be available: %s:", exc)

