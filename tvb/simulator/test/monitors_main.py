
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
