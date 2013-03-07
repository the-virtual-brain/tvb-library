
"""
This has been copied from the main clause of the models module

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

raise ImportError('module needs to be rewritten')


if __name__ == "__main__":
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()

    #Initialise Models in their default state:
    WILSON_COWAN_MODEL = WilsonCowan()
    REDUCED_SET_FITZHUGH_NAGUMO_MODEL = ReducedSetFitzHughNagumo()
    REDUCED_SET_HINDMARSH_ROSE_MODEL = ReducedSetHindmarshRose()
    JANSEN_RIT_MODEL = JansenRit()
    GENERIC_2D_MODEL = Generic2dOscillator()
    BRUNEL_WANG_MODEL = BrunelWang()
    WONG_WANG_MODEL = WongWang()


    LOG.info("All Models initialised in their default state without error...")
