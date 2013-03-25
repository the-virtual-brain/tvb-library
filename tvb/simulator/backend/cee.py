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

"""
This module enables execution of generated C code.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import tempfile
import subprocess
import ctypes

def dll(src, libname,
        args=['gcc', '-std=c99', '-fPIC', '-shared', '-lm'],
        debug=False):

    if debug:
        file = open('temp.c', 'w')
    else:
        file = tempfile.NamedTemporaryFile(suffix='.c')

    with file as fd:
        fd.write(src)
        fd.flush()
        if debug:
            args.append('-g')
        else:
            args.append('-O3')
        ret = subprocess.call(args + [fd.name, '-o', libname])

    return ret

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

        

