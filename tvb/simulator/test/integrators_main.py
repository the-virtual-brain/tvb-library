
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
