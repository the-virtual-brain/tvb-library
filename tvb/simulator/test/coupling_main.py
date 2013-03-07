
"""
This has been copied from the main clause of the coupling module

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

raise ImportError('module needs to be rewritten')


if __name__ == "__main__":
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()

    #Initialise Couplings:
    LINEAR_COUPLING = Linear()
    SCALING_COUPLING = Scaling()
    SIGMOIDAL_COUPLING = Sigmoidal()
    LOG.info("All Couplings initialised without error...")


