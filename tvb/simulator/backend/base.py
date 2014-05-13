"Base backend driver classes"

import string
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

from . import templates

class Code(object):
    "Interface managing code to run on a device"

    def build_kernel(self, src=None, templ='tvb.cu', debug=False, **kwds):
        self.source = src or templates.sources[templ]
        self.kernel = string.Template(self.source).substitute(**kwds)
        if debug:
            temppath = os.path.abspath('./temp.cu')
            LOG.debug('completed template written to %r', temppath)
            with open(temppath, 'w') as fd:
                fd.write(source)


    @classmethod
    def build(cls, fns=[], T=string.Template, templ='tvb.cu', debug=False, **kwds):

        source = T(templates.sources[templ]).substitute(**args) 

        if debug:
            temppath = os.path.abspath('./temp.cu')
            LOG.debug('completed template written to %r', temppath)
            with open(temppath, 'w') as fd:
                fd.write(source)

        if using_gpu:
            cls.mod = CUDASourceModule("#define TVBGPU\n" + source, 
                                       options=["--ptxas-options=-v"])
        else:
            cls.mod = cee.srcmod("#include <math.h>\n" + source, fns)


class Global(object):
    "Interface to global (scalar) variables stored on device. "

    def __init__(self, name, dtype):
        self.code  = device_code
        self.name  = name
        self.dtype = dtype
        self.__post_init = True

    def post_init(self):
        self.__post_init = False

    # __get__
    # __set__


class Array(object):
    "Interface to N-dim. array stored on device"

    @property
    def cpu(self):
        if not hasattr(self, '_cpu'):
            self._cpu = zeros(self.shape).astype(self.type)
        return self._cpu

    @property
    def shape(self):
        return tuple(getattr(self.parent, k) for k in self.dimensions)

    @property
    def nbytes(self):
        bytes_per_elem = empty((1,), dtype=self.type).nbytes
        return prod(self.shape)*bytes_per_elem

    # @property device
    # @property value
    # def set(arg)

    def __init__(self, name, type, dimensions):
        self.parent = None
        self.name = name
        self.type = type
        self.dimensions = dimensions

class Driver(object):
    "Base driver class"

class RegionParallel(Driver):
    "Driver for parallel region simulations"

    _example_code = {
        'model_dfun': """
        float a   = P(0)
            , b   = P(1)
            , tau = P(2)
            , x   = X(0)
            , y   = X(1) ;

        DX(0) = (x - x*x*x/3.0 + y)*tau;
        DX(1) = (a + b*y - x + I(0))/tau;
        """,

        'noise_gfun': """
        float nsig;
        for (int i_svar=0; i_svar<n_svar; i_svar++)
        {
            nsig = P(i_svar);
            GX(i_svar) = sqrt(2.0*nsig);
        }
        """, 

        'integrate': """
        float dt = P(0);
        model_dfun(dx1, x, mmpr, input);
        noise_gfun(gx, x, nspr);
        for (int i_svar=0; i_svar<n_svar; i_svar++)
            X(i_svar) += dt*(DX1(i_svar) + STIM(i_svar)) + GX(i_svar)*NS(i_svar);
        """,

        'coupling': """
        // parameters
        float a = P(0);

        I = 0.0;
        for (int j_node=0; j_node<n_node; j_node++, idel++, conn++)
            I += a*GIJ*XJ;


        """
        }

    def build_kernel(self):
        args = dict()
        for k in 'model_dfun noise_gfun integrate coupling'.split():
            if k not in kwds:
                LOG.debug('using example code for %r', k)
                src = cls._example_code[k]
            else:
                src = kwds[k]
            args[k] = src

