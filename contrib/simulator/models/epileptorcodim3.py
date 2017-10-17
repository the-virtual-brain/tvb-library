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
Saggio codimension 3 Epileptor model

.. moduleauthor:: Marisa Luisa Saggio
.. moduleauthor:: Len Spek

"""

# Third party python libraries
import numpy

# The Virtual Brain
try:
    from tvb.basic.logger.builder import get_logger

    LOG = get_logger(__name__)
except ImportError:
    import logging

    LOG = logging.getLogger(__name__)

# import datatypes and traited datatypes
from tvb.datatypes.arrays import FloatArray, IntegerArray
from tvb.basic.traits.types_basic import Range, Dict, Enumerate
import tvb.simulator.models as models


class EpileptorCodim3(models.Model):
    """
    .. [Saggioetal_2017] Saggio ML, Spiegler A, Bernard C, Jirsa VK. *Fast–Slow Bursters in the Unfolding of a
        High Codimension Singularity and the Ultra-slow Transitions of Classes.*
        Journal of Mathematical Neuroscience. 2017;7:7. doi:10.1186/s13408-017-0050-8.

    .. The Epileptor codim 3 model is a neural mass model which contains two subsystems acting at different timescales.
        For the fast subsystem we use the unfolding of a degenerate Takens-Bogdanov bifucation of codimension 3.
        The slow subsystem steers the fast one back and forth along these paths leading to bursting behavior.
        The model is able to produce almost all the classes of bursting predicted for systems
        with a planar fast subsystem.

        In this implementation the model can produce Hysteresis-Loop Bursters of classes c0, c0', c2s, c3s, c4s, c10s,
        c11s, c2b, c4b, c8b, c14b and c16b as classified by [Saggioetal_2017] Table 2. The default model parameters
        correspond to class c2s.

    .. automethod:: EpileptorCodim3.__init__

    """

    _ui_name = "Epileptor codim 3"
    ui_configurable_parameters = ['mu1_start', 'mu2_start', 'nu_start', 'mu1_stop', 'mu2_stop', 'nu_stop', 'b', 'R',
                                  'c',
                                  'dstar', 'N']

    # Define traited attributes for this model, these represent possible kwargs.
    mu1_start = FloatArray(
        label="mu1_start",
        default=numpy.array([-0.02285]),
        doc="The bifurcation mu1 at the initial point for the given class, default for class c2s "
            "(Saddle-Node at onset and Saddle-Homoclinic at offset)",
        order=1)

    mu2_start = FloatArray(
        label="mu2_start",
        default=numpy.array([0.3448]),
        doc="The bifurcation mu2 at the initial point for the given class, default for class c2s "
            "(Saddle-Node at onset and Saddle-Homoclinic at offset)",
        order=2)

    nu_start = FloatArray(
        label="nu_start",
        default=numpy.array([0.2014]),
        doc="The bifurcation nu at the initial point for the given class, default for class c2s "
            "(Saddle-Node at onset and Saddle-Homoclinic at offset)",
        order=3)

    mu1_stop = FloatArray(
        label="mu1_stop",
        default=numpy.array([-0.07465]),
        doc="The bifurcation mu1 at the final point for the given class, default for class c2s "
            "(Saddle-Node at onset and Saddle-Homoclinic at offset)",
        order=4)

    mu2_stop = FloatArray(
        label="mu2_stop",
        default=numpy.array([0.3351]),
        doc="The bifurcation mu2 at the final point for the given class, default for class c2s "
            "(Saddle-Node at onset and Saddle-Homoclinic at offset)",
        order=5)

    nu_stop = FloatArray(
        label="nu_stop",
        default=numpy.array([0.2053]),
        doc="The bifurcation nu at the final point for the given class, default for class c2s "
            "(Saddle-Node at onset and Saddle-Homoclinic at offset)",
        order=6)

    b = FloatArray(
        label="b",
        default=numpy.array([1.0]),
        doc="Unfolding type of the degenerate Takens-Bogdanov bifurcation, default is a focus type",
        order=7)

    R = FloatArray(
        label="R",
        default=numpy.array([0.4]),
        doc="Radius in unfolding",
        order=8)

    c = FloatArray(
        label="c",
        default=numpy.array([0.001]),
        doc="Speed of the slow variable",
        order=9)

    dstar = FloatArray(
        label="dstar",
        default=numpy.array([0.3]),
        doc="Threshold for the inversion of the slow variable",
        order=10)

    N = IntegerArray(
        label="N",
        default=numpy.array([1]),
        doc="The branch of the resting state, default is 1",
        order=11)

    state_variable_range = Dict(
        label="State variable ranges [lo, hi]",
        default={"x": numpy.array([0.4, 0.6]),
                 "y": numpy.array([-0.1, 0.1]),
                 "z": numpy.array([0.01, 0.1])},
        doc="Typical bounds on state variables .",
        order=16
    )

    variables_of_interest = Enumerate(
        label="Variables watched by Monitors",
        options=['x', 'y', 'z', 'y - x'],
        default=['x', 'z'],
        select_multiple=True,
        doc="Quantities available to monitor.",
        order=100
    )

    def __init__(self, **kwargs):
        """
        Initialise parameters

        """

        super(EpileptorCodim3, self).__init__(**kwargs)

        # state variables names
        self.state_variables = ['x', 'y', 'z']

        # number of state variables
        self._nvar = 3
        self.cvar = numpy.array([0], dtype=numpy.int32)

        # the variable of interest
        self.voi = numpy.array([0], dtype=numpy.int32)

        # If there are derived parameters from the predefined parameters, then initialize them to None
        self.E = None
        self.F = None
        self.xs = None
        self.mu1 = None
        self.mu2 = None
        self.nu = None

    def dfun(self, state_variables, coupling, local_coupling=0.0):
        """
        The equations were taken from [Saggioetal_2017]
        cf. Eqns. (4) and (7), page 17

        The state variables x and y correspond to the fast subsystem
            and the state variable z corresponds to the slow subsystem.

            .. math::
                \\dot{x} &= -y
                \\dot{y} &= x^3 - \mu_2 x - \mu_1 - y(\nu + b x + x^2)
                \\dot{z} &= -c(\sqrt{(x-x_s}^2+y^2} - d^*)

        Where \mu_1, \mu_2 and \nu lie on a great arc of a sphere of radius R parametrised by the unit vectors E and F.

            .. math::
                \begin{pmatrix}\mu_2 & -\mu_1 & \nu \end{pmatrix} &= R(E \cos z + F \sin z)

        And where x_s is the x-coördinate of the resting state (stable equilibrium).
            This is computed by finding the solution of
            .. math::
                x_s^3 - mu2*x_s - mu1 = 0

             And taking the branch which corresponds to the resting state.
             If x_s is complex, we take the real part.

        """
        x = state_variables[0, :]
        y = state_variables[1, :]
        z = state_variables[2, :]

        # Computes the values of mu2,mu1 and nu given the great arc (E,F,R) and the value of the slow variable z
        self.mu2 = self.R * (self.E[0] * numpy.cos(z) + self.F[0] * numpy.sin(z))
        self.mu1 = -self.R * (self.E[1] * numpy.cos(z) + self.F[1] * numpy.sin(z))
        self.nu = self.R * (self.E[2] * numpy.cos(z) + self.F[2] * numpy.sin(z))

        # Computes x_s, which is the solution to x_s^3 - mu2*x_s - mu1 = 0
        if self.N == 1:
            self.xs = (self.mu1 / 2.0 + numpy.sqrt(self.mu1 ** 2 / 4.0 - self.mu2 ** 3 / 27.0 + 0 * 1j)) ** (
                1.0 / 3.0) + (self.mu1 / 2.0 - numpy.sqrt(self.mu1 ** 2 / 4.0 - self.mu2 ** 3 / 27.0 + 0 * 1j)) ** (
                1.0 / 3.0)
        elif self.N == 2:
            self.xs = -1.0 / 2.0 * (1.0 - 1j * 3 ** (1.0 / 2.0)) * (self.mu1 / 2.0 + numpy.sqrt(
                self.mu1 ** 2 / 4.0 - self.mu2 ** 3 / 27.0 + 0 * 1j)) ** (1.0 / 3.0) - 1.0 / 2.0 * (
                1.0 + 1j * 3 ** (1.0 / 2.0)) * (self.mu1 / 2.0 - numpy.sqrt(
                self.mu1 ** 2 / 4.0 - self.mu2 ** 3 / 27.0 + 0 * 1j)) ** (1.0 / 3.0)
        elif self.N == 3:
            self.xs = -1.0 / 2.0 * (1.0 + 1j * 3 ** (1.0 / 2.0)) * (self.mu1 / 2.0 + numpy.sqrt(
                self.mu1 ** 2 / 4.0 - self.mu2 ** 3 / 27.0 + 0 * 1j)) ** (1.0 / 3.0) - 1.0 / 2.0 * (
                1.0 - 1j * 3 ** (1.0 / 2.0)) * (self.mu1 / 2.0 - numpy.sqrt(
                self.mu1 ** 2 / 4.0 - self.mu2 ** 3 / 27.0 + 0 * 1j)) ** (1.0 / 3.0)
        self.xs = numpy.real(self.xs)

        # global coupling: To be implemented
        # my_first_global_coupling_coefficient = coupling[0, :]

        xdot = -y
        ydot = x ** 3 - self.mu2 * x - self.mu1 - y * (self.nu + self.b * x + x ** 2)
        zdot = -self.c * (numpy.sqrt((x - self.xs) ** 2 + y ** 2) - self.dstar)

        derivative = numpy.array([xdot, ydot, zdot])
        return derivative

    def update_derived_parameters(self):
        """
        The equations were taken from [Saggioetal_2017]
        cf. Eqn. (7), page 17

        Here we parametrize the great arc which lies on a sphere of radius R between the points A and B, which are given by:
            .. math::
                A &= \begin{pmatrix}\mu_{2,start} & -\mu_{1,start} & \nu_{start} \end{pmatrix}
                B &= \begin{pmatrix}\mu_{2,stop} & -\mu_{1,stop} & \nu_{stop} \end{pmatrix}

        Then we parametrize this great arc with z as parameter by R(E \cos z + F \sin z)
            where the unit vectors E and F are given by:
            .. math::
                E &= A/\|A\|
                F &= ((A \times B) \times A)/\|(A \times B) \times A\|
        """

        A = numpy.array([self.mu2_start[0], -self.mu1_start[0], self.nu_start[0]])
        B = numpy.array([self.mu2_stop[0], -self.mu1_stop[0], self.nu_stop[0]])
        self.E = A / numpy.linalg.norm(A)
        self.F = numpy.cross(numpy.cross(A, B), A)
        self.F = self.F / numpy.linalg.norm(self.F)


if __name__ == "__main__":
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)

    # Check that the docstring examples, if there are any, are accurate.
    import doctest

    doctest.testmod()

    # Initialise Model in their default state:
    model = EpileptorCodim3()  # c2s

    LOG.info("EpileptorCodim3 model initialised in its default state without error...")

    from tvb.simulator.plot.phase_plane_interactive import PhasePlaneInteractive
    import tvb.simulator.integrators

    INTEGRATOR = tvb.simulator.integrators.HeunDeterministic(dt=2 ** -5)
    ppi_fig = PhasePlaneInteractive(model=model, integrator=INTEGRATOR)
    ppi_fig.show()
