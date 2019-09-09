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
Wilson-Cowan equations based model definition.
"""

from .base import Model, LOG, numpy, basic, arrays


class WilsonCowan(Model):
    r"""
    **References**:
    .. [WC_1972] Wilson, H.R. and Cowan, J.D. *Excitatory and inhibitory
        interactions in localized populations of model neurons*, Biophysical
        journal, 12: 1-24, 1972.
    .. [WC_1973] Wilson, H.R. and Cowan, J.D  *A Mathematical Theory of the
        Functional Dynamics of Cortical and Thalamic Nervous Tissue*
    .. [D_2011] Daffertshofer, A. and van Wijk, B. *On the influence of
        amplitude on the connectivity between phases*
        Frontiers in Neuroinformatics, July, 2011
    Used Eqns 11 and 12 from [WC_1972]_ in ``dfun``.  P and Q represent external
    inputs, which when exploring the phase portrait of the local model are set
    to constant values. However in the case of a full network, P and Q are the
    entry point to our long range and local couplings, that is, the  activity
    from all other nodes is the external input to the local population.
    The default parameters are taken from figure 4 of [WC_1972]_, pag. 10
    In [WC_1973]_ they present a model of neural tissue on the pial surface is.
    See Fig. 1 in page 58. The following local couplings (lateral interactions)
    occur given a region i and a region j:
      E_i-> E_j
      E_i-> I_j
      I_i-> I_j
      I_i-> E_j
    +---------------------------+
    |          Table 1          |
    +--------------+------------+
    |                           |
    |  SanzLeonetAl,   2014     |
    +--------------+------------+
    |Parameter     |  Value     |
    +==============+============+
    | k_e, k_i     |    1.00    |
    +--------------+------------+
    | r_e, r_i     |    0.00    |
    +--------------+------------+
    | tau_e, tau_i |    10.0    |
    +--------------+------------+
    | c_1          |    10.0    |
    +--------------+------------+
    | c_2          |    6.0     |
    +--------------+------------+
    | c_3          |    1.0     |
    +--------------+------------+
    | c_4          |    1.0     |
    +--------------+------------+
    | a_e, a_i     |    1.0     |
    +--------------+------------+
    | b_e, b_i     |    0.0     |
    +--------------+------------+
    | theta_e      |    2.0     |
    +--------------+------------+
    | theta_i      |    3.5     |
    +--------------+------------+
    | alpha_e      |    1.2     |
    +--------------+------------+
    | alpha_i      |    2.0     |
    +--------------+------------+
    | P            |    0.5     |
    +--------------+------------+
    | Q            |    0       |
    +--------------+------------+
    | c_e, c_i     |    1.0     |
    +--------------+------------+
    | alpha_e      |    1.2     |
    +--------------+------------+
    | alpha_i      |    2.0     |
    +--------------+------------+
    |                           |
    |  frequency peak at 20  Hz |
    |                           |
    +---------------------------+
    The parameters in Table 1 reproduce Figure A1 in  [D_2011]_
    but set the limit cycle frequency to a sensible value (eg, 20Hz).
    Model bifurcation parameters:
        * :math:`c_1`
        * :math:`P`
    The models (:math:`E`, :math:`I`) phase-plane, including a representation of
    the vector field as well as its nullclines, using default parameters, can be
    seen below:
        .. _phase-plane-WC:
        .. figure :: img/WilsonCowan_01_mode_0_pplane.svg
            :alt: Wilson-Cowan phase plane (E, I)
            The (:math:`E`, :math:`I`) phase-plane for the Wilson-Cowan model.
    .. automethod:: WilsonCowan.__init__
    The general formulation for the \textit{\textbf{Wilson-Cowan}} model as a
    dynamical unit at a node $k$ in a BNM with $l$ nodes reads:
    .. math::
            \dot{E}_k &= \dfrac{1}{\tau_e} (-E_k  + (k_e - r_e E_k) \mathcal{S}_e (\alpha_e \left( c_{ee} E_k - c_{ei} I_k  + P_k - \theta_e + \mathbf{\Gamma}(E_k, E_j, u_{kj}) + W_{\zeta}\cdot E_j + W_{\zeta}\cdot I_j\right) ))\\
            \dot{I}_k &= \dfrac{1}{\tau_i} (-I_k  + (k_i - r_i I_k) \mathcal{S}_i (\alpha_i \left( c_{ie} E_k - c_{ee} I_k  + Q_k - \theta_i + \mathbf{\Gamma}(E_k, E_j, u_{kj}) + W_{\zeta}\cdot E_j + W_{\zeta}\cdot I_j\right) ))
    """
    _ui_name = "Wilson-Cowan"
    ui_configurable_parameters = ['c_ee', 'c_ei', 'c_ie', 'c_ii', 'tau_e', 'tau_i',
                                  'a_e', 'b_e', 'c_e', 'a_i', 'b_i', 'c_i', 'r_e',
                                  'r_i', 'k_e', 'k_i', 'P', 'Q', 'theta_e', 'theta_i',
                                  'alpha_e', 'alpha_i']

    # Define traited attributes for this model, these represent possible kwargs.
    c_ee = arrays.FloatArray(
        label=":math:`c_{ee}`",
        default=numpy.array([12.0]),
        range=basic.Range(lo=11.0, hi=16.0, step=0.01),
        doc="""Excitatory to excitatory  coupling coefficient""",
        order=1)

    c_ie = arrays.FloatArray(
        label=":math:`c_{ei}`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=15.0, step=0.01),
        doc="""Inhibitory to excitatory coupling coefficient""",
        order=2)

    c_ei = arrays.FloatArray(
        label=":math:`c_{ie}`",
        default=numpy.array([13.0]),
        range=basic.Range(lo=2.0, hi=22.0, step=0.01),
        doc="""Excitatory to inhibitory coupling coefficient.""",
        order=3)

    c_ii = arrays.FloatArray(
        label=":math:`c_{ii}`",
        default=numpy.array([11.0]),
        range=basic.Range(lo=2.0, hi=15.0, step=0.01),
        doc="""Inhibitory to inhibitory coupling coefficient.""",
        order=4)

    tau_e = arrays.FloatArray(
        label=r":math:`\tau_e`",
        default=numpy.array([10.0]),
        range=basic.Range(lo=0.0, hi=150.0, step=0.01),
        doc="""Excitatory population, membrane time-constant [ms]""",
        order=5)

    tau_i = arrays.FloatArray(
        label=r":math:`\tau_i`",
        default=numpy.array([10.0]),
        range=basic.Range(lo=0.0, hi=150.0, step=0.01),
        doc="""Inhibitory population, membrane time-constant [ms]""",
        order=6)

    a_e = arrays.FloatArray(
        label=":math:`a_e`",
        default=numpy.array([1.2]),
        range=basic.Range(lo=0.0, hi=1.4, step=0.01),
        doc="""The slope parameter for the excitatory response function""",
        order=7)

    b_e = arrays.FloatArray(
        label=":math:`b_e`",
        default=numpy.array([2.8]),
        range=basic.Range(lo=1.4, hi=6.0, step=0.01),
        doc="""Position of the maximum slope of the excitatory sigmoid function""",
        order=8)

    c_e = arrays.FloatArray(
        label=":math:`c_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=1.0, hi=20.0, step=1.0),
        doc="""The amplitude parameter for the excitatory response function""",
        order=9)

    theta_e = arrays.FloatArray(
        label=r":math:`\theta_e`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=60., step=0.01),
        doc="""Excitatory threshold""",
        order=10)

    a_i = arrays.FloatArray(
        label=":math:`a_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""The slope parameter for the inhibitory response function""",
        order=11)

    b_i = arrays.FloatArray(
        label=r":math:`b_i`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=6.0, step=0.01),
        doc="""Position of the maximum slope of a sigmoid function [in
        threshold units]""",
        order=12)

    theta_i = arrays.FloatArray(
        label=r":math:`\theta_i`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=60.0, step=0.01),
        doc="""Inhibitory threshold""",
        order=13)

    c_i = arrays.FloatArray(
        label=":math:`c_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=1.0, hi=20.0, step=1.0),
        doc="""The amplitude parameter for the inhibitory response function""",
        order=14)

    r_e = arrays.FloatArray(
        label=":math:`r_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Excitatory refractory period""",
        order=15)

    r_i = arrays.FloatArray(
        label=":math:`r_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Inhibitory refractory period""",
        order=16)

    k_e = arrays.FloatArray(
        label=":math:`k_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Maximum value of the excitatory response function""",
        order=17)

    k_i = arrays.FloatArray(
        label=":math:`k_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""Maximum value of the inhibitory response function""",
        order=18)

    P = arrays.FloatArray(
        label=":math:`P`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the excitatory population.
        Constant intensity.Entry point for coupling.""",
        order=19)

    Q = arrays.FloatArray(
        label=":math:`Q`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the inhibitory population.
        Constant intensity.Entry point for coupling.""",
        order=20)

    alpha_e = arrays.FloatArray(
        label=r":math:`\alpha_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the excitatory population.
        Constant intensity.Entry point for coupling.""",
        order=21)

    alpha_i = arrays.FloatArray(
        label=r":math:`\alpha_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the inhibitory population.
        Constant intensity.Entry point for coupling.""",
        order=22)

    # Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"E": numpy.array([0.0, 1.0]),
                 "I": numpy.array([0.0, 1.0])},
        doc="""The values for each state-variable should be set to encompass
        the expected dynamic range of that state-variable for the current
        parameters, it is used as a mechanism for bounding random inital
        conditions when the simulation isn't started from an explicit history,
        it is also provides the default range of phase-plane plots.""",
        order=23)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["E", "I", "E + I", "E - I"],
        default=["E"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
               monitored. It can be overridden for each Monitor if desired. The
               corresponding state-variable indices for this model are :math:`E = 0`
               and :math:`I = 1`.""",
        order=24)

    state_variables = 'E I'.split()
    _nvar = 2
    cvar = numpy.array([0, 1], dtype=numpy.int32)

    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""
       .. math::
            \dot{E}_k &= \dfrac{1}{\tau_e} (-E_k  + (k_e - r_e E_k) \mathcal{S}_e (\alpha_e \left( c_{ee} E_k - c_{ei} I_k  + P_k - \theta_e + \mathbf{\Gamma}(E_k, E_j, u_{kj}) + W_{\zeta}\cdot E_j + W_{\zeta}\cdot I_j\right) ))\\
            \dot{I}_k &= \dfrac{1}{\tau_i} (-I_k  + (k_i - r_i I_k) \mathcal{S}_i (\alpha_i \left( c_{ie} E_k - c_{ee} I_k  + Q_k - \theta_i + \mathbf{\Gamma}(E_k, E_j, u_{kj}) + W_{\zeta}\cdot E_j + W_{\zeta}\cdot I_j\right) ))
        """

        E = state_variables[0, :]
        I = state_variables[1, :]
        derivative = numpy.empty_like(state_variables)

        # long-range coupling
        c_0 = coupling[0, :]

        # short-range (local) coupling
        lc_0 = local_coupling * E
        lc_1 = local_coupling * I

        x_e = self.alpha_e * (self.c_ee * E - self.c_ei * I + self.P  - self.theta_e +  c_0 + lc_0 + lc_1)
        x_i = self.alpha_i * (self.c_ie * E - self.c_ii * I + self.Q  - self.theta_i + lc_0 + lc_1)

        s_e = self.c_e / (1.0 + numpy.exp(-self.a_e * (x_e - self.b_e)))
        s_i = self.c_i / (1.0 + numpy.exp(-self.a_i * (x_i - self.b_i)))

        derivative[0] = (-E + (self.k_e - self.r_e * E) * s_e) / self.tau_e
        derivative[1] = (-I + (self.k_i - self.r_i * I) * s_i) / self.tau_i

        return derivative