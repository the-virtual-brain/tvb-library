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
Coupling functions

The activity (state-variables) that have been propagated over the long-range
Connectivity pass through these functions before entering the equations
(Model.dfun()) describing the local dynamics.

The state-variable vector for the $k$-th node or region in the network can be expressed as:
Derivative = Noise + Local dynamics + Coupling(time delays).

More formally:

.. math::

         \\dot{\\Psi}_{k} = - \\Lambda\\left(\\Psi_{k}\\right) + Z \\left(\\Xi_{k} + \\sum_{j=1}^{l} u_{kj} \\Gamma_{v=2}[\\left(\\Psi_{k}(t),  \\Psi_{j}(t-\\tau_{kj}\\right)]\\right).


Here we compute the term Coupling(time delays) or 
:math:`\\sum_{j=1}^{l} u_{kj} \\Gamma_{v=2}[\\left(\\Psi_{k}(t),  \\Psi_{j}(t-\\tau_{kj}\\right)]`, 
where :math:`u_{kj}` are the elements of the weights matrix from a Connectivity datatype.

This term is equivalent to the dot product between the weights matrix (on the
left) and the delayed state vector. This order is important in the case 
case of an asymmetric connectivity matrix, where the
convention to distinguish target ($k$) and source ($j$) nodes is the
following:


.. math::

    \\left(\\begin{matrix} a & b \\
        c & d \end{matrix}\\right)

         C_{kj}  &= \left(\\begin{matrix} ^\mathrm{To}/_\mathrm{from} & 0 & 1 & 2 & \cdots & l \\
                                                           0         & 1  & 1  &  0 & 1  &  0 \\
                                                           1         & 1  & 1  &  0 & 1  &  0 \\
                                                           2         & 1  & 0  &  0 & 1  &  0 \\
                                                     \\vdots          & 1  & 0  &  1 & 0  &  1 \\
                                                           l         & 0  & 0  &  0 & 0  &  0 \\
                                                           \end{matrix}\\right)

.. NOTE: Our convention is the inverse of the BCT toolbox. Furthermore, this
         convention is consistent with the notation used in Physics and in our
         equation, ie, :math:`u_{kj}` matches row-column indexing and describes the
         connection strength from node j to node k


.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Noelia Montejo <Noelia@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""
import numpy

import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.datatypes.arrays as arrays

from tvb.simulator.common import get_logger
LOG = get_logger(__name__)



class Coupling(core.Type):
    """
    The base class for Coupling functions.
    """
    _base_classes = ["Coupling"]

    def __init__(self, **kwargs):
        """
        Initialize the model with parameters as keywords arguments, a sensible
        default parameter set should be provided via the trait mechanism.

        """
        super(Coupling, self).__init__(**kwargs)
        LOG.debug(str(kwargs))


    def configure(self):
        """  """
        super(Coupling, self).configure()
        pass


    def __repr__(self):
        """A formal, executable, representation of a Coupling object."""
        class_name = self.__class__.__name__
        traited_kwargs = self.trait.keys()
        formal = class_name + "(" + "=%s, ".join(traited_kwargs) + "=%s)"
        return formal % eval("(self." + ", self.".join(traited_kwargs) + ")")


    def __str__(self):
        """An informal, human readable, representation of a Coupling object."""
        class_name = self.__class__.__name__
        traited_kwargs = self.trait.keys()
        informal = class_name + "(" + ", ".join(traited_kwargs) + ")"
        return informal


    def __call__(self, g_ij, x_i, x_j):
        """
        Instances of the Coupling class are called by the simulator in the
        following way:

        ::

            k_i = coupling(g_ij, x_i, x_j)

        where g_ij is the connectivity weight matrix, x_i is the current state,
        x_j is the delayed state of the coupling variables chosen for the
        simulation, and k_i is the input to the ith node due to the coupling
        between the nodes.

        Normally, all Coupling types compute a dot product between some
        function of current and past state and the connectivity matrix to
        produce k_i, e.g.

        ::

            (g_ij * x_j).sum(axis=0)

        in the simplest case.

        """
        pass


class coupling_device_info(object):
    """
    Utility class that allows Coupling subclass to annotate their requirements
    for their gfun to run on a device

    Please see tvb.sim.models.model_device_info

    """

    def __init__(self, pars, kernel=""):
        self._pars = pars
        self._kernel = kernel

    @property
    def n_cfpr(self):
        return len(self._pars)

    @property
    def cfpr(self):
        pars = numpy.zeros((self.n_cfpr,), dtype=numpy.float32)
        for i, p in enumerate(self._pars):
            name = p if type(p) in (str, unicode) else p.trait.name
            pars[i] = getattr(self.inst, name)
        return pars

    @property
    def kernel(self):
        return self._kernel

    def __get__(self, inst, ownr):
        if inst:
            self.inst = inst
            return self
        else:
            return None

    def __set__(self, inst, val):
        raise AttributeError



class Linear(Coupling):
    """
    Linear Coupling function.

    """

    a = arrays.FloatArray(
        label = ":math:`a`",
        default=numpy.array([0.00390625,]),
        range = basic.Range(lo = 0.0, hi = 1.0, step = 0.01),
        doc = """Rescales the connection strength while maintaining the ratio
        between different values.""",
        order = 1)

    b = arrays.FloatArray(
        label = ":math:`b`",
        default = numpy.array([0.0,]),
        doc = """Shifts the base of the connection strength while maintaining
        the absolute difference between different values.""",
        order = 2)


    def __call__(self, g_ij, x_i, x_j):
        """
        Evaluate the Linear function for the arg ``x``. The equation being
        evaluated has the following form:

            .. math::
                a x + b


        """
        coupled_input = (g_ij.transpose((2, 1, 0, 3)) * x_j).sum(axis=0)

        return self.a * coupled_input + self.b


    device_info = coupling_device_info(
        pars = ['a', 'b'],
        kernel = """

        // parameters
        float a = P(0)
            , b = P(1);

        I = 0.0;
        for (int j_node=0; j_node<n_node; j_node++, idel++, conn++)
            I += a*GIJ*XJ;
        I += b;

        """
        )



#NOTE: This was primarily created as a work around for the local_connectivity
#      not being able to have a scaling through the UI...
class Scaling(Coupling):
    """
    Scaling Coupling function.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Scaling.__init__
    .. automethod:: Scaling.__call__

    """

    a = basic.Float(
        label="Scaling factor",
        default = 0.00390625,
        range = basic.Range(lo = 0.0, hi = 1.0, step = 0.01),
        doc = """Rescales the connection strength while maintaining the ratio
        between different values.""")


    def __call__(self, g_ij, x_i, x_j):
        """
        Evaluate the Linear function for the arg ``x``. The equation being
        evaluated has the following form:

            .. math::
                a x


        """
        coupled_input = (g_ij.transpose((2, 1, 0, 3)) * x_j).sum(axis=2)
        return self.a * coupled_input

    device_info = coupling_device_info(
        pars = ['a'],
        kernel = """

        // parameters
        float a = P(0);

        I = 0.0;
        for (int j_node=0; j_node<n_node; j_node++, idel++, conn++)
            I += a*GIJ*XJ;

        """
        )



class HyperbolicTangent(Coupling):
    """
    Hyperbolic tangent.

    """

    a = arrays.FloatArray(
        label = ":math:`a`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Minimum of the sigmoid function""",
        order = 1)

    b = arrays.FloatArray(
        label = ":math:`b`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = -1.0, hi = 1.0, step = 10.0),
        doc = """Scaling factor for the variable""",
        order = 2)

    midpoint = arrays.FloatArray(
        label = "midpoint",
        default = numpy.array([0.0,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Midpoint of the linear portion of the sigmoid""",
        order = 3)

    sigma = arrays.FloatArray(
        label = r":math:`\sigma`",
        default = numpy.array([1.0,]),
        range = basic.Range(lo = 0.01, hi = 1000.0, step = 10.0),
        doc = """Standard deviation of the ...""",
        order = 4)

    normalise = basic.Bool(
        label = "normalise by in-strength",
        default = True,
        doc = """Normalise the node coupling by the node's in-strenght""",
        order = 5)


    def __call__(self, g_ij, x_i, x_j):
        r"""
        Evaluate the Sigmoidal function for the arg ``x``. The equation being
        evaluated has the following form:

            .. math::
                        a * (1 + tanh((x - midpoint)/sigma))

        """
        temp =  self.a * (1 +  numpy.tanh((self.b * x_j - self.midpoint) / self.sigma))

        if self.normalise:
            #NOTE: normalising by the strength or degrees may yield NaNs, so fill these values with inf
            in_strength = g_ij.sum(axis=2)[:, :, numpy.newaxis, :]
            in_strength[in_strength==0] = numpy.inf
            temp *= (g_ij.transpose((2, 1, 0, 3)) / in_strength) #region mode normalisation

            coupled_input = temp.mean(axis=0)
        else:
            coupled_input = (g_ij.transpose((2, 1, 0, 3))*temp).mean(axis=0)

        return coupled_input



class Sigmoidal(Coupling):
    """
    Sigmoidal Coupling function.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Sigmoidal.__init__
    .. automethod:: Sigmoidal.__call__

    """
    #NOTE: using a = numpy.pi / numpy.sqrt(3.0) and the default parameter produces something close to the current default for
    #      Linear (a=0.00390625, b=0) over the linear portion of the sigmoid,
    #      with saturation at -1 and 1.

    cmin = arrays.FloatArray(
        label = ":math:`c_{min}`",
        default = numpy.array([-1.0,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Minimum of the sigmoid function""",
        order = 1)

    cmax = arrays.FloatArray(
        label = ":math:`c_{max}`",
        default = numpy.array([1.0,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Maximum of the sigmoid function""",
        order = 2)

    midpoint = arrays.FloatArray(
        label = "midpoint",
        default = numpy.array([0.0,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Midpoint of the linear portion of the sigmoid""",
        order = 3)

    a = arrays.FloatArray(
        label = r":math:`a`",
        default = numpy.array([1.0,]),
        range = basic.Range(lo = 0.01, hi = 1000.0, step = 10.0),
        doc = """Scaling of .... """,
        order = 4)

    sigma = arrays.FloatArray(
        label = r":math:`\sigma`",
        default = numpy.array([230.0,]),
        range = basic.Range(lo = 0.01, hi = 1000.0, step = 10.0),
        doc = """Standard deviation of the ...""",
        order = 5)


    def __init__(self, **kwargs):
        """Precompute a constant after the base __init__"""
        super(Sigmoidal, self).__init__(**kwargs)
        self.pi_on_sqrt3 = numpy.pi / numpy.sqrt(3.0)


    def __call__(self, g_ij, x_i, x_j):
        r"""
        Evaluate the Sigmoidal function for the arg ``x``. The equation being
        evaluated has the following form:

            .. math::
                c_{min} + (c_{max} - c_{min}) / (1.0 + \exp(-a(x-midpoint)/\sigma))


        """
        coupled_input = (g_ij * x_j).sum(axis=1)
        sig = self.cmin + ((self.cmax - self.cmin) / (1.0 + numpy.exp(-self.a *((coupled_input - self.midpoint) / self.sigma))))
        return sig


class SigmoidalJansenRit(Sigmoidal):
    """
    Sigmoidal Coupling function for the Jansen and Rit model.

    """


    cmin = arrays.FloatArray(
        label = ":math:`c_{min}`",
        default = numpy.array([0.0,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Minimum of the sigmoid function""",
        order = 1)

    cmax = arrays.FloatArray(
        label = ":math:`c_{max}`",
        default = numpy.array([2.0 * 0.0025,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Maximum of the sigmoid function""",
        order = 2)

    midpoint = arrays.FloatArray(
        label = "midpoint",
        default = numpy.array([6.0,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 10.0),
        doc = """Midpoint of the linear portion of the sigmoid""",
        order = 3)

    r  = arrays.FloatArray(
        label = r":math:`r`",
        default = numpy.array([1.0,]),
        range = basic.Range(lo = 0.01, hi = 1000.0, step = 10.0),
        doc = """the steepness of the sigmoidal transformation""",
        order = 4)


    a = arrays.FloatArray(
        label = r":math:`a`",
        default = numpy.array([0.56,]),
        range = basic.Range(lo = 0.01, hi = 1000.0, step = 10.0),
        doc = """Scaling of the coupling term """,
        order = 5)




    def __init__(self, **kwargs):
        """Precompute a constant after the base __init__"""
        super(SigmoidalJansenRit, self).__init__(**kwargs)


    def __call__(self, g_ij, x_i, x_j):
        r"""
        Evaluate the Sigmoidal function for the arg ``x``. The equation being
        evaluated has the following form:

            .. math::
                c_{min} + (c_{max} - c_{min}) / (1.0 + \exp(-a(x-midpoint)/\sigma))

        Assumes that x_j has have two state variables.


        """

        magic_exp_number = 709
        diff_input = x_j[:, 0, numpy.newaxis, :, :] - x_j[:, 1, numpy.newaxis, :, :]        
        temp       = self.r * (self.midpoint - (diff_input))
        sigm_y1_y2 = numpy.where(temp > magic_exp_number, self.cmax / (1.0 + numpy.exp(temp)), self.cmax / (1.0 + numpy.exp(temp)))     
        coupled_input = self.a * ( g_ij.transpose((2, 1, 0, 3)) * sigm_y1_y2).sum(axis=0)

        return coupled_input


class PreSigmoidal(Coupling):
    """Pre-Sigmoidal Coupling function (pre-product) with a Static/Dynamic 
    and Local/Global threshold.

    .. automethod:: PreSigmoidal.__init__
    .. automethod:: PreSigmoidal.configure
    .. automethod:: PreSigmoidal.__call__
    .. automethod:: PreSigmoidal.call_static
    .. automethod:: PreSigmoidal.call_dynamic

    """
    #NOTE: Different from Sigmoidal coupling where the product is an input of the sigmoid.
    #      Here the sigmoid is an input of the product.

    H = arrays.FloatArray(
        label = "H",
        default = numpy.array([0.5,]),
        range = basic.Range(lo = -100.0, hi = 100.0, step = 1.0),
        doc = """Global Factor""",
        order = 1)

    Q = arrays.FloatArray(
        label = "Q",
        default = numpy.array([1.,]),
        range = basic.Range(lo = -100.0, hi = 100.0, step = 1.0),
        doc = """Average""",
        order = 2)

    G = arrays.FloatArray(
        label = "G",
        default = numpy.array([60.,]),
        range = basic.Range(lo = -1000.0, hi = 1000.0, step = 1.),
        doc = """Gain""",
        order = 3)

    P = arrays.FloatArray(
        label = "P",
        default = numpy.array([1.,]),
        range = basic.Range(lo = -100.0, hi = 100.0, step = 0.01),
        doc = """Excitation on Inhibition ratio""",
        order = 4)

    theta = arrays.FloatArray(
        label = ":math:`\\theta`",
        default = numpy.array([0.5,]),
        range = basic.Range(lo = -100.0, hi = 100.0, step = 0.01),
        doc = """Threshold.""",
        order = 5)

    dynamic = arrays.IntegerArray(
        label = "Dynamic",
        default = numpy.array([1]),
        range = basic.Range(lo = 0, hi = 1., step = 1),
        doc = """Boolean value for static/dynamic threshold for (0/1).""",
        order = 6)

    globalT = arrays.IntegerArray(
        label = ":math:`global_{\\theta}`",
        default = numpy.array([0,]),
        range = basic.Range(lo = 0, hi = 1., step = 1),
        doc = """Boolean value for local/global threshold for (0/1).""",
        order = 7)


    def __init__(self, **kwargs):
        '''Set the default indirect call.'''
        super(PreSigmoidal, self).__init__(**kwargs)
        self.rightCall = self.call_static
        

    def configure(self):
        """Set the right indirect call."""
        super(PreSigmoidal, self).configure()

        # Dynamic or static threshold
        if self.dynamic:
            self.rightCall = self.call_dynamic
        
        # Global or local threshold 
        if self.globalT:
            self.sliceT = 0
            self.meanOrNot = lambda arr: numpy.diag(arr[:,0,:,0]).mean() * numpy.ones((arr.shape[1],1))

        else:
            self.sliceT = slice(None)
            self.meanOrNot = lambda arr: numpy.diag(arr[:,0,:,0])[:,numpy.newaxis]


    def __call__(self, g_ij, x_i, x_j):
        r"""Evaluate the sigmoidal function for the arg ``x``. The equation being
        evaluated has the following form:

        .. math::
                H * (Q + \tanh(G * (P*x - \theta)))

        """
        return self.rightCall(g_ij, x_i, x_j)
    
        
    def call_static(self, g_ij, x_i, x_j):
        """Static threshold."""    
        
        A_j = self.H * (self.Q + numpy.tanh(self.G * (self.P * x_j \
            - self.theta[self.sliceT,numpy.newaxis])))
        
        return (g_ij.transpose((2, 1, 0, 3)) * A_j).sum(axis=0)


    def call_dynamic(self, g_ij, x_i, x_j):
        """Dynamic threshold as state variable given by the second state variable.
        With the coupling term, returns the direct node output for the dynamic threshold.
        """
        
        A_j = self.H * (self.Q + numpy.tanh(self.G * (self.P * x_j[:,0,:,:] \
            - x_j[:,1,self.sliceT,:])[:,numpy.newaxis,:,:]))
        
        c_0 = (g_ij[:,0] * A_j[:,0]).sum(axis=0)
        c_1 = self.meanOrNot(A_j)
        return numpy.array([c_0, c_1])



class Difference(Coupling):

    a = arrays.FloatArray(
        label = ":math:`a`",
        default=numpy.array([0.1,]),
        range = basic.Range(lo = 0.0, hi = 10., step = 0.1),
        doc = """Rescales the connection strength while maintaining the ratio
        between different values.""",
        order = 1)


    def __call__(self, g_ij, x_i, x_j):
        r"""
        Evaluates a difference coupling:
        x_i: current state. shape ncv, n, m
        x_j: past state. shape n, ncv, n, m

            .. math::
                a \sum_j^N g_ij (x_j - x_i)

        """
        x_i = x_i[None, :, :, :].transpose((2, 1, 3, 0))
        return self.a*(g_ij.transpose((2, 1, 0, 3))*(x_j - x_i)).sum(axis=0)

    device_info = coupling_device_info(
        pars = ['a'],
        kernel = """
        // load parameters
        float a = P(0);

        I = 0.0;
        for (int j_node=0; j_node<n_node; j_node++, idel++, conn++)
            I += a*GIJ*(XJ - XI);
        """
        )



class Kuramoto(Coupling):

    a = arrays.FloatArray(
        label   = ":math:`a`",
        default = numpy.array([1.0,]),
        range   = basic.Range(lo = 0.0, hi = 1.0, step = 0.01),
        doc = """ Rescales the connection strength while maintaining the ratio between
        different values. Notice that the coupling term is also automatically
        rescaled by the number of nodes.""",
        order = 1)


    def __call__(self, g_ij, x_i, x_j, sin=numpy.sin):
        r"""
        Evaluates the Kuramoto-style coupling, a periodic difference:

            .. math::
                a / N \sum_j^N g_ij sin(x_j - x_i - alpha_ij)
                x_i: current state. shape ncv, n, m
                x_j: past state. shape n, ncv, n, m
                
        Assumes heterogenous coupling.        

        """
        number_of_regions = g_ij.shape[0]
        x_i = x_i[None, :, :, :].transpose((2, 1, 3, 0))
        return (self.a / number_of_regions)*(g_ij.transpose((2, 1, 0, 3))*sin(x_j-x_i)).sum(axis=0)

    device_info = coupling_device_info(
        pars = ['a'],
        kernel = """
        // load parameters
        float a = P(0);

        I = 0.0;
        for (int j_node=0; j_node<n_node; j_node++, idel++, conn++)
            I += a*GIJ*sin(XJ - XI);
        """
        )


