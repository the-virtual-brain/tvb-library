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
#   The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Implementation of differet BOLD signal models. Four different models are distinguished: 

+ CBM_N: Classical BOLD Model Non-linear
+ CBM_L: Classical BOLD Model Linear
+ RBM_N: Revised   BOLD Model Non-linear (default)
+ RBM_L: Revised   BOLD Model Linear

``Classical`` means that the coefficients used to compute the BOLD signal are
derived as described in [Obata2004]_ . ``Revised`` coefficients are defined in
[Stephan2007]_

References:

.. [Stephan2007] Stephan KE, Weiskopf N, Drysdale PM, Robinson PA,
                 Friston KJ (2007) Comparing hemodynamic models with 
                 DCM. NeuroImage 38: 387-401.

.. [Obata2004]  Obata, T.; Liu, T. T.; Miller, K. L.; Luh, W. M.; Wong, E. C.; Frank, L. R. &
                Buxton, R. B. (2004) **Discrepancies between BOLD and flow dynamics in primary and
                supplementary motor areas: application of the balloon model to the
                interpretation of BOLD transients.** Neuroimage, 21:144-153

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

    The haemodynamic model parameters based on constants for a 1.5 T scanner.

        
    """
    
    #NOTE: a potential problem when the input is a TimeSeriesSurface.
    #TODO: add an spatial averaging for TimeSeriesSurface.

    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries that represents the input neural activity""",
        order = 1)
    # it also sets the bold sampling period.
    dt = basic.Float(
        label = ":math:`dt`",
        default = None, 
        required = True,
        doc = """The integration time step size for the balloon model (s)""",
        order = 2)


    integrator = integrators_module.Integrator(
        label = "Integration scheme",
        default = integrators_module.HeunDeterministic,
        required = True,
        order = 3,
        doc = """ A tvb.simulator.Integrator object which is
        an integration scheme with supporting attributes such as 
        integration step size and noise specification for stochastic 
        methods. It is used to compute the time courses of the balloon model state 
        variables.""")
    
    non_linear = basic.Bool(
        label = "Select non_linear or linear BOLD equations",
        default = True,
        required = True,
        doc = """Select the non-linear or linear set of equations for the 
        BOLD model (N or L).""",
        order = 4)

    RBM = basic.Bool(
        label = "Revised BOLD Model",
        default = True,
        required = True,
        doc = """Select classical vs revised BOLD model (CBM or RBM). 
        Coefficients  k1, k2 and k3 will be derived accordingly.""",
        order = 5)

    neural_input_transformation = basic.Dict(
        label="Neural input",
        options=["none", "abs_diff", "sum"],
        default=["none"],
        select_multiple=False,
        doc=""" This represents the operation to perform on the state-variable(s) of
        the model used to generate the input TimeSeries. ``none`` takes the
        first state-variable as neural input; `` abs_diff`` is the absolute
        value of the derivative (first order difference); ``sum``: sum all the
        state-variables in the input TimeSeries.""")

    tau_s = basic.Float(
        label = ":math:`\tau_s`",
        default = 0.65, 
        required = True,
        doc = """Balloon model parameter. Time of signal decay (s)""", 
        order = 6)

    tau_f = basic.Float(
        label = ":math:`\tau_f`",
        default = 0.41, 
        required = True,
        doc = """ Balloon model parameter. Time of flow-dependent elimination or
        feedback regulation (s). The average  time blood take to traverse the
        venous compartment. It is the  ratio of resting blood volume (V0) to
        resting blood flow (F0).""",
        order = 7)

    tau_o = basic.Float(
        label = ":math:`\tau_o`",
        default = 0.98, 
        required = True,
        doc = """
        Balloon model parameter. Haemodynamic transit time (s). The average
        time blood take to traverse the venous compartment. It is the  ratio
        of resting blood volume (V0) to resting blood flow (F0).""",
        order = 8)

    alpha = basic.Float(
        label = ":math:`\tau_f`",
        default = 0.32, 
        required = True,
        doc = """Balloon model parameter. Stiffness parameter. Grubb's exponent.""",
        order = 9)

    TE = basic.Float(
        label = ":math:`TE`",
        default = 0.04, 
        required = True,
        doc = """BOLD parameter. Echo Time""",
        order = 10)

    V0 = basic.Float(
        label = ":math:`V_0`",
        default = 4.0, 
        required = True,
        doc = """BOLD parameter. Resting blood volume fraction.""",
        order = 11)

    E0 = basic.Float(
        label = ":math:`E_0`",
        default = 0.4, 
        required = True,
        doc = """BOLD parameter. Resting oxygen extraction fraction.""",
        order = 12)

    epsilon = arrays.FloatArray(
        label = ":math:`\epsilon`",
        default = numpy.array([0.5]),
        range = basic.Range(lo=0.5, hi=2.0, step=0.25), 
        required = True,
        doc = """ BOLD parameter. Ratio of intra- and extravascular signals. In principle  this
        parameter could be derived from empirical data and spatialized.""",
        order =13)

    nu_0 = basic.Float(
        label = ":math:`\nu_0`",
        default = 40.3 , 
        required = True,
        doc = """BOLD parameter. Frequency offset at the outer surface of magnetized vessels (Hz).""",
        order = 14)

    r_0 = basic.Float(
        label = ":math:`\nu_0`",
        default = 25. , 
        required = True,
        doc = """ BOLD parameter. Slope r0 of intravascular relaxation rate (Hz). Only used for
        ``revised`` coefficients. """,
        order = 15)



    def evaluate(self):
        """
        Calculate simulated BOLD signal
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        ts_shape = self.time_series.data.shape

        #NOTE: Just using the first state variable, although in the Bold monitor
        #      input is the sum over the state-variables. Only time-series
        #      from basic monitors should be used as inputs.

        neural_activity = self.time_series.data[:, 0, :, :]
        neural_activity = neural_activity[:, numpy.newaxis, :, :]

        ts_time  = self.time_series.time 

        if self.dt is None:
            self.dt = self.time_series.sample_period / 1000. # (s) integration time step
            msg = "Integration time step size for the balloon model is %s seconds" % str(dt)
            LOG.info(msg)

        #NOTE: Avoid upsampling ...
        if self.dt < (self.time_series.sample_period / 1000.):
            msg = "Integration time step shouldn't be smaller than the sampling period of the input signal." 
            LOG.error()

        # integration time in (s)
        t_int  = ts_time / 1000. 
        ballon_nvar = 4           

        #NOTE: hard coded initial conditions
        state = numpy.zeros((ts_shape[0], balloon_nvar, ts_shape[2], 1)) #s
        state[0, 1,:] = 1. # f
        state[0, 2,:] = 1. # v
        state[0, 3,:] = 1. # q

        # BOLD model coefficients
        k = self.compute_derived_parameters()
        k1, k2, k3 = k[0], k[1], k[2]

        # prepare integrator
        self.integrator.dt = self.dt
        self.integrator.configure()

        scheme = self.integrator.scheme

        # NOTE: the following variables are not used in this integration but
        # required due to the way integrators scheme has been defined.

        local_coupling = 0.0
        stimulus = 0.0

        # solve equations
        for step in range(1, t_int.shape[0]):
            state[step, :] = scheme(state[step-1, :], self.balloon_dfun, neural_activity[step, :], local_coupling, stimulus)

        # NOTE: just for the sake of clarity, define the variables used in the BOLD model
        s = state[:, 0,:] 
        f = state[:, 1,:] 
        v = state[:, 2,:] 
        q = state[:, 3,:] 

        # BOLD models
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

        ds  = x - (1./self.tau_s) * s - (1./self.tau_f) * (f-1) 
        df  = s
        dv  = (1. / self.tau_o) * (f - v**(1./self.alpha))
        dq  = (1. / self.tau_o) * ((f * (1.-(1. - self.E0)**(1./f)) / self.E0) - (v**(1./self.alpha)) * (q/v))  

        return numpy.array([ds, df, dv, dq])