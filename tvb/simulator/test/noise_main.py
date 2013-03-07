
"""
This has been copied from the main clause of the noise module

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

raise ImportError('module needs to be rewritten')


if __name__ == "__main__":
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()

    #Initialise Noises in their default state:
    NOISE_STREAM = RandomStream()
    NOISE = Additive()
    NOISE = Multiplicative()  
    print "All Noises initialised in their default state without error..."
