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
Implementation of differet BOLD signal models as described in [Stephan2007]_

Four different models are distinguishe: 

+ CBM_N: Classical BOLD Model Non-linear
+ CBM_L: Classical BOLD Model Linear
+ RBM_N: Revised   BOLD Model Non-linear (default)
+ RBM_L: Revised   BOLD Model Linear

Classical mean that the coefficients used to compute the BOLD signal are
derived as described in [Buxton1998]_ and [Friston2000]_


.. [Stephan2007] Stephan KE, Weiskopf N, Drysdale PM, Robinson PA,
                 Friston KJ (2007) Comparing hemodynamic models with 
                 DCM. NeuroImage 38: 387-401.


.. [Buxton1998]  DOC ME
.. [Friston2000] DOC ME
.. [Buxton2004]  DOC ME
.. [Obata2004]   DOC ME

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import numpy
import tvb.datatypes.time_series as time_series
import tvb.datatypes.arrays as arrays
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.util as util
import tvb.simulator.integrators as integrators_module
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class BalloonModel(core.Type):
    """

    A class for calculating the simulated BOLD signal given a TimeSeries
    object of TVB and returning another TimeSeries object.

    NOTE: a potential problem when the input is a TimeSeriesSurface.
    TODO: add an spatial averaging for TimeSeriesSurface.

    The haemodynamic model parameters based on constants for a 1.5 T scanner.

        
    """
    
    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries that represents the input neural activity""")
     
    dt = basic.Float(
        label = ":math:`dt`",
        default = 0.001, 
        required = True,
        doc = """The integration time step size for the BOLD model (s)""")
    
    non_linear = basic.Bool(
        label = "Select non_linear or linear BOLD equations",
        default = True,
        required = True,
        doc = """Select the non-linear or linear set of equations for the 
        BOLD model (N or L).""")

    RBM = basic.Bool(
        label = "Revised BOLD Model",
        default = True,
        required = True,
        doc = """Select classical vs revised BOLD model (CBM or RBM). 
        Coefficients  k1, k2 and k3 will be derived accordingly.""")

    tau_s = basic.Float(
        label = ":math:`\tau_s`",
        default = 0.65, 
        required = True,
        doc = """Time of signal decay (s)""")

    tau_f = basic.Float(
        label = ":math:`\tau_f`",
        default = 0.41, 
        required = True,
        doc = """Time of flow-dependent elimination or feedback regulation (s). The average 
        time blood take to traverse the venous compartment. It is the 
        ratio of resting blood volume (V0) to resting blood flow (F0).""")

    tau_o = basic.Float(
        label = ":math:`\tau_o`",
        default = 0.98, 
        required = True,
        doc = """Haemodynamic transit time (s). The average 
        time blood take to traverse the venous compartment. It is the 
        ratio of resting blood volume (V0) to resting blood flow (F0).""")

    alpha = basic.Float(
        label = ":math:`\tau_f`",
        default = 0.32, 
        required = True,
        doc = """Stiffness parameter. Grubb's exponent.""")


    TE = basic.Float(
        label = ":math:`TE`",
        default = 0.04, 
        required = True,
        doc = """Echo Time""")


    V0 = basic.Float(
        label = ":math:`V_0`",
        default = 4.0, 
        required = True,
        doc = """Resting blood volume fraction.""")

    E0 = basic.Float(
        label = ":math:`E_0`",
        default = 0.4, 
        required = True,
        doc = """Resting oxygen extraction fraction.""")

    epsilon = arrays.FloatArray(
        label = ":math:`\epsilon`",
        default = numpy.array([0.5]),
        range = basic.Range(lo=0.5, hi=2.0, step=0.25), 
        required = True,
        doc = """Resting oxygen extraction fraction. In principle 
        this parameter can be derived from empirical data 
        and spatialized.""")


    nu_0 = basic.Float(
        label = ":math:`\nu_0`",
        default = 40.3 , 
        required = True,
        doc = """Frequency offset at the outer surface of magnetized vessels (Hz).""")


    r_0 = basic.Float(
        label = ":math:`\nu_0`",
        default = 25. , 
        required = True,
        doc = """Slope r0 of intravascular relaxation rate (Hz).""")


    integrator = integrators_module.Integrator(
        label = "Integration scheme",
        default = integrators_module.HeunDeterministic,
        required = True,
        order = 6,
        doc = """A tvb.simulator.Integrator object which is
            an integration scheme with supporting attributes such as 
            integration step size and noise specification for stochastic 
            methods. It is used to compute the time courses of the model state 
            variables.""")



    def evaluate(self):
        """
        Calculate simulated BOLD signal
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        ts_shape = self.time_series.data.shape

        # for the time being just testing with the first state variable
        # TODO: check how many sv time_series dtype has

        neural_activity = self.time_series.data[:, 0, :, :]
        neural_activity = neural_activity[:, numpy.newaxis, :, :]

        ts_time  = self.time_series.time 
        dt       = self.time_series.sample_period / 1000.#self.dt                 # (s) integration time step

        if dt < (self.time_series.sample_period / 1000.):
            msg = "Integration time step shouldn't be smaller than the sampling period of the input signal." 
            LOG.error()

        # integration time
        t_int  = ts_time[:-1] / 1000.            # (s)

        state = numpy.zeros((ts_shape[0]-1, 4, ts_shape[2], 1))
        state[0, 1,:] = 1. # f
        state[0, 2,:] = 1. # v
        state[0, 3,:] = 1. # q

        k = self.compute_derived_parameters()
        k1, k2, k3 = k[0], k[1], k[2]

        self.integrator.dt = dt
        self.integrator.configure()

        scheme = self.integrator.scheme
        local_coupling = 0.0
        stimulus = 0.0

        for step in range(1, t_int.shape[0]):
            state[step, :] = scheme(state[step-1, :], self.balloon_dfun, neural_activity[step, :], local_coupling, stimulus)

        # NOTE: just for the sake of clarity, define the variables used in the BOLD model
        s = state[:, 0,:] 
        f = state[:, 1,:] 
        v = state[:, 2,:] 
        q = state[:, 3,:] 

        if self.non_linear:
            """
            Non-linear BOLD model equations.
            Page 391. Eq. (13) top in [Stephan2007]_ 
            """
            y_bold = self.V0*(k1*(1.-q) + k2*(1. - q/v) + k3 * (1.-v))

        else:
            """
            Linear BOLD model equations.
            Page 391. Eq. (13) bottom in [Stephan2007]_ 
            """
            y_bold = self.V0 * ((k1 + k2)*(1.-q) + (k3 - k2)*(1.-v))

        sample_period = 1./dt

        
        bold_signal = time_series.TimeSeries(
            data = y_bold,
            time = t_int,
            sample_period = sample_period,
            sample_period_unit = 's',
            use_storage = False)

        
        return bold_signal


    def compute_derived_parameters(self):
        """
        Compute derived parameters :math:`k_1`, :math:`k_2` and :math:`k_3`.
        """

        if not self.RBM:
            """
            Classical BOLD Model Coefficients [Obata2004]_
            Page 389 in [Stephan2007]_, Eq. (3)
            """
            k1 = 7. * self.E0
            k2 = 2. * self.E0
            k3 = 1. - self.epsilon
        else:
            """
            Revised BOLD Model Coefficients.
            Generalized BOLD signal model.
            Page 400 in [Stephan2007]_, Eq. (12)
            """
            k1  = 4.3 * self.nu_0 * self.E0 * self.TE
            k2  = self.epsilon * self.r_0 * self.E0 * self.TE
            k3  = 1 - self.epsilon

        return numpy.array([k1, k2, k3])

    def balloon_dfun(self, state_variables, neural_input, local_coupling=0.0):
        r"""
        The Balloon model equations. See Eqs. (4-10) in [Stephan2007]_
        .. math::
                \frac{ds}{dt} &= x - \kappa\,s - \gamma \,(f-1) \\
                \frac{df}{dt} &= s \\
                \frac{dv}{dt} &= \frac{1}{\tau_o} \, (f - v^{1/\alpha})\\
                \frac{dq}{dt} &= \frac{1}{\tau_o}(f \, \frac{1-(1-E_0)^{1/\alpha}}{E_0} - v^{&/\alpha} \frac{q}{v})\\
                \kappa &= \frac{1}{\tau_s}\\
                \gamma &= \frac{1}{\tau_f}
        """

        s  = state_variables[0, :]
        f  = state_variables[1, :]
        v  = state_variables[2, :]
        q  = state_variables[3, :]

        x = neural_input[0,:]

        ds  = x - (1./self.tau_s) * s - (1./self.tau_f) * (f - 1 ) 
        df  = s
        dv  = (1. / self.tau_o) * (f - v**(1./self.alpha))
        dq  = (1. / self.tau_o) * ((f * (1.-(1. - self.E0)**(1./f)) / self.E0) - (v**(1./self.alpha)) * (q/v))  

        return numpy.array([ds, df, dv, dq])



