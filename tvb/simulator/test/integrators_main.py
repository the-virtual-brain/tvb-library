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
This has been copied from the main clause of the integrators module

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

raise ImportError('module needs to be rewritten')

# Do some basic testing if run as main...
if __name__ == '__main__':
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()

    #Initialise deterministic and stochastic Heun integrators:
    INTEGRATOR = HeunDeterministic(dt=2**-4)
    INTEGRATOR = HeunStochastic(dt=2**-4)
    INTEGRATOR.configure()

    #Initialise deterministic and stochastic Euler integrators:
    INTEGRATOR = EulerDeterministic(dt=2**-4)
    INTEGRATOR = EulerStochastic(dt=2**-4)
    INTEGRATOR.configure()

    #Initialise deterministic Runge-Kutta integrator:
    INTEGRATOR = RungeKutta4thOrderDeterministic(dt=2**-4)

    LOG.info("All integrators initialised without error...")
