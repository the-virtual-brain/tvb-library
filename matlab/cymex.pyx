"""
cymex.pyx
---------

Implements a MEX function bridge to Python in "pure" Cython. 

While the name MATLAB is used here, this code was written 
and debugged with Octave, a MATLAB clone.

mw@eml.cc 2013

"""

import sys, numpy as np
cimport numpy as np


cdef extern from *:

    # some const defintions are required
    ctypedef char*     const_char_ptr        "const char*"
    ctypedef mxArray*  const_mxArray_ptr     "const mxArray*"
    ctypedef mxArray** const_mxArray_ptr_ptr "const mxArray**"
    
    # module initialization function
    void initcymex()

cdef extern from "Python.h":
    # http://docs.python.org/2/c-api/init.html
    void Py_Initialize()
    int Py_IsInitialized()

"""
This is going to be fun, because MATLAB plays tricks wiht 
library loading. Maybe someone at Mathworks could help out here.
"""
cdef extern from "dlfcn.h":
    int RTLD_LAZY, RTLD_GLOBAL
    void *dlopen(const_char_ptr fname, int flag)
    
cdef extern from "mex.h":

    # MATLAB's N-dimensional array type (opaque)
    ctypedef struct mxArray:
        pass

    # functions from MATLAB's documented extern API
    int mexPrintf(char *msg, ...)
    int mexEvalString(const_char_ptr cmd)
    int mxGetN(mxArray*pm)
    void* mxMalloc(int)
    int mxGetString(mxArray*pm, char*str, int strlen)
    int mexCallMATLAB(int nlhs, mxArray **plhs,
                      int rlhs, mxArray **prhs, const_char_ptr cmd)

    # may longjmp? could screw the pooch with p/cython
    void mexErrMsgTxt(const_char_ptr msg) 
    void mexErrMsgIdAndTxt(const_char_ptr id, const_char_ptr txt, ...)

cdef extern from *:
    #cdef extern from "matrix.h":

    mxArray *mxCreateDoubleMatrix(int m, int n, int flag)
    double *mxGetPr(const_mxArray_ptr pm)
    int mxGetNumberOfElements(const_mxArray_ptr pm)
    void mxSetPr(mxArray *pm, double *x)
    mxArray *mxCreateString(const_char_ptr s)

    # http://www.mathworks.com/help/matlab/apiref/mxclassid.html
    ctypedef enum mxClassID:

        mxUNKNOWN_CLASS
        mxCELL_CLASS
        mxSTRUCT_CLASS
        mxLOGICAL_CLASS
        mxCHAR_CLASS
        mxVOID_CLASS
        mxFUNCTION_CLASS

        # mxClassID Value   MATLAB Type     MEX Type    C Type                  numpy.dtype

        mxDOUBLE_CLASS  #   double          double      double                  float64
        mxSINGLE_CLASS  #   single          float       float                   float32
        mxINT8_CLASS    #   int8            int8_T      char, byte              byte, int8
        mxUINT8_CLASS   #   uint8           uint8_T     unsigned char, byte     ubyte, uint8
        mxINT16_CLASS   #   int16           int16_T     short                   etc.
        mxUINT16_CLASS  #   uint16          uint16_T    unsigned short
        mxINT32_CLASS   #   int32           int32_T     int
        mxUINT32_CLASS  #   uint32          uint32_T    unsigned int
        mxINT64_CLASS   #   int64           int64_T     long long
        mxUINT64_CLASS  #   uint64          uint64_T    unsigned long long

    mxClassID mxGetClassID(const_mxArray_ptr pm)

# redirect Python output to MATLAB
class mexPrinter(object):
    def write(self, msg):
        mexPrintf(msg)

import sys
sys.stdout = mexPrinter()
sys.stderr = mexPrinter()

cdef mstr(mxArray* arr):
    "Convert MATLAB string to Python string"
    cdef:
        int buflen, status
        char *buf
    buflen = mxGetN(arr)*sizeof(char)+1
    buf = <char*> mxMalloc(buflen)
    status = mxGetString(arr, buf, buflen)
    return buf[:buflen-1] if status == 0 else ''

cdef mlsin(int n):
    "Test calling MATLAB functions from Cython"
    cdef mxArray *l, *r
    l = mxCreateDoubleMatrix(1, 1, 0)
    r = mxCreateDoubleMatrix(1, 1, 0)
    cdef double *dp = <double*> mxGetPr(r)
    for i in range(n):
        dp[0] = i*1e-10
        mexCallMATLAB(1, &l, 1, &r, "sin")
    return (<double*>mxGetPr(l))[0]

cdef mlread(int nlhs, mxArray* lhs[],
            int nrhs, const_mxArray_ptr_ptr rhs):
    "Pass up to 49 2D NumPy arrays to MATLAB"
    if not nlhs == (nrhs-1):
        print "[a, b, c, ...] = cymex('r', 'a', 'b', 'c', ...);"
        return
    cdef double *l, *r
    cdef np.ndarray[np.float64_t, ndim=2] nd
    for i in range(nrhs-1):
        nd = np.atleast_2d(eval(mstr(rhs[i+1])).astype(np.float64, order="F"))
        print nd.shape[0], nd.shape[1]
        lhs[i] = mxCreateDoubleMatrix(nd.shape[0], nd.shape[1], 0)
        l = <double*> mxGetPr(lhs[i])
        r = <double*> nd.data
        for j in range(nd.size):
            l[j] = r[j]

cdef mlrepl():
    "Enter interactive Python console in MATLAB"
    cdef:
        mxArray *arg[2], *ret
    print "Entering Python command line, type .q or quit or exit to return"
    arg[0] = mxCreateString(">>> ")
    arg[1] = mxCreateString("s")
    while True:
        mexCallMATLAB(1, &ret, 2, arg, "input")
        if mstr(ret) in ('.q', 'quit', 'exit'):
            break
        else:
            exec mstr(ret) in globals()
    print "Returning to MATLAB/Octave"

cdef mlwrite(int nlhs, mxArray* lhs[],
             int nrhs, const_mxArray_ptr_ptr rhs):
    "Pass up to 24 MATLAB arrays to Python, with given name"
    if not nrhs%2 == 1:
        print "cymex('w', 'a', a, 'b', b, 'c', c, ...);"
        return 

    cdef:
        np.ndarray[np.float64_t, ndim=1] nd
        const_mxArray_ptr rhi
        int *rhi_sh
        double *l, *r

    for i in range((nrhs-1)/2):
        assert mxGetClassID(rhs[2*i+1])==mxCHAR_CLASS
        rhi = rhs[2*i+2]
        nd = np.empty((mxGetNumberOfElements(rhi),), np.float64)
        #rhi_sh = mxGetDimensions(rhi)
        l = <double*> nd.data
        r = <double*> mxGetPr(rhi)
        for j in range(nd.size):
            l[j] = r[j]           
        globals()[mstr(rhs[2*i+1])] = nd

cdef mltest(int nlhs, mxArray* lhs[],
             int nrhs, const_mxArray_ptr_ptr rhs):
    "Run various tests in Cython"
    if not nrhs>1:
        print "cymex test [np/blas/lapack/mlsin1/mlsinn]"
        return

    if mstr(rhs[1]) == 'np':                     # ok 
        import numpy
        print numpy.random.randn(10)

    elif mstr(rhs[1]) == 'blas':                 # ok
        import numpy
        A = numpy.ones((3, 3))
        b = numpy.ones((3, ))
        print A.dot(b)
        
    elif mstr(rhs[1]) == 'lapack':               # MKL ERROR: Parameter 5 was incorrect on entry to DGESDD
        from numpy import linalg, r_
        A = r_[:20].reshape((4,5))
        print linalg.svd(A)[1]
        
    elif mstr(rhs[1]) == 'mlsin1':
        print mlsin(1)
        
    elif mstr(rhs[1]) == 'mlsinn': # 1e3 calls cymex mlsinn -> 6.3 s
        mlsin(int(1e3))

def insert_path(p, post=False):
    "Add to path if not already there"
    if not p in sys.path:
        print 'adding %s to Python path' % (p,)
        sys.path.append(p)


def gen_interface(f):
    """
    Generate a MATLAB function in current directory corresponding
    to the passed function.

    returns arguments always a cell array of Python's return tuple
    except when there's only one.

    TODO: This should be expanded to work with the traits definitions
    on classes so that running

    >> help tvb_models

    in MATLAB gives the appropriate help 

    """
    from inspect import getargspec
    ar, va, vk, df = getargspec(f)
    fn = f.__module__ + '_' + f.func_name
    if fn[0] == '_':
        fn[0] = 'u'
    fn = fn.replace('.', '_')
    with open(fn+'.m', 'w') as fd:
        fd.write("""function ret = {fname}({rhs})
{doc}
{writes}
cymex exec {fname}()
ret = cymex('r', '__ret')
""".format(rhs = ', '.join(ar),
           writes = '\n'.join(["cymex('w', %s);" % (a,) for a in ar]),
           fname=fn,
           doc='\n'.join(["% " + l for l in f.__doc__.split('\n')]) if f.__doc__ else '% '
           ))

echo = False
        
cdef public void mexFunction(int nlhs, mxArray* lhs[],
                             int nrhs, const_mxArray_ptr_ptr rhs):
    """
    Entry point when calling cymex in MATLAB code. It is 
    performant enough, 1e6 calls takes just a few seconds.

    """

    global echo

    if not Py_IsInitialized(): # is just { return initialized; }
        mexPrintf("starting cymex... ")
        dlopen("libpython2.7.so", RTLD_LAZY | RTLD_GLOBAL)
        Py_Initialize()
        initcymex()
        mexPrintf("done!\n")

    if nrhs == 0 or not mxGetClassID(rhs[0]) == mxCHAR_CLASS:
        mexErrMsgTxt("[output] = cymex('cmd', ...)")
        return

    try:

        # consider first argument to mex function as the command
        # if this becomes bottleneck, switch to ints
        cmd = mstr(rhs[0])

        if cmd == 'test':
            mltest(nlhs, lhs, nrhs, rhs)
           
        elif cmd == 'x':
            code = ' '.join([mstr(rhs[i]) for i in range(1, nrhs)])
            if echo:
                print code
            exec code in globals()

        elif cmd == 'r': 
            mlread(nlhs, lhs, nrhs, rhs)

        elif cmd == 'w':
            mlwrite(nlhs, lhs, nrhs, rhs)

        elif cmd == 'repl':
            mlrepl()

        elif cmd == 'echo':
            echo = True if mstr(rhs[1])=='on' else False

        else:
            print '?', repr(cmd), nrhs


    except Exception as e:
        #raise e
        import traceback, cStringIO
        cs = cStringIO.StringIO()
        traceback.print_exc(file=cs)
        txt = cs.getvalue()
        mexErrMsgTxt(txt)

    return # mexFunction
