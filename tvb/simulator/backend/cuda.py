
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


