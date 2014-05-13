# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (in press)
#
#

"""
Driver implementation for PyCUDA

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


try:
    import pyublas
except ImportError as exc:
    pyublas = None
    LOG.debug('pyublas unavailable')

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule as CUDASourceModule
from pycuda import gpuarray
import pycuda.tools

from . import base


class OccupancyRecord(pycuda.tools.OccupancyRecord):
    def __repr__(self):
        ret = "Occupancy(tb_per_mp=%d, limited_by=%r, "
              "warps_per_mp=%d, occupancy=%0.3f)"
        return ret % (self.tb_per_mp, self.limited_by, 
                      self.warps_per_mp, self.occupancy)

_, total_mem = cuda.mem_get_info()

from pycuda.curandom import XORWOWRandomNumberGenerator as XWRNG
rng = XWRNG()

# FIXME should be on the noise objects, but has different interface
# FIXME this is additive white noise
def gen_noise_into(devary, dt):
    gary = devary.device
    rng.fill_normal(gary)
    gary.set(gary.get()*sqrt(dt))


