
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


