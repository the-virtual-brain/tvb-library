
"""
Test history in simulator.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import numpy as np
try:
    from tvb.tests.library.base_testcase import BaseTestCase
except:
    pass
from tvb.simulator import simulator as sim


class IdCoupling(sim.coupling_module.Coupling):
    "Implements an identity coupling function."
    def __call__(self, g_ij, x_i, x_j):
        return (g_ij * x_j).sum(axis=2).transpose((1, 0, 2))

class Sum(sim.models_module.Model):
    nvar = 1
    _nvar = 1
    state_variables_range = {'x': [0, 100]}
    variables_of_interest = sim.basic.Enumerate(default=['x'], options=['x'])
    cvar = np.array([0])
    def dfun(self, X, coupling, local_coupling=0):
        return X + coupling + local_coupling


class ExactPropagationTests(BaseTestCase):

    def build_simulator(self, n=4):
        conn = np.zeros((n, n), np.int32)
        for i in range(conn.shape[0] - 1):
            conn[i, i+1] = 1
        dist = np.r_[:conn.size].reshape(conn.shape)
        self.sim = sim.Simulator(
            conduction_speed=1,
            coupling=IdCoupling(),
            surface=None,
            stimulus=None,
            integrator=sim.integrators_module.Identity(dt=1),
            initial_conditions=np.ones((n*n, 1, n, 1)),
            simulation_length=10,
            connectivity=sim.connectivity_dtype.Connectivity(
                weights=conn,
                tract_lengths=dist
            ),
            model=Sum(),
            monitors=(sim.monitors_module.Raw(), ),
            )
        self.sim.configure()

    def test_propagation(self):
        n = 4
        self.build_simulator(n=n)
        if False:
            print self.sim.connectivity.weights
            print self.sim.connectivity.delays
        x = np.zeros((n, ))
        xs = []
        for (t, raw), in self.sim():
            xs.append(raw.flat[:].copy())
        xs = np.array(xs)
        # manually propgate information
        xs_ = np.ones_like(xs)
        xs_[:, :3] += np.cumsum(xs_[:, 3], axis=0)[:, np.newaxis]
        for i in reversed(range(n - 2)):
            di = self.sim.connectivity.delays[i, i + 1]
            xs_[(di + 1):, i] = xs_[di, i] + np.cumsum(xs_[:len(xs_) - di - 1, i + 1])
        assert np.allclose(xs_, xs)
