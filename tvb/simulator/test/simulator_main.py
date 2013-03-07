
"""
Re-copied from the main clause of the simulator.simulator module to testing.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
"""

from tvb.simulator.lab import *

raise ImportError('this module needs to be rewritten')

# See simulator_tester.py
if __name__ == '__main__':

    #Import from tvb.simulator modules:
    import tvb.simulator.noise

    #Initialise  Connectivity, Coupling, and a Model
#    CM = coupling_dtype.LinearCoupling()
#    CM.parameters['a']=-0.0152
    CM = coupling_module.Linear(a=-0.0152)
    CONNECTIVITY = connectivity_dtype.Connectivity()
    CONNECTIVITY.speed = numpy.array([7.0])

    MODEL = models_module.Generic2dOscillator()

    #Initialise some Monitors with period in physical time
    MOMO = monitors_module.Raw()
    MIMI = monitors_module.GlobalAverage(period=2**-2)
    MEME = monitors_module.SubSample(period=2**-2)
    MAMA = monitors_module.TemporalAverage(period=2**-2)

    #Bundle them
    MONITORS = (MOMO, MIMI, MEME, MAMA)

    #Initialise an Integrator
    NOISE = tvb.simulator.noise.Additive(nsig = numpy.array([0.00390625,]))
    HEUNINT = integrators_module.HeunStochastic(dt=2**-4, noise=NOISE)

    #Initialise a Simulator -- NetworkModel, Integrator, and Monitors.
    SIM = Simulator(model = MODEL,
                    connectivity = CONNECTIVITY,
                    coupling = CM,
                    integrator = HEUNINT,
                    monitors = MONITORS)

    SIM.configure()

    #Perform the simulation
    RAW_DATA = []
    GAVG_DATA = []
    SUBSAMP_DATA = []
    TAVG_DATA = []

    for raw, gavg, subsamp, tavg in SIM(simulation_length=2**6):
        if not raw is None:
            RAW_DATA.append(raw)
        if not gavg is None:
            GAVG_DATA.append(gavg)
        if not subsamp is None:
            SUBSAMP_DATA.append(subsamp)
        if not tavg is None:
            TAVG_DATA.append(tavg)



