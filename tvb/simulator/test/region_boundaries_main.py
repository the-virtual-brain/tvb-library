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
This has been copied from the main clause of the region_boundaries module

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

raise ImportError('module needs to be rewritten')


if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module... 
    LOG.info("Testing %s ..." % __file__)

    import tvb.simulator.surfaces as surfaces_module
    CORTEX = surfaces_module.Cortex()

    CORTEX_BOUNDARIES = RegionBoundaries(CORTEX)


