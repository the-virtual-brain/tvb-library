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
Driver implementation for C99 + OpenMP

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import tempfile
import subprocess
import ctypes
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

try:
    import psutil
except Exception as exc:
    LOG.exception(exc)
    LOG.warning('psutil not available, no memory checks will be performed')


from . import base


total_mem = psutil.phymem_usage().total

# FIXME this is additive white noise
def gen_noise_into(devary, dt):
    devary.cpu[:] = random.normal(size=devary.shape)
    devary.cpu[:] *= sqrt(dt)


def dll(src, libname,
        args=['gcc', '-std=c99', '-fPIC', '-shared', '-lm'],
        debug=False):

    if debug:
        file = open('temp.c', 'w')
    else:
        file = tempfile.NamedTemporaryFile(suffix='.c')
    LOG.debug('open C file %r', file)

    with file as fd:
        fd.write(src)
        fd.flush()
        if debug:
            args.append('-g')
        else:
            args.append('-O3')
        args += [fd.name, '-o', libname]
        LOG.debug('calling %r', args)
        proc = subprocess.Popen(args, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        proc.wait()
        LOG.debug('return code %r', proc.returncode)
        if proc.returncode > 0:
            LOG.error('failed compilation:\n%s\n%s', proc.stdout.read(), proc.stderr.read())

class srcmod(object):

    def __init__(self, src, fns, debug=False, printsrc=False):

        if src.__class__.__module__ == 'cgen':
            self.src = '\n'.join(src.generate())
        else:
            self.src = src

        if printsrc:
            print "srcmod: source is \n%s" % (self.src,)

        if debug:
            dll(self.src, 'temp.so', debug=debug)
            self._module = ctypes.CDLL('temp.so')
        else:
            with tempfile.NamedTemporaryFile(suffix='.so') as fd:
                dll(self.src, fd.name, debug=debug)
                self._module = ctypes.CDLL(fd.name)

        for f in fns:
            fn = getattr(self._module, f)
            if debug:
                def fn_(*args, **kwds):
                    try:
                        ret = fn(*args, **kwds)
                    except Exception as exc:
                        msg = 'ctypes call of %r failed w/ %r'
                        msg %= (f, exc)
                        raise Exception(msg)
                    return ret
            else:
                fn_ = fn
            setattr(self, f, fn_)

class C99Compiler(object):
    def __call__(self, src, libname, debug=False, io=subprocess.PIPE):
        args = [self.cmd] + self.flags
        if debug:
            file = open('temp.c', 'w')
        else:
            file = tempfile.NamedTemporaryFile(suffix='.c')
        LOG.debug('open C file %r', file)
        with file as fd:
            fd.write(src)
            fd.flush()
            if debug:
            args.append(self.g_flag if debug else self.opt_flag)
            args += [fd.name, '-o', libname]
            LOG.debug('calling %r', args)
            proc = subprocess.Popen(args, stdout=io, stderr=io)
            proc.wait()
            LOG.debug('return code %r', proc.returncode)
            if proc.returncode > 0:
                LOG.error('failed compilation:\n%s\n%s', 
                        proc.stdout.read(), proc.stderr.read())


class GCC(C99Compiler):
    cmd = 'gcc'
    flags = ['-std=c99', '-fPIC', '-shared', '-lm']
    g_flag = '-g'
    opt_flag = '-O3'


class Code(base.Code):
    "Interface to C code"

    def __init__(self, *args, cc=None, **kwds):
        super(Code, self).__init__(*args, **kwds)
        self.cc = cc or GCC()

    def build_module(self, fns, debug=False):

        if debug:
            self.cc(self.src, 'temp.so', debug=debug)
            self._module = ctypes.CDLL('temp.so')
        else:
            with tempfile.NamedTemporaryFile(suffix='.so') as fd:
                self.cc(self.src, fd.name, debug=debug)
                self._module = ctypes.CDLL(fd.name)

        for f in fns:
            fn = getattr(self._module, f)
            if debug:
                def fn_(*args, **kwds):
                    try:
                        ret = fn(*args, **kwds)
                    except Exception as exc:
                        msg = 'ctypes call of %r failed w/ %r'
                        msg %= (f, exc)
                        raise Exception(msg)
                    return ret
            else:
                fn_ = fn
            setattr(self, f, fn_)

