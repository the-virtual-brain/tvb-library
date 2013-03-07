
"""
Profiling example for running a stochastic surface simulation with EEG and 
BOLD.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

from tvb.simulator.lab import *
from time import time

lconn = surfaces.LocalConnectivity(
        equation=equations.Gaussian(),
        cutoff=30.0,
        )

lconn.equation.parameters['sigma'] = 10.0
lconn.equation.parameters['amp']   = 0.0


sim = simulator.Simulator(
        model        = models.Generic2dOscillator(),
        connectivity = connectivity.Connectivity(speed=4.0),
        coupling     = coupling.Linear(a=-2**-9),
        integrator   = integrators.HeunStochastic(
                            dt=2**-4,
                            noise=noise.Additive(nsig=ones((2,))*0.001)
                            ),
        monitors     = (
            monitors.EEG(period=1e3/2**10), # 1024 Hz
            monitors.Bold(period=500)       # 0.5  Hz
            ),
        surface      = surfaces.Cortex(
            local_connectivity = lconn,
            coupling_strength  = array([0.01])
            ),
        )

sim.configure()

# set delays to mean
print sim.connectivity.idelays
sim.connectivity.delays[:] = sim.connectivity.delays.mean()
sim.connectivity.set_idelays(sim.integrator.dt)
print sim.connectivity.idelays

1/0
ts_eeg, ys_eeg = [], []
ts_bold, ys_bold = [], []

tic = time()
for eeg, bold in sim(60e3):
    if not eeg is None:
        t, y = eeg
        ts_eeg.append(t)
        ys_eeg.append(y)
    if not bold is None:
        t, y = bold
        ts_bold.append(t)
        ys_bold.append(y)
    print t

print '1024 ms took %f s' % (time() - tic,)


save('ts_eeg.npy', squeeze(array(ts_eeg)))
save('ys_eeg.npy', squeeze(array(ys_eeg)))
save('ts_bold.npy', squeeze(array(ts_bold)))
save('ys_bold.npy', squeeze(array(ys_bold)))
