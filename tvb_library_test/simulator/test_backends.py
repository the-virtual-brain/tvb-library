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
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
This module attempts to test that the various backends produce reasonable
simulation data & agree with each other.


.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import ctypes

from numpy import *

from tvb.simulator.lab import *
from tvb.simulator.backend import genc, ccpp, cuda

# note, this is a private dataset not available with TVB.
# it will need to be replaced with something suitable.
from data.dsi import load_dataset


class Sim(object):

    tf = 2**10
    dt = 2**-4 # 0.0625
    ds = 1
    ts = r_[0:tf:dt]

    vel = 2**2.
    gsc = -2**-9
    exc = 2**0.

    dataset_idx = 0

    nsv = 2

    def __init__(self):
        self.dataset = load_dataset(self.dataset_idx)
        self.n = self.dataset.weights.shape[0]

    def __iter__(self):
        self.i = 0
        self.t = self.ts[self.i]
        return self

    def next(self):
        self.i += 1
        self.t += self.dt
        return self.t


class CeeSim(Sim):


    def __init__(self, ic=None):
        super(CeeSim, self).__init__()

        C = ascontiguousarray

        idel = (self.dataset.distances/self.vel/self.dt).astype(int64)
        self.idel = C(idel)
        self.horizon = self.idel.max() + 1
        self.conn = C(self.dataset.weights)
        self.gsc = C(array([self.gsc]))/self.n
        self.exc = C(array([self.exc]))
        self.hist = C(zeros((self.horizon, self.n)) + 0.1)
        self.state = C(ic or 0.1*ones((self.n, 2)))

        src = genc.module(genc.model(dt=self.dt, **genc.fhn), 
                          genc.step (self.n, len(genc.fhn['eqns']), 
                                     model=genc.fhn['name']),
                          genc.wrap (self.horizon))

        self.mod = ccpp.srcmod(src, ['step'], debug=False)
                         

        for arr_name in ['idel', 'conn', 'hist', 'state', 'gsc', 'exc']:
            arr = getattr(self, arr_name)
            ptr = arr.ctypes.data_as(ctypes.c_void_p)
            setattr(self, 'p_%s' % (arr_name,), ptr)

    @timed
    def next(self):
        super(CeeSim, self).next()
        self.mod.step(self.i, self.p_idel, self.p_hist, self.p_conn, 
                      self.p_state, self.p_gsc, self.p_exc)
        return self.t, self.state.copy()


class CudaSim(Sim):

    nic = 32

    def __init__(self, ic=None, nthr=256):
        super(CudaSim, self).__init__()

        # def gpu(gsc, exc, vel
        # cat=concatenate):

        self.nthr    = nthr
        self.idel    = (self.dataset.distances/self.vel/self.dt).astype(int32)
        self.horizon = self.idel.max() + 1
        self.hist    = zeros((self.horizon, self.n, self.nthr)) + 0.1
        self.conn    = self.dataset.weights
        self.state   = ic or 0.1*ones((self.n, self.nsv, self.nthr))

        self.exc     = self.exc*ones((self.nthr,))
        self.gsc     = self.gsc*ones((self.nthr,))/self.n

        genc.RPointer.gpu = True
        src = genc.module(
                genc.model(dt=self.dt, 
                           noise=False, 
                           gpu=True,
                           **genc.fhn),
                genc.step (self.n,
                           len(genc.fhn['eqns']),
                           model=genc.fhn['name'], 
                           noise=False, gpu=True),
                genc.wrap (self.horizon, gpu=True),
                gpu=True)
        self.mod = cuda.srcmod(src, ['step'], debug=False)

    gpuarray_opts = {'_timed': False, '_memdebug': False}

    def __iter__(self):
        self.gpuarrays = cuda.arrays_on_gpu(
            idel =self.idel.astype(int32), 
            hist =self.hist.astype(float32),
            conn =self.conn.astype(float32), 
            state=self.state.astype(float32),
            exc  =self.exc.astype(float32), 
            gsc  =self.gsc.astype(float32),
            **self.gpuarray_opts)

        self.gpuarrays.__enter__()

        return super(CudaSim, self).__iter__()

    def __del__(self):
        if hasattr(self, 'gpuarrays'):
            self.gpuarrays.__exit__()

    @timed
    def next(self):
        super(CudaSim, self).next()

        g = self.gpuarrays

        self.mod.step(int32(self.i), 
                      g.idel, g.hist, g.conn, g.state, g.gsc, g.exc,
                      block=(self.nthr, 1, 1), grid=(1, 1))

        # maybe separate again for perf & to be sure no thread mixing...
        """
        mod.update(int32(step), g.hist, g.X, 
                   block=(ublock if nthr>=ublock else nthr, 1, 1), 
                   grid=(nthr/ublock if nthr/ublock > 0 else 1, 1))
        """
        return self.t, g.state.get()


class NpSim(Sim):

    def __init__(self, ic=None):
        super(NpSim, self).__init__()

        self.idel = (self.dataset.distances/self.vel/self.dt).astype(int64)
        self.horizon = self.idel.max() + 1
        self.history = zeros((self.horizon, self.n), dtype=float64) + 0.1
        self.state = ic or 0.1*ones((self.n, 2))
        self.gsc = self.n # no divide because we take mean below!

        
    @timed
    def next(self, dot=dot, take=take, array=array):
        super(NpSim, self).next()

        x, y = self.state.T
        old_idx = self.n*((self.i - 1 - self.idel) % self.horizon)
        old_state = take(self.history, old_idx + r_[:self.n])
        coupling = self.gsc*dot(self.dataset.weights, old_state).mean(axis=1)
        dstate = array([(x - x*x*x/3.0 + y)*3./5., 
                        (self.exc - x  )/3./5. + coupling]).T
        self.state += self.dt*(dstate)# + randn(n, 2)/20.0)

        now_idx = self.n*(self.i % self.horizon) + r_[:self.n]
        self.history.flat[now_idx] = self.state[:, 0]

        return self.t, self.state.copy()


if __name__ == '__main__':

    Sim.exc = 0.85

    npy = NpSim()
    cee = CeeSim()
    gpu = CudaSim()

    # sanity 
    assert allclose(npy.state, cee.state)
    assert npy.horizon == cee.horizon
    assert allclose(npy.idel, cee.idel)
    assert allclose(npy.state, gpu.state[...,0])
    assert npy.horizon == gpu.horizon
    assert allclose(npy.idel, gpu.idel)

    old = (npy.state.copy(), cee.state.copy(), gpu.state[..., 0].copy())

    # unit test for generated wrap function
    for i in r_[-10*npy.horizon:20*npy.horizon]:
        try:
            assert cee.mod._module.wrap(ctypes.c_int(i)) == i%npy.horizon
        except:
            msg = 'wrap missed corner case: %d -> %d, should be %d'
            msg %= i, cee.mod._module.wrap(ctypes.c_int(i)), i%npy.horizon 
            raise ValueError(msg)

    ys = []

    for i, npy_step, cee_step, gpu_step in zip(range(Sim.ts.shape[0]),
                                               npy, cee, gpu):

        npy_t, npy_x = npy_step
        cee_t, cee_x = cee_step
        gpu_t, gpu_x = gpu_step

        assert (diff(gpu_x, axis=2)**2).sum() == 0.0
        gpu_x = gpu_x[..., 0]


        assert npy_t == cee_t
        assert npy_t == gpu_t

        dnpy, dcee, dgpu = (npy_x - old[0], cee_x - old[1], gpu_x - old[2])

        if i % 10 == 0:
            print (i, ((dnpy - dcee)**2).mean(), ((npy_x - cee_x)**2).mean(),
                      ((dnpy - dgpu)**2).mean(), ((npy_x - gpu_x)**2).mean())

            ys.append(array([
                npy_x[0, 0],
                cee_x[0, 0],
                gpu_x[0, 0]
            ]))

        old = (npy_x, cee_x, gpu_x)

        if i < 400:

            # compare numpy & cee
            try:
                assert ((dnpy - dcee)**2).mean() < 1e-7
                assert ((npy_x - cee_x)**2).mean() < 1e-3
            except AssertionError:
                msg = 'diff avg err: %g, abs avg err: %g'
                msg %= ((dnpy - dcee)**2).mean(), ((npy_x - cee_x)**2).mean()
                raise AssertionError(msg)

            # compare numpy & gpu
            try:
                assert ((dnpy - dgpu)**2).mean() < 1e-6
                assert ((npy_x - gpu_x)**2).mean() < 1e-3
            except AssertionError:
                msg = 'diff avg err: %g, abs avg err: %g'
                msg %= ((dnpy - dgpu)**2).mean(), ((npy_x - gpu_x)**2).mean()
                raise AssertionError(msg)

    print 'npy -> %0.3f Hz' % (1/array(npy.next.times).mean(),)
    print 'cee -> %0.3f Hz' % (1/array(cee.next.times).mean(),)
    print 'gpu -> %0.3f Hz' % (1/array(gpu.next.times).mean(),)

    ys = array(ys)
