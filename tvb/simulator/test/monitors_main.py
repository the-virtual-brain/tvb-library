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
This has been copied from the main clause of the monitors module

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

raise ImportError('module needs to be rewritten')


# Do some basic testing if run as main...
if __name__ == '__main__':
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()

    #Initialise Monitors:
    MONITOR_RAW = Raw()
    MONITOR_SUB_SAMPLE = SubSample(period=2**-4)
    MONITOR_GLOBAL_AVERAGE = GlobalAverage(period=2**-4)
    MONITOR_TMPORAL_AVERAGE = TemporalAverage(period=2**-4)
    MONITOR_SPATIAL_AVERAGE = SpatialAverage(period=2**-4)
    MONITOR_EEG = EEG(period=2**-4)
    MONITOR_BOLD = Bold()
    LOG.info("All Monitors initialised without error...")

    #Configure Monitors:
#        
#    import tvb.simulator.surfaces as surfaces
#    CORTEX = surfaces.Cortex()
#        , spatial_mask=CORTEX.region_mapping
#    LOG.info("All Monitors configured without error...")
