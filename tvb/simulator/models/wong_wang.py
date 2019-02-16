# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)

"""
Models based on Wong-Wang's work.

"""

from .base import ModelNumbaDfun, LOG, numpy, basic, arrays
from numba import guvectorize, float64

@guvectorize([(float64[:],)*11], '(n),(m)' + ',()'*8 + '->(n)', nopython=True)
def _numba_dfun(S, c, a, b, d, g, ts, w, j, io, dx):
    "Gufunc for reduced Wong-Wang model equations."

    if S[0] < 0.0:
        dx[0] = 0.0 - S[0]
    elif S[0] > 1.0:
        dx[0] = 1.0 - S[0]
    else:
        x = w[0]*j[0]*S[0] + io[0] + j[0]*c[0]
        h = (a[0]*x - b[0]) / (1 - numpy.exp(-d[0]*(a[0]*x - b[0])))
        dx[0] = - (S[0] / ts[0]) + (1.0 - S[0]) * h * g[0]


class ReducedWongWang(ModelNumbaDfun):
    r"""
    .. [WW_2006] Kong-Fatt Wong and Xiao-Jing Wang,  *A Recurrent Network
                Mechanism of Time Integration in Perceptual Decisions*.
                Journal of Neuroscience 26(4), 1314-1328, 2006.

    .. [DPA_2013] Deco Gustavo, Ponce Alvarez Adrian, Dante Mantini, Gian Luca
                  Romani, Patric Hagmann and Maurizio Corbetta. *Resting-State
                  Functional Connectivity Emerges from Structurally and
                  Dynamically Shaped Slow Linear Fluctuations*. The Journal of
                  Neuroscience 32(27), 11239-11252, 2013.



    .. automethod:: ReducedWongWang.__init__

    Equations taken from [DPA_2013]_ , page 11242

    .. math::
                 x_k       &=   w\,J_N \, S_k + I_o + J_N \mathbf\Gamma(S_k, S_j, u_{kj}),\\
                 H(x_k)    &=  \dfrac{ax_k - b}{1 - \exp(-d(ax_k -b))},\\
                 \dot{S}_k &= -\dfrac{S_k}{\tau_s} + (1 - S_k) \, H(x_k) \, \gamma

    """
    _ui_name = "Reduced Wong-Wang"
    ui_configurable_parameters = ['a', 'b', 'd', 'gamma', 'tau_s', 'w', 'J_N', 'I_o']

    #Define traited attributes for this model, these represent possible kwargs.
    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([0.270, ]),
        range=basic.Range(lo=0.0, hi=0.270, step=0.01),
        doc="[n/C]. Input gain parameter, chosen to fit numerical solutions.",
        order=1)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([0.108, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="[kHz]. Input shift parameter chosen to fit numerical solutions.",
        order=2)

    d = arrays.FloatArray(
        label=":math:`d`",
        default=numpy.array([154., ]),
        range=basic.Range(lo=0.0, hi=200.0, step=0.01),
        doc="""[ms]. Parameter chosen to fit numerical solutions.""",
        order=3)

    gamma = arrays.FloatArray(
        label=r":math:`\gamma`",
        default=numpy.array([0.641, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Kinetic parameter""",
        order=4)

    tau_s = arrays.FloatArray(
        label=r":math:`\tau_S`",
        default=numpy.array([100., ]),
        range=basic.Range(lo=50.0, hi=150.0, step=1.0),
        doc="""Kinetic parameter. NMDA decay time constant.""",
        order=5)

    w = arrays.FloatArray(
        label=r":math:`w`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Excitatory recurrence""",
        order=6)

    J_N = arrays.FloatArray(
        label=r":math:`J_{N}`",
        default=numpy.array([0.2609, ]),
        range=basic.Range(lo=0.2609, hi=0.5, step=0.001),
        doc="""Excitatory recurrence""",
        order=7)

    I_o = arrays.FloatArray(
        label=":math:`I_{o}`",
        default=numpy.array([0.33, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""[nA] Effective external input""",
        order=8)

    sigma_noise = arrays.FloatArray(
        label=r":math:`\sigma_{noise}`",
        default=numpy.array([0.000000001, ]),
        range=basic.Range(lo=0.0, hi=0.005),
        doc="""[nA] Noise amplitude. Take this value into account for stochatic
        integration schemes.""",
        order=-1)

    state_variable_range = basic.Dict(
        label="State variable ranges [lo, hi]",
        default={"S": numpy.array([0.0, 1.0])},
        doc="Population firing rate",
        order=9
    )

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["S"],
        default=["S"],
        select_multiple=True,
        doc="""default state variables to be monitored""",
        order=10)

    state_variables = ['S']
    _nvar = 1
    cvar = numpy.array([0], dtype=numpy.int32)

    def configure(self):
        """  """
        super(ReducedWongWang, self).configure()
        self.update_derived_parameters()

    def _numpy_dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""
        Equations taken from [DPA_2013]_ , page 11242

        .. math::
                 x_k       &=   w\,J_N \, S_k + I_o + J_N \mathbf\Gamma(S_k, S_j, u_{kj}),\\
                 H(x_k)    &=  \dfrac{ax_k - b}{1 - \exp(-d(ax_k -b))},\\
                 \dot{S}_k &= -\dfrac{S_k}{\tau_s} + (1 - S_k) \, H(x_k) \, \gamma

        """
        S   = state_variables[0, :]
        S[S<0] = 0.
        S[S>1] = 1.
        c_0 = coupling[0, :]


        # if applicable
        lc_0 = local_coupling * S

        x  = self.w * self.J_N * S + self.I_o + self.J_N * c_0 + self.J_N * lc_0
        H = (self.a * x - self.b) / (1 - numpy.exp(-self.d * (self.a * x - self.b)))
        dS = - (S / self.tau_s) + (1 - S) * H * self.gamma

        derivative = numpy.array([dS])
        return derivative

    def dfun(self, x, c, local_coupling=0.0):
        x_ = x.reshape(x.shape[:-1]).T
        c_ = c.reshape(c.shape[:-1]).T + local_coupling * x[0]
        deriv = _numba_dfun(x_, c_, self.a, self.b, self.d, self.gamma,
                        self.tau_s, self.w, self.J_N, self.I_o)
        return deriv.T[..., numpy.newaxis]


class ReducedWongWang_EI(ModelNumbaDfun):
    r"""
       ReducedWongWang_EI is a dynamic mean field model that simulates local regional activity via 
       interconnected populations of excitatory pyramidal (E) and inhibitory (I) neurons, with NMDA (excit-
       atory) and GABA (inhibitory) synaptic receptors (Deco et al., 2014).
       
        Equations taken from [Deco_2014], page 7889:
    
        .. math::
            I_E,i &= W_E * I_0 + w * J_NMDA * S_E,i + J_NMDA * \mathbf\Gamma(S_E,j, c_{ij})
                    - J_i * S_I,i + I_ext \\
            I_I,i &= W_I * I_0 + J_NMDA * S_E,i + \lambda * J_NMDA * \mathbf\Gamma(S_E,j, c_{ij}) 
                    - S_I,i \\
             
            r_E,i &= (a_E * I_E,i - b_E) / (1 - exp(d_E *(a_E * I_E,i - b_E)))
            r_I,i &= (a_I * I_I,i - b_I) / (1 - exp(d_I *(a_I * I_I,i - b_I)))
             
            \dot{S}_E,i &= - S_E,i / \tau_E + (1 - S_E,i) * \gamma * r_E,i
            \dot{S}_I,i &= - S_I,i / \tau_I + r_I,i
             
        See:
        .. [Deco et al., 2014] Deco,G; Ponce-Alvarez, A; Hagmann, P; Romani, GL ; Mantini, D;
            and Corbetta, M. *How Local Excitation–Inhibition Ratio Impacts the Whole Brain Dynamics.*
            J. Neurosci, 2014, 34(23):7886 –7898.
            
        Note: the ReducedWongWang model is a further reduction of the ReducedWongWang_EI.
    
        .. moduleauthor:: courtiol.julie@gmail.com
    """

    _ui_name = "Reduced Wong-Wang_EI"
    ui_configurable_parameters = ['a_E', 'b_E', 'd_E', 'tau_E', 'tau_NMDA', 'W_E', 'w', 'J', 'I_ext',
                                  'gamma', 'a_I', 'b_I', 'd_I', 'tau_I', 'tau_GABA', 'W_I', 'lbda',
                                  'I_0', 'J_NMDA']

    # parameters
    # excitatory gating variables
    a_E = arrays.FloatArray(
        label=":math:`a_E`",
        default=numpy.array([310., ]),
        range=basic.Range(lo=0.0, hi=400.0, step=0.1),
        doc="""Synaptic gating constant. [nC-1]""",
        order=1)

    b_E = arrays.FloatArray(
        label=":math:`b_E`",
        default=numpy.array([125., ]),
        range=basic.Range(lo=0.0, hi=200.0, step=0.1),
        doc="""Synaptic gating constant. [Hz]""",
        order=2)
        
    d_E = arrays.FloatArray(
        label=":math:`d_E`",
        default=numpy.array([.16, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Synaptic gating constant. [s]""",
        order=3)
     
    tau_E = arrays.FloatArray(
        label=":math:`\tau_E`",
        default=numpy.array([100., ]),
        range=basic.Range(lo=50., hi=150., step=1.),
        doc="""Decay times for excitatory population. [ms]""",
        order=4)
       
    tau_NMDA = arrays.FloatArray(
        label=":math:`\tau_NMDA`",
        default=numpy.array([100., ]),
        range=basic.Range(lo=50., hi=150., step=1.),
        doc="""Decay times for NMDA synapses. [ms]""",
        order=5)
   
    W_E = arrays.FloatArray(
        label=":math:`W_E`",
        default=numpy.array([1., ]),
        range=basic.Range(lo=0.1, hi=10., step=0.1),
        doc="""Scaling factor of external input I_0 for the excitatory population.""",
        order=6)

    w = arrays.FloatArray(
        label=r":math:`w`",
        default=numpy.array([1.4, ]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.1),
        doc="""Local excitatory recurrence.""",
        order=7)
        
    J = arrays.FloatArray(
        label=r":math:`J`",
        default=numpy.array([1., ]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.1),
        doc="""Local feedback inhibitory synaptic coupling. [nA]
            By default ; in FIC case it is adjusted independently.""",
        order=8)
        
    I_ext = arrays.FloatArray(
        label=r":math:`I_ext`",
        default=numpy.array([0., ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""External stimulation: I_ext=0 under resting-state condition,
            I_ext=0.02 in task condition.""",
        order=9)
        
    gamma = arrays.FloatArray(
        label=r":math:`\gamma`",
        default=numpy.array([0.000641, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.000001),
        doc="""Kinetic parameter. [ms]""",
        order=10)

    # inhibitory gating variables
    a_I = arrays.FloatArray(
        label=":math:`a_I`",
        default=numpy.array([615., ]),
        range=basic.Range(lo=0.0, hi=700.0, step=0.1),
        doc="""Synaptic gating constant. [nC-1]""",
        order=11)

    b_I = arrays.FloatArray(
        label=":math:`b_I`",
        default=numpy.array([177., ]),
        range=basic.Range(lo=0.0, hi=200.0, step=0.1),
        doc="""Synaptic gating constant. [Hz]""",
        order=12)

    d_I = arrays.FloatArray(
        label=":math:`d_I`",
        default=numpy.array([.087, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.001),
        doc="""Synaptic gating constant. [s]""",
        order=13)

    tau_I = arrays.FloatArray(
        label=":math:`\tau_I`",
        default=numpy.array([10., ]),
        range=basic.Range(lo=1., hi=50., step=1.),
        doc="""Decay times for inhibitory population. [ms]""",
        order=14)

    tau_GABA = arrays.FloatArray(
        label=":math:`\tau_GABA`",
        default=numpy.array([10., ]),
        range=basic.Range(lo=1., hi=50., step=1.),
        doc="""Decay times for GABA synapses. [ms]""",
        order=15)

    W_I = arrays.FloatArray(
        label=":math:`W_I`",
        default=numpy.array([.7, ]),
        range=basic.Range(lo=0.1, hi=10., step=0.1),
        doc="""Scaling factor of external input I_0 for the inhibitory population.""",
        order=16)
        
    lbda = arrays.BoolArray(
        label=r":math:`\lambda`",
        default=numpy.array([0]),
        doc="""When \lambda is True, then long-range feedworward inhibition (FFI)
        is considered. The default value is False, i.e., no FFI.""",
        order=17)
        
    # shared parameters
    I_0 = arrays.FloatArray(
        label=":math:`I_0`",
        default=numpy.array([0.382, ]),
        range=basic.Range(lo=0.001, hi=1., step=0.001),
        doc="""Overall effective external input. [nA]""",
        order=18)

    J_NMDA = arrays.FloatArray(
        label=":math:`J_NMDA`",
        default=numpy.array([0.15, ]),
        range=basic.Range(lo=0.01, hi=1., step=0.01),
        doc="""Excitatory synaptic coupling. [nA]""",
        order=19)

    # initialization
    state_variable_range = basic.Dict(
        label="State variable ranges [lo, hi]",
        default={"S_E": numpy.array([0.0, 1.0]),
                 "S_I": numpy.array([0.0, 1.0])},
        doc="Average excitatory (E) and inhibitory (I) synaptic gating variables.",
        order=20)
        
    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["S_E", "S_I"],
        default=["S_E", "S_I"],
        select_multiple=True,
        doc="""Default state-variables to be monitored.""",
        order=21)
        
    state_variables = ['S_E', 'S_I']
    _nvar = 2                                    #number of state-variables
    cvar = numpy.array([0], dtype=numpy.int32)   #coupling variables

    def _numpy_dfun(self, state_variables, coupling, local_coupling=0.0,
                array=numpy.array, where=numpy.where, concat=numpy.concatenate):
        r"""
            Computes the derivatives of the state-variables of Reduced_WongWang_EI
            with respect to time.
        """

        y = state_variables
        ydot = numpy.empty_like(state_variables)

        # long-range (global) coupling
        lrc = coupling[0]
        
        # short-range (local) coupling
        #src = local_coupling * y[0]

        # local dynamics equations
        # excitatory population
        I_E = self.W_E * self.I_0 + self.w * self.J_NMDA * y[0] + lrc * self.J_NMDA - self.J * y[1] + self.I_ext
        r_E = (self.a_E * I_E - self.b_E) / (1 - numpy.exp(- self.d_E * (self.a_E * I_E - self.b_E)))
        ydot[0] = - y[0] / self.tau_E + (1 - y[0]) * self.gamma * r_E

        # inhibitory population
        I_I = self.W_I * self.I_0 + self.J_NMDA * y[0] - y[1] + lrc * self.lbda * self.J_NMDA
        r_I = (self.a_I * I_I - self.b_I) / (1 - numpy.exp(- self.d_I * (self.a_I * I_I - self.b_I)))
        ydot[1] = - y[1] / self.tau_I + r_I

        return ydot

    def dfun(self, x, c, local_coupling=0.0):

        x_ = x.reshape(x.shape[:-1]).T
        c_ = c.reshape(c.shape[:-1]).T
        #src = local_coupling * x[0, :, 0]
        deriv = _numba_dfun_rwwEI(x_, c_,
                                  self.a_E, self.b_E, self.d_E, self.tau_E, self.tau_NMDA, self.W_E, self.w,
                                  self.J, self.I_ext, self.gamma,
                                  self.a_I, self.b_I, self.d_I, self.tau_I, self.tau_GABA, self.W_I, self.lbda,self.I_0, self.J_NMDA)
        return deriv.T[..., numpy.newaxis]

@guvectorize([(float64[:],) * 22], '(n),(m)' + ',()' *  19 + '->(n)', nopython=True)
def _numba_dfun_rwwEI(y, coupl,
                      a_E, b_E, d_E, tau_E, tau_NMDA, W_E, w, J, I_ext, gamma,
                      a_I, b_I, d_I, tau_I, tau_GABA, W_I, lbda, I_0, J_NMDA,
                      ydot):
    "Gufunc for ReducedWongWang_EI model equations."

    #long-range coupling
    lrc = coupl[0]

    # excitatory population
    I_E = W_E[0] * I_0[0] + w[0] * J_NMDA[0] * y[0] + lrc * J_NMDA[0] - J[0] * y[1] + I_ext[0]
    r_E = (a_E[0] * I_E - b_E[0]) / (1 - numpy.exp(- d_E[0] * (a_E[0] * I_E - b_E[0])))
    ydot[0] = - y[0] / tau_E[0] + (1 - y[0]) * gamma[0] * r_E

    # inhibitory population
    I_I = W_I[0] * I_0[0] + J_NMDA[0] * y[0] - y[1] + lrc * lbda[0] * J_NMDA[0]
    r_I = (a_I[0] * I_I - b_I[0]) / (1 - numpy.exp(- d_I[0] * (a_I[0] * I_I - b_I[0])))
    ydot[1] = - y[1] / tau_I[0] + r_I
