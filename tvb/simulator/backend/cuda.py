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
Pycuda interop patterns


.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import time
import os
import string

try:
    import pyublas
except ImportError as exc:
    global __pyublas__available__
    __pyublas__available__ = False

try:
    import pycuda.autoinit
    import pycuda.driver
    import pycuda.gpuarray as gary
    from pycuda.compiler import SourceModule
    from pycuda.tools import DeviceData, OccupancyRecord

except Exception as exc:
    print "importing pycuda modules failed with exception", exc
    print "please check PATH and LD_LIBRARY_PATH variables"
    print os.environ
    print

def orinfo(n):
    orec = OccupancyRecord(DeviceData(), n)
    return """occupancy record information
        thread blocks per multiprocessor - %d
        warps per multiprocessor - %d
        limited by - %s
        occupancy - %f
    """ % (orec.tb_per_mp, orec.warps_per_mp, orec.limited_by, orec.occupancy)

#                                       dispo=pycuda.autoinit.device.total_memory()
def estnthr(dist, vel, dt, nsv, pf=0.7, dispo=1535*2**20                           ):
    n = dist.shape[0]
    idelmax = long(dist.max()/vel/dt)
    return long( (dispo*pf - 4*n*n + 4*n*n)/(4*idelmax*n + 4*nsv*n + 4 + 4) )


class arrays_on_gpu(object):

    def __init__(self, _timed="gpu timer", _memdebug=False, **arrays):

        self.__array_names = arrays.keys()

        if _memdebug:
            memuse = sum([v.size*v.itemsize for k, v in arrays.iteritems()])/2.**20
            memavl = pycuda.autoinit.device.total_memory()/2.**20
            print 'GPU mem use %0.2f MB of %0.2f avail.' % (memuse, memavl)
            for k, v in arrays.iteritems():
                print 'gpu array %s.shape = %r' % (k, v.shape)
            assert memuse <= memavl
    
        for key, val in arrays.iteritems():
            setattr(self, key, gary.to_gpu(val))

        self._timed_msg = _timed

    def __enter__(self, *args):
        self.tic = time.time()
        return self

    def __exit__(self, *args):

        if self._timed_msg:
            print "%s %0.3f s" % (self._timed_msg, time.time() - self.tic)

        for key in self.__array_names:
            delattr(self, key)

   
class srcmod(object):
    
    def __init__(self, src, fns, debug=False):

        self.src = src

        if debug:
            print "srcmod: source is \n%s" % (self.src,)

        self._module = SourceModule(self.src)

        for f in fns:
            fn = self._module.get_function(f)
            if debug:
                def fn_(*args, **kwds):
                    try:
                        fn(*args, **kwds)
                        pycuda.driver.Context.synchronize()
                    except Exception as exc:
                        msg = 'PyCUDA launch of %r failed w/ %r'
                        msg %= (fn, exc)
                        raise Exception(msg)
            else:
                fn_ = fn
            setattr(self, f, fn_)


