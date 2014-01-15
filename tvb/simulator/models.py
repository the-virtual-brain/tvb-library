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
A collection of neuronal dynamics models.

Specific models inherit from the abstract class Model, which in turn inherits
from the class Trait from the tvb.basic.traits module.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>
.. moduleauthor:: Gaurav Malhotra <Gaurav@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import inspect
import numpy
import numexpr
from scipy.integrate import trapz as scipy_integrate_trapz
from scipy.stats import norm as scipy_stats_norm
from tvb.simulator.common import get_logger
import tvb.datatypes.arrays as arrays
import tvb.datatypes.lookup_tables as lookup_tables
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.simulator.noise as noise_module


LOG = get_logger(__name__)


#TODO: For UI convinience set the step in all parameters ranges such that there
#      are apporximately 10 steps from lo to hi...


class Model(core.Type):
    """
    Defines the abstract class for neuronal models.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Model.__init__
    .. automethod:: Model.dfun
    .. automethod:: Model.update_derived_parameters

    """
    _base_classes = ['Model', "JRFast"]
    #NOTE: the parameters that are contained in the following list will be
    #      editable from the ui in an visual manner
    ui_configurable_parameters = []

    noise = noise_module.Noise(
        fixed_type=True, #Can only be Noise in UI, and not a subclass of Noise
        label="Initial Conditions Noise",
        default=noise_module.Noise,
        doc="""A noise source used to provide random initial conditions when
        no, or insufficient, explicit initial conditions are provided. 
        NOTE: Dispersion is computed based on ``state_variable_range``.""",
        order=42 ** 42) #NOTE: Hoping this order will always make it last...


    def __init__(self, **kwargs):
        """
        Initialize the model with parameters as keywords arguments, a sensible
        default parameter set should be provided via the trait mechanism.

        """
        super(Model, self).__init__(**kwargs)
        LOG.debug(str(kwargs))

        #self._state_variables = None
        self._nvar = None
        self.number_of_modes = 1 #NOTE: Models without modes can ignore this.


    def configure(self):
        """  """
        super(Model, self).configure()
        self.update_derived_parameters()


    def __repr__(self):
        """ A formal, executable, representation of a Model object. """
        class_name = self.__class__.__name__
        traited_kwargs = self.trait.keys()
        formal = class_name + "(" + "=%s, ".join(traited_kwargs) + "=%s)"
        return formal % eval("(self." + ", self.".join(traited_kwargs) + ")")


    def __str__(self):
        """ An informal, human readable, representation of a Model object. """
        #NOTE: We don't explicitly list kwds cause some models have too many.
        informal = self.__class__.__name__ + "(**kwargs)"
        return informal


    @property
    def state_variables(self):
        """ A list of the state variables in this model. """
        return self.trait['variables_of_interest'].trait.options


    @property
    def nvar(self):
        """ The number of state variables in this model. """
        return self._nvar
        
        
#    @property
#    def distal_coupling(self):
#        """ Heterogeneous coupling given by the connectivity matrix"""
#        return self._distal_coupling
#        
#    @property
#    def local_coupling(self):
#        """ Homogeneous connectivity given by a local connectivity kernel"""
#        return self._local_coupling
#        
#    @property
#    def internal_coupling(self):
#        """ Internal connectivity between neural masses of a model"""
#        return self._internal_coupling
#        
#    @property
#    def state_coupling(self):
#        """ State operator: A matrix where each elemeent represents a parameter of the model """
#        return self._state_coupling
        

    def update_derived_parameters(self):
        """
        When needed, this should be a method for calculating parameters that are
        calculated based on paramaters directly set by the caller. For example, 
        see, ReducedSetFitzHughNagumo. When not needed, this pass simplifies 
        code that updates an arbitrary models parameters -- ie, this can be 
        safely called on any model, whether it's used or not. 
        """
        pass


    def configure_initial(self, dt, shape):
        """Docs..."""
        #Configure the models noise stream
        if self.noise.ntau > 0.0:
            self.noise.configure_coloured(dt, shape)
        else:
            # The same applies for truncated rv
            self.noise.configure_white(dt, shape)


    def initial(self, dt, history_shape):
        """
        Defines a set of sensible initial conditions, it is only expected that
        these initial conditions be guaranteed to be sensible for the default
        parameter set.

        It is often seen that initial conditions or initial history are filled
        following ic = nsig * noise + loc, where noise is a stream of random
        numbers drawn from a uniform or normal distribution.

        Here, the noise is integrated, that is the initial conditions are
        described by a diffusion process.

        """
        #NOTE: The following max_history_length factor is set such that it
        #considers the worst case possible for the history array, that is, low
        #conduction speed and the longest white matter fibre. With this, plus
        #drawing the random stream of numbers from a truncated normal
        #distribution, we expect to bound the diffussion process used to set
        #the initial history to the state variable ranges. (even for the case
        #of rate based models)

        # Example:
        #        + longest fiber: 200 mm (Ref:)
        #        + min conduction speed: 3 mm/ms (Ref: http://www.scholarpedia.org/article/Axonal_conduction_delays) 
        #          corpus callosum in the macaque monkey.
        #        + max time delay: tau = longest fibre / speed \approx 67 ms
        #        + let's hope for the best...

        max_history_length = 67. # ms
        #TODO: There is an issue of allignment when the current implementation 
        #      is used to pad out explicit inital conditions that aren't as long
        #      as the required history...
        #TODO: We still ideally want to support spatial colour for surfaces --
        #      though this will probably have to be done at the Simulator level
        #      with a linear, strictly-stable, spatially invariant filter
        #      defined on the mesh surface... and in a way that won't change the
        #      temporal correllation structure... and I'm also assuming that the
        #      temporally coloured noise hasn't un-whitened the spatial noise
        #      distribution to start with... [ie, spatial colour is a longer
        #      term problem to solve...])
        #TODO: Ideally we'd like to have a independent random stream for each node.
        #      Currently, if the number of nodes is different we'll get the
        #      slightly different values further in the history array.

        initial_conditions = numpy.zeros(history_shape)
        tpts = history_shape[0]
        nvar = history_shape[1]
        history_shape = history_shape[2:]
        
        self.configure_initial(dt, history_shape)
        noise = numpy.zeros((tpts, nvar) + history_shape)
        nsig  = numpy.zeros(nvar)
        loc   = numpy.zeros(nvar)  

        for tpt in range(tpts):
            for var in range(nvar):
                loc[var]  = self.state_variable_range[self.state_variables[var]].mean()
                nsig[var] = (self.state_variable_range[self.state_variables[var]][1] -
                             self.state_variable_range[self.state_variables[var]][0]) / 2.0 
                nsig[var] = nsig[var] / max_history_length

                # define lower und upper bounds to truncate the random variates to the sv range.
                lo = self.state_variable_range[self.state_variables[var]][0]
                hi = self.state_variable_range[self.state_variables[var]][1]
                lo_bound, up_bound = (lo - loc[var]) / nsig[var], (hi - loc[var]) / nsig[var]
                
                noise[tpt, var, :] = self.noise.generate(history_shape, truncate=True, 
                                                         lo=lo_bound, hi=up_bound)
        
        for var in range(nvar):
                #TODO: Hackery, validate me...-noise.mean(axis=0) ... self.noise.nsig
            initial_conditions[:, var, :] = numpy.sqrt(2.0 * nsig[var]) * numpy.cumsum(noise[:, var, :],axis=0) + loc[var]

        return initial_conditions


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        """
        Defines the dynamic equations. That is, the derivative of the 
        state-variables given their current state ``state_variables``, the past 
        state from other regions of the brain currently arriving ``coupling``, 
        and the current state of the "local" neighbourhood ``local_coupling``.

        """
        pass

    def stationary_trajectory(self,
                              coupling=numpy.array([[0.0]]),
                              initial_conditions=None,
                              n_step=1000, n_skip=10, dt=2 ** -4,
                              map=map):
        """
        Computes the state space trajectory of a single mass model system
        where coupling is static, with a deteministic Euler method. 

        Models expect coupling of shape (n_cvar, n_node), so if this method
        is called with coupling (:, n_cvar, n_ode), it will compute a 
        stationary trajectory for each coupling[i, ...]

        """

        if coupling.ndim == 3:
            def mapped(coupling_i):
                kwargs = dict(initial_conditions=initial_conditions,
                              n_step=n_step, n_skip=n_skip, dt=dt)
                ts, ys = self.stationary_trajectory(coupling_i, **kwargs)
                return ts, ys

            out = [ys for ts, ys in map(mapped, coupling)]
            return ts, numpy.array(out)

        state = initial_conditions
        if type(state) == type(None):
            n_mode = self.number_of_modes
            state = numpy.empty((self.nvar, n_mode))
            for i, (lo, hi) in enumerate(self.state_variable_range.values()):
                state[i, :] = numpy.random.uniform(size=n_mode) * (hi - lo) / 2. + lo
        state = state[:, numpy.newaxis]

        out = [state.copy()]
        for i in xrange(n_step):
            state += dt * self.dfun(state, coupling)
            if i % n_skip == 0:
                out.append(state.copy())

        return numpy.r_[0:dt * n_step:1j * len(out)], numpy.array(out)
        
        

#TODO: both coupling/connectivity and local_coupling should be generalised to 
#      couplings and local_couplings that can be set to independantly on each 
#      state variable of a model at run time. Current functionality would then 
#      come via defaults that turn off the coupling on some state variables. 


class model_device_info(object):
    """
    A model_device_info is a class that provides enough additional information, on
    request, in order to run the owner on a native code device, e.g. a CUDA
    GPU.

    All such device_data classes will need to furnish their corresponding 
    global values as well as corresponding array arguments for update(.), 
    already initialized based on the instance object that the device_data
    instance is attached to.

    Such things are built on conventions: a class should declare both
    a device_data attribute as well as class specific information, that is
    not programmatically available via traits. In general, each of the 
    abstract classes (Model, Noise, Integrator & Coupling) have n_xxpr
    and xxpr, but they don't have symmetric properties, so it will be done
    case by case.

    """

    def __init__(self, pars=[], kernel=""):
        """
        Make a model_device_info instance with a list of trait attributes
        corresponding to the mass model parameters, and a kernel which is
        a string of code required to implement the model's dfun on device.

        The order of the parameters MUST identify the order of the parameters
        in the array returned by the mmpr property and thus the order in
        which the parameters can be read via P(i) macro in the kernel code.

        Don't forget, the kernel code defines per node, per thread update.

        Unforunately, I did not forsee an obvious way to nicely handle modes in the
        reduced models. Kernel code must handle all variables as scalars.

        """

        self._pars = pars
        self._kernel = kernel

    @property
    def n_mmpr(self):
        if self.n_mode == 1:
            return len(self._pars)
        else:
            # have to figure out default par size
            new = self.inst.__class__()
            new.configure()
            count = 0
            for k in new.device_info._pars:
                att = getattr(new, k if type(k) == str else k.trait.name)
                count += att.size
            return count

    @property
    def mmpr(self): # build mmpr array from known inst traits

        nm = self.inst.number_of_modes
        if nm == 1:
            pars = []
            for par in self._pars:
                name = par if type(par) == str else par.trait.name
                pars.append(getattr(self.inst, name))
            return numpy.vstack(pars).T # so self.mmpr[0] yield all pars for node 0
        else:
            pars = []
            new = self.inst.__class__()
            new.configure()
            for k in self._pars:
                name = k if type(k) == str else k.trait.name
                att, attnew = getattr(self.inst, name), getattr(new, name)
                if att.size == attnew.size:
                    pars.append(att.flat[:])
                else:
                    msg = """%r.%r.mmpr requires that modal models be initialized with
                    spatially homogeneous pars, i.e. array([0.0]) not 
                    array([0.0, 0.1, ...]). Please set the per node parameters
                    by hand, after configuring the device handler. Sorry."""
                    raise AttributeError(msg % (self.inst, self))
            return numpy.hstack(pars)[numpy.newaxis, :]

    @property
    def n_mode(self):
        return getattr(self.inst, 'number_of_modes', 1)

    @property
    def n_svar(self):
        return self.inst._nvar * self.n_mode

    @property
    def n_cvar(self):
        return self.inst.cvar.size * self.n_mode

    @property
    def cvar(self):
        assert self.inst.cvar.ndim == 1
        if self.n_mode == 1:
            return self.inst.cvar.astype(numpy.int32)
        else:
            return numpy.tile(self.inst.cvar, (self.n_mode, 1)).flat[:].astype(numpy.int32)

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
        raise AttributeError('%r is not to be set' % (self,))


class WilsonCowan(Model):
    """
    **References**:

    .. [WC_1972] Wilson, H.R. and Cowan, J.D. *Excitatory and inhibitory 
        interactions in localized populations of model neurons*, Biophysical
        journal, 12: 1-24, 1972.
    .. [WC_1973] Wilson, H.R. and Cowan, J.D  *A Mathematical Theory of the 
        Functional Dynamics of Cortical and Thalamic Nervous Tissue*

    Used Eqns 11 and 12 from [WC_1972]_ in ``dfun``.  P and Q represent external inputs,
    which when exploring the phase portrait of the local model are set to
    constant values. However in the case of a full network, P and Q are the
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
 

    The models (:math:`E`, :math:`I`) phase-plane, including a representation of
    the vector field as well as its nullclines, using default parameters, can be
    seen below:

        .. _phase-plane-WC:
        .. figure :: img/WilsonCowan_01_mode_0_pplane.svg
            :alt: Wilson-Cowan phase plane (E, I)

            The (:math:`E`, :math:`I`) phase-plane for the Wilson-Cowan model.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: WilsonCowan.__init__
    .. automethod:: WilsonCowan.dfun

    """
    _ui_name = "Wilson-Cowan model"
    ui_configurable_parameters = ['c_1', 'c_2', 'c_3', 'c_4', 'tau_e', 'tau_i',
                                  'a_e', 'theta_e', 'a_i', 'theta_i', 'r_e',
                                  'r_i', 'k_e', 'k_i', 'P', 'Q']

    #Define traited attributes for this model, these represent possible kwargs.
    c_1 = arrays.FloatArray(
        label=":math:`c_1`",
        default=numpy.array([12.0]),
        range=basic.Range(lo=11.0, hi=16.0, step=0.01),
        doc="""Excitatory to excitatory  coupling coefficient""",
        order=1)

    c_2 = arrays.FloatArray(
        label=":math:`c_2`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=15.0, step=0.01),
        doc="""Inhibitory to excitatory coupling coefficient""",
        order=2)

    c_3 = arrays.FloatArray(
        label=":math:`c_3`",
        default=numpy.array([13.0]),
        range=basic.Range(lo=2.0, hi=22.0, step=0.01),
        doc="""Excitatory to inhibitory coupling coefficient.""",
        order=3)

    c_4 = arrays.FloatArray(
        label=":math:`c_4`",
        default=numpy.array([11.0]),
        range=basic.Range(lo=2.0, hi=15.0, step=0.01),
        doc="""Inhibitory to inhibitory coupling coefficient.""",
        order=4)

    tau_e = arrays.FloatArray(
        label=r":math:`\tau_e`",
        default=numpy.array([10.0]),
        range=basic.Range(lo=5.0, hi=15.0, step=0.01),
        doc="""Excitatory population, membrane time-constant [ms]""",
        order=5)

    tau_i = arrays.FloatArray(
        label=r":math:`\tau_i`",
        default=numpy.array([10.0]),
        range=basic.Range(lo=5.0, hi=15.0, step=0.01),
        doc="""Inhibitory population, membrane time-constant [ms]""",
        order=6)

    a_e = arrays.FloatArray(
        label=":math:`a_e`",
        default=numpy.array([1.2]),
        range=basic.Range(lo=1.0, hi=1.4, step=0.01),
        doc="""The slope parameter for the excitatory response function""",
        order=7)

    theta_e = arrays.FloatArray(
        label=r":math:`\theta_e`",
        default=numpy.array([2.8]),
        range=basic.Range(lo=1.4, hi=4.2, step=0.01),
        doc="""Position of the maximum slope of a sigmoid function [in
        threshold units].""",
        order=8)

    a_i = arrays.FloatArray(
        label=":math:`a_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""The slope parameter for the inhibitory response function""",
        order=9)

    theta_i = arrays.FloatArray(
        label=r":math:`\theta_i`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=6.0, step=0.01),
        doc="""Position of the maximum slope of a sigmoid function [in
        threshold units]""",
        order=10)

    r_e = arrays.FloatArray(
        label=":math:`r_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Excitatory refractory period""",
        order=11)

    r_i = arrays.FloatArray(
        label=":math:`r_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Inhibitory refractory period""",
        order=12)

    k_e = arrays.FloatArray(
        label=":math:`k_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Maximum value of the excitatory response function""",
        order=13)

    k_i = arrays.FloatArray(
        label=":math:`k_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""Maximum value of the inhibitory response function""",
        order=14)

    P = arrays.FloatArray(
        label=":math:`k_i`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""External stimulus to the excitatory population. Constant intensity.Entry point for coupling.""",
        order=15)

    Q = arrays.FloatArray(
        label=":math:`k_i`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""External stimulus to the inhibitory population. Constant intensity.Entry point for coupling.""",
        order=16)


    #Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"E": numpy.array([0.0, 0.5]),
                 "I": numpy.array([0.0, 0.5])},
        doc="""The values for each state-variable should be set to encompass
        the expected dynamic range of that state-variable for the current 
        parameters, it is used as a mechanism for bounding random inital 
        conditions when the simulation isn't started from an explicit history,
        it is also provides the default range of phase-plane plots.""",
        order=15)

    #    variables_of_interest = arrays.IntegerArray(
    #        label = "Variables watched by Monitors",
    #        range = basic.Range(lo = 0.0, hi = 2.0, step = 1.0),
    #        default = numpy.array([0], dtype=numpy.int32),
    #        doc = """This represents the default state-variables of this Model to be
    #        monitored. It can be overridden for each Monitor if desired. The
    #        corresponding state-variable indices for this model are :math:`E = 0`
    #        and :math:`I = 1`.""",
    #        order = 16)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["E", "I"],
        default=["E"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
                                    monitored. It can be overridden for each Monitor if desired. The 
                                    corresponding state-variable indices for this model are :math:`E = 0`
                                    and :math:`I = 1`.""",
        order=16)

    #    coupling_variables = arrays.IntegerArray(
    #        label = "Variables to couple activity through",
    #        default = numpy.array([0], dtype=numpy.int32))

    #    nsig = arrays.FloatArray(
    #        label = "Noise dispersion",
    #        default = numpy.array([0.0]),
    #        range = basic.Range(lo = 0.0, hi = 1.0))


    def __init__(self, **kwargs):
        """
        Initialize the WilsonCowan model's traited attributes, any provided as
        keywords will overide their traited default.

        """
        LOG.info('%s: initing...' % str(self))
        super(WilsonCowan, self).__init__(**kwargs)
        #self._state_variables = ["E", "I"]
        self._nvar = 2
        self.cvar = numpy.array([0, 1], dtype=numpy.int32)
        LOG.debug('%s: inited.' % repr(self))


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""

        .. math::
            \tau \dot{x}(t) &= -z(t) + \phi(z(t)) \\
            \phi(x) &= \frac{c}{1-exp(-a (x-b))}

        """

        E = state_variables[0, :]
        I = state_variables[1, :]

        # long-range coupling
        c_0 = coupling[0, :]

        # short-range (local) coupling
        lc_0 = local_coupling * E
        lc_1 = local_coupling * I 

        x_e = self.c_1 * E - self.c_2 * I + 1.25 + c_0 + lc_0 + lc_1
        x_i = self.c_3 * E - self.c_4 * I + c_0 + lc_0 + lc_1

        s_e = 1.0 / (1.0 + numpy.exp(-self.a_e * (x_e - self.theta_e)))
        s_i = 1.0 / (1.0 + numpy.exp(-self.a_i * (x_i - self.theta_i)))

        dE = (-E + (self.k_e - self.r_e * E) * s_e) / self.tau_e
        dI = (-I + (self.k_i - self.r_i * I) * s_i) / self.tau_i

        derivative = numpy.array([dE, dI])

        return derivative

    # info for device_data
    device_info = model_device_info(

        pars=['c_1', 'c_2', 'c_3', 'c_4', 'tau_e', 'tau_i', 'a_e', 'theta_e',
              'a_i', 'theta_i', 'r_e', 'r_i', 'k_e', 'k_i'],

        kernel="""
        // read parameters
        float c_1     = P(0)
            , c_2     = P(1)
            , c_3     = P(2)
            , c_4     = P(3)
            , tau_e   = P(4)
            , tau_i   = P(5)
            , a_e     = P(6)
            , theta_e = P(7)
            , a_i     = P(8)
            , theta_i = P(9)
            , r_e     = P(10)
            , r_i     = P(11)
            , k_e     = P(12)
            , k_i     = P(13)

        // state variables
            , e = X(0)
            , i = X(1)

        // aux variables
            , c_0 = I(0)

            , x_e = c_1 * e - c_2 * i + c_0
            , x_i = c_3 * e - c_4 * i

            , s_e = 1.0 / (1.0 + exp(-a_e * (x_e - theta_e)))
            , s_i = 1.0 / (1.0 + exp(-a_i * (x_i - theta_i)));

        // set derivatives
        DX(0) = (-e + (k_e - r_e * e) * s_e) / tau_e;
        DX(1) = (-i + (k_i - r_i * i) * s_i) / tau_e;
        """
    )


class ReducedSetFitzHughNagumo(Model):
    r"""
    A reduced representation of a set of Fitz-Hugh Nagumo oscillators,
    [SJ_2008]_.

    The models (:math:`\xi`, :math:`\eta`) phase-plane, including a 
    representation of the vector field as well as its nullclines, using default
    parameters, can be seen below:

        .. _phase-plane-rFHN_0:
        .. figure :: img/ReducedSetFitzHughNagumo_01_mode_0_pplane.svg
            :alt: Reduced set of FitzHughNagumo phase plane (xi, eta), 1st mode.

            The (:math:`\xi`, :math:`\eta`) phase-plane for the first mode of
            a reduced set of Fitz-Hugh Nagumo oscillators.

        .. _phase-plane-rFHN_1:
        .. figure :: img/ReducedSetFitzHughNagumo_01_mode_1_pplane.svg
            :alt: Reduced set of FitzHughNagumo phase plane (xi, eta), 2nd mode.

            The (:math:`\xi`, :math:`\eta`) phase-plane for the second mode of
            a reduced set of Fitz-Hugh Nagumo oscillators.

        .. _phase-plane-rFHN_2:
        .. figure :: img/ReducedSetFitzHughNagumo_01_mode_2_pplane.svg
            :alt: Reduced set of FitzHughNagumo phase plane (xi, eta), 3rd mode.

            The (:math:`\xi`, :math:`\eta`) phase-plane for the third mode of
            a reduced set of Fitz-Hugh Nagumo oscillators.


    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: ReducedSetFitzHughNagumo.__init__
    .. automethod:: ReducedSetFitzHughNagumo.dfun
    .. automethod:: ReducedSetFitzHughNagumo.update_derived_parameters

    #NOTE: In the Article this modelis called StefanescuJirsa2D

    """
    _ui_name = "Stefanescu-Jirsa 2D"
    ui_configurable_parameters = ['tau', 'a', 'b', 'K11', 'K12', 'K21', 'sigma',
                                  'mu']

    #Define traited attributes for this model, these represent possible kwargs.
    tau = arrays.FloatArray(
        label=r":math:`\tau`",
        default=numpy.array([3.0]),
        range=basic.Range(lo=1.5, hi=4.5, step=0.01),
        doc="""doc...(prob something about timescale seperation)""",
        order=1)

    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([0.45]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""doc...""",
        order=2)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([0.9]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""doc...""",
        order=3)

    K11 = arrays.FloatArray(
        label=":math:`K_{11}`",
        default=numpy.array([0.5]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Internal coupling, excitatory to excitatory""",
        order=4)

    K12 = arrays.FloatArray(
        label=":math:`K_{12}`",
        default=numpy.array([0.15]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Internal coupling, excitatory to inhibitory""",
        order=5)

    K21 = arrays.FloatArray(
        label=":math:`K_{21}`",
        default=numpy.array([0.15]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Internal coupling, inhibitory to excitatory""",
        order=6)

    sigma = arrays.FloatArray(
        label=r":math:`\sigma`",
        default=numpy.array([0.35]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Standard deviation of Gaussian distribution""",
        order=7)

    mu = arrays.FloatArray(
        label=r":math:`\mu`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Mean of Gaussian distribution""",
        order=8)

    #Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"xi": numpy.array([-4.0, 4.0]),
                 "eta": numpy.array([-3.0, 3.0]),
                 "alpha": numpy.array([-4.0, 4.0]),
                 "beta": numpy.array([-3.0, 3.0])},
        doc="""The values for each state-variable should be set to encompass
        the expected dynamic range of that state-variable for the current 
        parameters, it is used as a mechanism for bounding random inital 
        conditions when the simulation isn't started from an explicit history,
        it is also provides the default range of phase-plane plots.""",
        order=9)

    #    variables_of_interest = arrays.IntegerArray(
    #        label = "Variables watched by Monitors",
    #        range = basic.Range(lo = 0.0, hi = 4.0, step = 1.0),
    #        default = numpy.array([0, 2], dtype=numpy.int32),
    #        doc = r"""This represents the default state-variables of this Model to be
    #        monitored. It can be overridden for each Monitor if desired. The
    #        corresponding state-variable indices for this model are :math:`\xi = 0`,
    #        :math:`\eta = 1`, :math:`\alpha = 2`, and :math:`\beta= 3`.""",
    #        order = 10)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["xi", "eta", "alpha", "beta"],
        default=["xi", "alpha"],
        select_multiple=True,
        doc=r"""This represents the default state-variables of this Model to be
                                    monitored. It can be overridden for each Monitor if desired. The 
                                    corresponding state-variable indices for this model are :math:`\xi = 0`,
                                    :math:`\eta = 1`, :math:`\alpha = 2`, and :math:`\beta= 3`.""",
        order=10)

    #    number_of_modes = Integer(
    #        order = -1, #-1 => don't show me as a configurable option in the UI...
    #        label = "Number of modes",
    #        default = 3)
    #
    #    nu = Integer(
    #        order = -1, #-1 => don't show me as a configurable option in the UI...
    #        label = "nu",
    #        default = 1500,
    #        range = basic.Range(lo = 0, hi = 10000, step = 100),
    #        doc = """Discretisation of Inhibitory distribution""")
    #
    #    nv = Integer(
    #        order = -1, #-1 => don't show me as a configurable option in the UI...
    #        label = "nv",
    #        default = 1500,
    #        range = basic.Range(lo = 0, hi = 10000, step = 100),
    #        doc = """Discretisation of Excitatory distribution""")

    #    coupling_variables = trait.Array(
    #        label = "Variables to couple activity through",
    #        default = numpy.array([0, 2], dtype=numpy.int32))

    #    nsig = trait.Array(label = "Noise dispersion",
    #                       default = numpy.array([0.0]))


    def __init__(self, **kwargs):
        """
        Initialise parameters for a reduced representation of a set of
        Fitz-Hugh Nagumo oscillators.

        """
        super(ReducedSetFitzHughNagumo, self).__init__(**kwargs)
        #self._state_variables = ["xi", "eta", "alpha", "beta"]
        self._nvar = 4
        self.cvar = numpy.array([0, 2], dtype=numpy.int32)

        #TODO: Hack fix, these cause issues with mapping spatialised parameters 
        #      at the region level to the surface for surface sims.
        #NOTE: Existing modes definition (from the paper) is not properly 
        #      normalised, so number_of_modes can't really be changed
        #      meaningfully anyway adnd nu and nv just need to be "large enough"
        #      so chaning them is only really an optimisation thing...
        self.number_of_modes = 3
        self.nu = 15000
        self.nv = 15000

        #Derived parameters
        self.Aik = None
        self.Bik = None
        self.Cik = None
        self.e_i = None
        self.f_i = None
        self.IE_i = None
        self.II_i = None
        self.m_i = None
        self.n_i = None


    def configure(self):
        """  """
        super(ReducedSetFitzHughNagumo, self).configure()

        if numpy.mod(self.nv, self.number_of_modes):
            error_msg = "nv must be divisible by the number_of_modes: %s"
            LOG.error(error_msg % repr(self))

        if numpy.mod(self.nu, self.number_of_modes):
            error_msg = "nu must be divisible by the number_of_modes: %s"
            LOG.error(error_msg % repr(self))

        self.update_derived_parameters()


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""

        .. math::
            \dot{\xi}_i &= 
                c\left(\xi_i-e_i\frac{\xi_i^3}{3}-\eta_i\right) +
                K_{11}\left[\sum_{k=1}^{3} A_{ik}\xi_k-\xi_i\right] -
                K_{12}\left[\sum_{k=1}^{3} B_{ik}\alpha_k-\xi_i\right] +
                cIE_i \\
            \dot{\eta}_i &=
                \frac{1}{c}\left(\xi_i-b\eta_i+m_i\right) \\
            \dot{\alpha}_i &=
                c\left(\alpha_i-f_i\frac{\alpha_i^3}{3}-\beta_i\right) +
                K_{21}\left[\sum_{k=1}^{3} C_{ik}\xi_i-\alpha_i\right] +
                cII_i \\
            \dot{\beta}_i &= \frac{1}{c}\left(\alpha_i-b\beta_i+n_i\right)

        """

        xi = state_variables[0, :]
        eta = state_variables[1, :]
        alpha = state_variables[2, :]
        beta = state_variables[3, :]

        # sum the activity from the modes
        c_0 = coupling[0, :].sum(axis=1)[:, numpy.newaxis]

        #TODO: generalize coupling variables to a matrix form 
        #c_1 = coupling[1, :] # this cv represents alpha

        dxi = (self.tau * (xi - self.e_i * xi ** 3 / 3.0 - eta) +
               self.K11 * (numpy.dot(xi, self.Aik) - xi) -
               self.K12 * (numpy.dot(alpha, self.Bik) - xi) +
               self.tau * (self.IE_i + c_0 + local_coupling * xi))

        deta = (xi - self.b * eta + self.m_i) / self.tau

        dalpha = (self.tau * (alpha - self.f_i * alpha ** 3 / 3.0 - beta) +
                  self.K21 * (numpy.dot(xi, self.Cik) - alpha) +
                  self.tau * (self.II_i + c_0 + local_coupling * alpha))

        dbeta = (alpha - self.b * beta + self.n_i) / self.tau

        derivative = numpy.array([dxi, deta, dalpha, dbeta])
        #import pdb; pdb.set_trace()
        return derivative


    def update_derived_parameters(self):
        """
        Calculate coefficients for the Reduced FitzHugh-Nagumo oscillator based
        neural field model. Specifically, this method implements equations for
        calculating coefficients found in the supplemental material of
        [SJ_2008]_.

        Include equations here...

        """

        newaxis = numpy.newaxis
        trapz = scipy_integrate_trapz

        stepu = 1.0 / (self.nu + 2 - 1)
        stepv = 1.0 / (self.nv + 2 - 1)

        norm = scipy_stats_norm(loc=self.mu, scale=self.sigma)

        Zu = norm.ppf(numpy.arange(stepu, 1.0, stepu))
        Zv = norm.ppf(numpy.arange(stepv, 1.0, stepv))

        # Define the modes
        V = numpy.zeros((self.number_of_modes, self.nv))
        U = numpy.zeros((self.number_of_modes, self.nu))

        nv_per_mode = self.nv / self.number_of_modes
        nu_per_mode = self.nu / self.number_of_modes

        for i in range(self.number_of_modes):
            V[i, i * nv_per_mode:(i + 1) * nv_per_mode] = numpy.ones(nv_per_mode)
            U[i, i * nu_per_mode:(i + 1) * nu_per_mode] = numpy.ones(nu_per_mode)

        # Normalise the modes
        V = V / numpy.tile(numpy.sqrt(trapz(V * V, Zv, axis=1)), (self.nv, 1)).T
        U = U / numpy.tile(numpy.sqrt(trapz(U * U, Zu, axis=1)), (self.nv, 1)).T

        # Get Normal PDF's evaluated with sampling Zv and Zu
        g1 = norm.pdf(Zv)
        g2 = norm.pdf(Zu)
        G1 = numpy.tile(g1, (self.number_of_modes, 1))
        G2 = numpy.tile(g2, (self.number_of_modes, 1))

        cV = numpy.conj(V)
        cU = numpy.conj(U)

        intcVdZ = trapz(cV, Zv, axis=1)[:, newaxis]
        intG1VdZ = trapz(G1 * V, Zv, axis=1)[newaxis, :]
        intcUdZ = trapz(cU, Zu, axis=1)[:, newaxis]
        #import pdb; pdb.set_trace()
        #Calculate coefficients 
        self.Aik = numpy.dot(intcVdZ, intG1VdZ).T
        self.Bik = numpy.dot(intcVdZ, trapz(G2 * U, Zu, axis=1)[newaxis, :])
        self.Cik = numpy.dot(intcUdZ, intG1VdZ).T

        self.e_i = trapz(cV * V ** 3, Zv, axis=1)[newaxis, :]
        self.f_i = trapz(cU * U ** 3, Zu, axis=1)[newaxis, :]

        self.IE_i = trapz(Zv * cV, Zv, axis=1)[newaxis, :]
        self.II_i = trapz(Zu * cU, Zu, axis=1)[newaxis, :]

        self.m_i = (self.a * intcVdZ).T
        self.n_i = (self.a * intcUdZ).T
        #import pdb; pdb.set_trace()

    # DRAGONS BE HERE
    device_info = model_device_info(
        pars=[
            # given parameters
            'tau', 'a', 'b', 'K11', 'K12', 'K21', 'sigma', 'mu',

            # derived parameters
            'Aik', 'Bik', 'Cik', 'e_i', 'f_i', 'IE_i', 'II_i', 'm_i', 'n_i'
        ],

        kernel="""
        // read given parameters

        float tau   = P(0)
            , a     = P(1)
            , b     = P(2)
            , K11   = P(3)
            , K12   = P(4)
            , K21   = P(5)
            , sigma = P(6)
            , mu    = P(7)

        // modal derived par macros
#define A(i,k) P((8 + 0*9 + 3*(i) + (k)))
#define B(i,k) P((8 + 1*9 + 3*(i) + (k)))
#define C(i,k) P((8 + 2*9 + 3*(i) + (k)))

#define E(i)   P((8 + 3*9 + 3*0 + (i)))
#define F(i)   P((8 + 3*9 + 3*1 + (i)))
#define IE(i)  P((8 + 3*9 + 3*2 + (i)))
#define II(i)  P((8 + 3*9 + 3*3 + (i)))
#define M(i)   P((8 + 3*9 + 3*4 + (i)))
#define N(i)   P((8 + 3*9 + 3*5 + (i)))

        // state variables macros
#define XI(i) X((0*n_mode + (i)))
#define ETA(i) X((1*n_mode + (i)))
#define ALPHA(i) X((2*n_mode + (i)))
#define BETA(i) X((3*n_mode + (i)))

        // aux variables

            , c_0 = I(0)
            , c_1 = I(1) /* --->>>>>>> */ ; /* <<<-------- extremely important semicolon */

        // nothing else but the dot product of the modal interaction coefficients with the instantanoneous state
#define XI_dot_A(k) (XI(1)*A(1, (k)) + XI(2)*A(2, (k)) + XI(3)*A(3, (k)))
#define XI_dot_C(k) (XI(1)*C(1, (k)) + XI(2)*C(2, (k)) + XI(3)*C(3, (k)))
#define ALPHA_dot_B(k) (ALPHA(1)*B(1, (k)) + ALPHA(2)*B(2, (k)) + ALPHA(3)*B(3, (k)))

        // derivatives
        for (int i=0; i<n_mode; i++)
        {
            DX(n_mode*0 + i) = (tau * (XI(i) - E(i)*XI(i)*XI(i)*XI(i)/3.0 - ETA(i)) + \
                                K11 * (XI_dot_A(i) - XI(i)) - \
                                K12 * (ALPHA_dot_B(i) - XI(i)) + \
                                tau * (IE(i) + c_0));

            DX(n_mode*1 + i) = (XI(i) - b*ETA(i) + M(i)) / tau;

            DX(n_mode*2 + i) = (tau * (ALPHA(i) - F(i)*ALPHA(i)*ALPHA(i)*ALPHA(i)/3.0 - BETA(i)) + \
                                K21 * (XI_dot_C(i) - ALPHA(i)) + \
                                tau * (II(i) + c_1));

            DX(n_mode*3 + i) = (ALPHA(i) - b*BETA(i) + N(i)) / tau;
        }

        // clean up
#undef A
#undef B
#undef C
#undef E
#undef F
#undef IE
#undef II
#undef M
#undef N
#undef XI
#undef ETA
#undef ALPHA
#undef BETA
#undef XI_dot_A
#undef XI_dot_C
#undef ALPHA_dot_B
        """
    )


class ReducedSetHindmarshRose(Model):
    r"""
    .. [SJ_2008] Stefanescu and Jirsa, PLoS Computational Biology, *A Low
        Dimensional Description of Globally Coupled Heterogeneous Neural
        Networks of Excitatory and Inhibitory*  4, 11, 26--36, 2008.

    The models (:math:`\xi`, :math:`\eta`) phase-plane, including a 
    representation of the vector field as well as its nullclines, using default
    parameters, can be seen below:

        .. _phase-plane-rHR_0:
        .. figure :: img/ReducedSetHindmarshRose_01_mode_0_pplane.svg
            :alt: Reduced set of FitzHughNagumo phase plane (xi, eta), 1st mode.

            The (:math:`\xi`, :math:`\eta`) phase-plane for the first mode of
            a reduced set of Hindmarsh-Rose oscillators.

        .. _phase-plane-rHR_1:
        .. figure :: img/ReducedSetHindmarshRose_01_mode_1_pplane.svg
            :alt: Reduced set of FitzHughNagumo phase plane (xi, eta), 2nd mode.

            The (:math:`\xi`, :math:`\eta`) phase-plane for the second mode of 
            a reduced set of Hindmarsh-Rose oscillators.

        .. _phase-plane-rHR_2:
        .. figure :: img/ReducedSetHindmarshRose_01_mode_2_pplane.svg
            :alt: Reduced set of FitzHughNagumo phase plane (xi, eta), 3rd mode.

            The (:math:`\xi`, :math:`\eta`) phase-plane for the third mode of
            a reduced set of Hindmarsh-Rose oscillators.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: ReducedSetHindmarshRose.__init__
    .. automethod:: ReducedSetHindmarshRose.dfun
    .. automethod:: ReducedSetHindmarshRose.update_derived_parameters
    
    #NOTE: In the Article this modelis called StefanescuJirsa3D

    """
    _ui_name = "Stefanescu-Jirsa 3D"
    ui_configurable_parameters = ['r', 'a', 'b', 'c', 'd', 's', 'xo', 'K11',
                                  'K12', 'K21', 'sigma', 'mu']

    #Define traited attributes for this model, these represent possible kwargs.
    r = arrays.FloatArray(
        label=":math:`r`",
        default=numpy.array([0.006]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Adaptation parameter""",
        order=1)

    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Dimensionless parameter as in the Hindmarsh-Rose model""",
        order=2)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([3.0]),
        range=basic.Range(lo=0.0, hi=3.0, step=0.01),
        doc="""Dimensionless parameter as in the Hindmarsh-Rose model""",
        order=3)

    c = arrays.FloatArray(
        label=":math:`c`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Dimensionless parameter as in the Hindmarsh-Rose model""",
        order=4)

    d = arrays.FloatArray(
        label=":math:`d`",
        default=numpy.array([5.0]),
        range=basic.Range(lo=2.5, hi=7.5, step=0.01),
        doc="""Dimensionless parameter as in the Hindmarsh-Rose model""",
        order=5)

    s = arrays.FloatArray(
        label=":math:`s`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=6.0, step=0.01),
        doc="""Adaptation paramters, governs feedback""",
        order=6)

    xo = arrays.FloatArray(
        label=":math:`x_{o}`",
        default=numpy.array([-1.6]),
        range=basic.Range(lo=-2.4, hi=-0.8, step=0.01),
        doc="""Leftmost equilibrium point of x""",
        order=7)

    K11 = arrays.FloatArray(
        label=":math:`K_{11}`",
        default=numpy.array([0.5]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Internal coupling, excitatory to excitatory""",
        order=8)

    K12 = arrays.FloatArray(
        label=":math:`K_{12}`",
        default=numpy.array([0.15]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Internal coupling, excitatory to inhibitory""",
        order=9)

    K21 = arrays.FloatArray(
        label=":math:`K_{21}`",
        default=numpy.array([0.15]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Internal coupling, inhibitory to excitatory""",
        order=10)

    sigma = arrays.FloatArray(
        label=r":math:`\sigma`",
        default=numpy.array([0.3]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Standard deviation of Gaussian distribution""",
        order=11)

    mu = arrays.FloatArray(
        label=r":math:`\mu`",
        default=numpy.array([2.2]),
        range=basic.Range(lo=1.1, hi=3.3, step=0.01),
        doc="""Mean of Gaussian distribution""",
        order=12)

    #Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"xi": numpy.array([-4.0, 4.0]),
                 "eta": numpy.array([-25.0, 20.0]),
                 "tau": numpy.array([2.0, 10.0]),
                 "alpha": numpy.array([-4.0, 4.0]),
                 "beta": numpy.array([-20.0, 20.0]),
                 "gamma": numpy.array([2.0, 10.0])},
        doc="""The values for each state-variable should be set to encompass
        the expected dynamic range of that state-variable for the current 
        parameters, it is used as a mechanism for bounding random inital 
        conditions when the simulation isn't started from an explicit history,
        it is also provides the default range of phase-plane plots.""",
        order=13)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["xi", "eta", "tau", "alpha", "beta", "gamma"],
        default=["xi", "eta", "tau"],
        select_multiple=True,
        doc=r"""This represents the default state-variables of this Model to be
                                    monitored. It can be overridden for each Monitor if desired. The 
                                    corresponding state-variable indices for this model are :math:`\xi = 0`,
                                    :math:`\eta = 1`, :math:`\tau = 2`, :math:`\alpha = 3`,
                                    :math:`\beta = 4`, and :math:`\gamma = 5`""",
        order=14)

    #    variables_of_interest = arrays.IntegerArray(
    #        label = "Variables watched by Monitors",
    #        range = basic.Range(lo = 0.0, hi = 6.0, step = 1.0),
    #        default = numpy.array([0, 3], dtype=numpy.int32),
    #        doc = r"""This represents the default state-variables of this Model to be
    #        monitored. It can be overridden for each Monitor if desired. The
    #        corresponding state-variable indices for this model are :math:`\xi = 0`,
    #        :math:`\eta = 1`, :math:`\tau = 2`, :math:`\alpha = 3`,
    #        :math:`\beta = 4`, and :math:`\gamma = 5`""",
    #        order = 14)

    #    number_of_modes = Integer(
    #        order = -1, #-1 => don't show me as a configurable option in the UI...
    #        label = "Number of modes",
    #        default = 3,
    #        doc = """Number of modes""")
    #
    #    nu = Integer(
    #        order = -1, #-1 => don't show me as a configurable option in the UI...
    #        label = "nu",
    #        default = 1500,
    #        range = basic.Range(lo = 500, hi = 10000, step = 500),
    #        doc = """Discretisation of Inhibitory distribution""")
    #
    #    nv = Integer(
    #        order = -1, #-1 => don't show me as a configurable option in the UI...
    #        label = "nv",
    #        default = 1500,
    #        range = basic.Range(lo = 500, hi = 10000, step = 500),
    #        doc = """Discretisation of Excitatory distribution""")

    #    coupling_variables = arrays.IntegerArray(
    #        label = "Variables to couple activity through",
    #        default = numpy.array([0, 3], dtype=numpy.int32))

    #    nsig = arrays.FloatArray(label = "Noise dispersion",
    #                       default = numpy.array([0.0]))


    def __init__(self, **kwargs):
        """
        Initialise parameters for a reduced representation of a set of
        Hindmarsh Rose oscillators, [SJ_2008]_.

        """
        super(ReducedSetHindmarshRose, self).__init__(**kwargs)
        #self._state_variables = ["xi", "eta", "tau", "alpha", "beta", "gamma"]
        self._nvar = 6
        self.cvar = numpy.array([0, 3], dtype=numpy.int32)

        #TODO: Hack fix, these cause issues with mapping spatialised parameters 
        #      at the region level to the surface for surface sims.
        #NOTE: Existing modes definition (from the paper) is not properly 
        #      normalised, so number_of_modes can't really be changed
        #      meaningfully anyway adnd nu and nv just need to be "large enough"
        #      so chaning them is only really an optimisation thing...
        self.number_of_modes = 3
        self.nu = 1500
        self.nv = 1500

        #derived parameters
        self.A_ik = None
        self.B_ik = None
        self.C_ik = None
        self.a_i = None
        self.b_i = None
        self.c_i = None
        self.d_i = None
        self.e_i = None
        self.f_i = None
        self.h_i = None
        self.p_i = None
        self.IE_i = None
        self.II_i = None
        self.m_i = None
        self.n_i = None


    def configure(self):
        """  """
        super(ReducedSetHindmarshRose, self).configure()

        if numpy.mod(self.nv, self.number_of_modes):
            error_msg = "nv must be divisible by the number_of_modes: %s"
            LOG.error(error_msg % repr(self))

        if numpy.mod(self.nu, self.number_of_modes):
            error_msg = "nu must be divisible by the number_of_modes: %s"
            LOG.error(error_msg % repr(self))

        self.update_derived_parameters()


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""
        The dynamic equations were taken from [SJ_2008]_, ...

        .. math::
            \dot{\xi}_i &= \eta_i - a_i\xi_i^3 + b_i\xi_i^2 -
                             \tau_i + K_{11} \left[\sum_{k=1}^{3} A_{ik} \xi_k -
                             \xi_i \right] - K_{12} \left[\sum_{k=1}^{3} B_{ik} \alpha_k -
                             \xi_i\right] + IE_i \\
            \dot{\eta}_i &= c_i-d_i\xi_i^2-\eta_i \\
            \dot{\tau}_i &= rs\xi_i-r\tau_i-m_i \\
            \dot{\alpha}_i &= \beta_i - e_i \alpha_i^3 +
                                f_i \alpha_i^2 - \gamma_i +
                                K_{21} \left[\sum_{k=1}^{3} C_{ik} \xi_k -
                                \alpha_i \right] + II_i \\
            \dot{\beta}_i &= h_i - p_i \alpha_i^2 - \beta_i \\
            \dot{\gamma}_i &= rs \alpha_i - r \gamma_i - n_i

        """

        xi = state_variables[0, :]
        eta = state_variables[1, :]
        tau = state_variables[2, :]
        alpha = state_variables[3, :]
        beta = state_variables[4, :]
        gamma = state_variables[5, :]

        c_0 = coupling[0, :].sum(axis=1)[:, numpy.newaxis]
        #c_1 = coupling[1, :]

        dxi = (eta - self.a_i * xi ** 3 + self.b_i * xi ** 2 - tau +
               self.K11 * (numpy.dot(xi, self.A_ik) - xi) -
               self.K12 * (numpy.dot(alpha, self.B_ik) - xi) +
               self.IE_i + c_0 + local_coupling * xi)

        deta = self.c_i - self.d_i * xi ** 2 - eta

        dtau = self.r * self.s * xi - self.r * tau - self.m_i

        dalpha = (beta - self.e_i * alpha ** 3 + self.f_i * alpha ** 2 - gamma +
                  self.K21 * (numpy.dot(xi, self.C_ik) - alpha) +
                  self.II_i + c_0 + local_coupling * alpha)

        dbeta = self.h_i - self.p_i * alpha ** 2 - beta

        dgamma = self.r * self.s * alpha - self.r * gamma - self.n_i

        derivative = numpy.array([dxi, deta, dtau, dalpha, dbeta, dgamma])

        return derivative


    def update_derived_parameters(self):
        """
        Calculate coefficients for the neural field model based on a Reduced set
        of Hindmarsh-Rose oscillators. Specifically, this method implements
        equations for calculating coefficients found in the supplemental
        material of [SJ_2008]_.

        Include equations here...

        """

        newaxis = numpy.newaxis
        trapz = scipy_integrate_trapz

        stepu = 1.0 / (self.nu + 2 - 1)
        stepv = 1.0 / (self.nv + 2 - 1)

        norm = scipy_stats_norm(loc=self.mu, scale=self.sigma)

        Iu = norm.ppf(numpy.arange(stepu, 1.0, stepu))
        Iv = norm.ppf(numpy.arange(stepv, 1.0, stepv))

        # Define the modes
        V = numpy.zeros((self.number_of_modes, self.nv))
        U = numpy.zeros((self.number_of_modes, self.nu))

        nv_per_mode = self.nv / self.number_of_modes
        nu_per_mode = self.nu / self.number_of_modes

        for i in range(self.number_of_modes):
            V[i, i * nv_per_mode:(i + 1) * nv_per_mode] = numpy.ones(nv_per_mode)
            U[i, i * nu_per_mode:(i + 1) * nu_per_mode] = numpy.ones(nu_per_mode)

        # Normalise the modes
        V = V / numpy.tile(numpy.sqrt(trapz(V * V, Iv, axis=1)), (self.nv, 1)).T
        U = U / numpy.tile(numpy.sqrt(trapz(U * U, Iu, axis=1)), (self.nu, 1)).T

        # Get Normal PDF's evaluated with sampling Zv and Zu
        g1 = norm.pdf(Iv)
        g2 = norm.pdf(Iu)
        G1 = numpy.tile(g1, (self.number_of_modes, 1))
        G2 = numpy.tile(g2, (self.number_of_modes, 1))

        cV = numpy.conj(V)
        cU = numpy.conj(U)

        #import pdb; pdb.set_trace()
        intcVdI = trapz(cV, Iv, axis=1)[:, newaxis]
        intG1VdI = trapz(G1 * V, Iv, axis=1)[newaxis, :]
        intcUdI = trapz(cU, Iu, axis=1)[:, newaxis]

        #Calculate coefficients
        self.A_ik = numpy.dot(intcVdI, intG1VdI).T
        self.B_ik = numpy.dot(intcVdI, trapz(G2 * U, Iu, axis=1)[newaxis, :])
        self.C_ik = numpy.dot(intcUdI, intG1VdI).T

        self.a_i = self.a * trapz(cV * V ** 3, Iv, axis=1)[newaxis, :]
        self.e_i = self.a * trapz(cU * U ** 3, Iu, axis=1)[newaxis, :]
        self.b_i = self.b * trapz(cV * V ** 2, Iv, axis=1)[newaxis, :]
        self.f_i = self.b * trapz(cU * U ** 2, Iu, axis=1)[newaxis, :]
        self.c_i = (self.c * intcVdI).T
        self.h_i = (self.c * intcUdI).T

        self.IE_i = trapz(Iv * cV, Iv, axis=1)[newaxis, :]
        self.II_i = trapz(Iu * cU, Iu, axis=1)[newaxis, :]

        self.d_i = (self.d * intcVdI).T
        self.p_i = (self.d * intcUdI).T

        self.m_i = (self.r * self.s * self.xo * intcVdI).T
        self.n_i = (self.r * self.s * self.xo * intcUdI).T

    # DRAGONS BE HERE
    device_info = model_device_info(
        pars=[
            # given parameters
            'r', 'a', 'b', 'c', 'd', 's', 'xo', 'K11', 'K12', 'K21', 'sigma', 'mu',
            # derived parameters
            'A_ik', 'B_ik', 'C_ik', 'a_i', 'b_i', 'c_i', 'd_i', 'e_i',
            'f_i', 'h_i', 'p_i', 'IE_i', 'II_i', 'm_i', 'n_i'],


        kernel="""
        // read given parameters

        float r     = P(0)
            , a     = P(1)
            , b     = P(2)
            , c     = P(3)
            , d     = P(4)
            , s     = P(5)
            , xo    = P(6)
            , K11   = P(7)
            , K12   = P(8)
            , K21   = P(9)
            , sigma = P(10)
            , mu    = P(11)

        // modal derived par macros (mX is X_ik, vX is x_i (sorry))
#define mA(i, k) P((12 + 0*9 + 3*(i) + (k)))
#define mB(i, k) P((12 + 1*9 + 3*(i) + (k)))
#define mC(i, k) P((12 + 2*9 + 3*(i) + (k)))

#define vA(i)    P((12 + 3*9 + 3*0 + (i)))
#define vB(i)    P((12 + 3*9 + 3*1 + (i)))
#define vC(i)    P((12 + 3*9 + 3*2 + (i)))
#define vD(i)    P((12 + 3*9 + 3*3 + (i)))
#define vE(i)    P((12 + 3*9 + 3*4 + (i)))
#define vF(i)    P((12 + 3*9 + 3*5 + (i)))
#define vH(i)    P((12 + 3*9 + 3*6 + (i)))
#define vP(i)    P((12 + 3*9 + 3*7 + (i)))
#define vIE(i)   P((12 + 3*9 + 3*8 + (i)))
#define vII(i)   P((12 + 3*9 + 3*9 + (i)))
#define vM(i)    P((12 + 3*9 + 3*10 + (i)))
#define vN(i)    P((12 + 3*9 + 3*11 + (i)))

        // state variable macros
#define XI(i)    X((0*n_mode + (i)))
#define ETA(i)   X((1*n_mode + (i)))
#define TAU(i)   X((2*n_mode + (i)))
#define ALPHA(i) X((3*n_mode + (i)))
#define BETA(i)  X((4*n_mode + (i)))
#define GAMMA(i) X((5*n_mode + (i)))

        // aux variables
            , c_0 = I(0)
            , c_1 = I(1)       /* the semicolon --> */  ;  /* don't forget it */
            
        // modal interactions
#define XI_dot_A(k) (XI(1)*mA(1, (k)) + XI(2)*mA(2, (k)) + XI(3)*mA(3, (k)))
#define XI_dot_C(k) (XI(1)*mC(1, (k)) + XI(2)*mC(2, (k)) + XI(3)*mC(3, (k)))
#define ALPHA_dot_B(k) (ALPHA(1)*mB(1, (k)) + ALPHA(2)*mB(2, (k)) + ALPHA(3)*mB(3, (k)))

        // derivatives
        for (int i=0; i<n_mode; i++)
        {
/* xi */    DX(n_mode*0 + i) = (ETA(i) - vA(i)*XI(i)*XI(i)*XI(i) + vB(i)*XI(i)*XI(i) - TAU(i) + \
                               K11 * (XI_dot_A(i) - XI(i)) - \
                               K12 * (ALPHA_dot_B(i) - XI(i)) + \
                               vIE(i) + c_0);

/* eta */   DX(n_mode*1 + i) = vC(i) - vD(i)*XI(i)*XI(i) - ETA(i);

/* tau */   DX(n_mode*2 + i) = r*s*XI(i) - r*TAU(i) - vM(i);

/* alpha */ DX(n_mode*3 + i) = (BETA(i) - vE(i)*ALPHA(i)*ALPHA(i)*ALPHA(i) + vF(i)*ALPHA(i)*ALPHA(i) - GAMMA(i) +\
                                K21 * (XI_dot_C(i) - ALPHA(i)) + \
                                vII(i) + c_1);

/* beta */  DX(n_mode*4 + i) = vH(i) - vP(i)*ALPHA(i)*ALPHA(i) - BETA(i);

/* gamma */ DX(n_mode*5 + i) = r*s*ALPHA(i) - r*GAMMA(i) - vN(i);
        }

#undef mA
#undef mB
#undef mC

#undef vA
#undef vB
#undef vC
#undef vD
#undef vE
#undef vF
#undef vH
#undef vP
#undef vIE
#undef vII
#undef vM
#undef vN

#undef XI
#undef ETA   
#undef TAU   
#undef ALPHA 
#undef BETA  
#undef GAMMA 

#undef XI_dot_A
#undef XI_dot_C
#undef ALPHA_dot_B

"""
    )


class JansenRit(Model):
    """
    The Jansen and Rit is a biologically inspired mathematical framework
    originally conceived to simulate the spontaneous electrical activity of
    neuronal assemblies, with a particular focus on alpha activity, for instance,
    as measured by EEG. Later on, it was discovered that in addition to alpha
    activity, this model was also able to simulate evoked potentials.

    .. [JR_1995]  Jansen, B., H. and Rit V., G., *Electroencephalogram and
        visual evoked potential generation in a mathematical model of
        coupled cortical columns*, Biological Cybernetics (73) 357:366, 1995.

    .. [J_1993] Jansen, B., Zouridakis, G. and Brandt, M., *A
        neurophysiologically-based mathematical model of flash visual evoked
        potentials*

    .. figure :: img/JansenRit_45_mode_0_pplane.svg
        :alt: Jansen and Rit phase plane (y4, y5)

        The (:math:`y_4`, :math:`y_5`) phase-plane for the Jansen and Rit model.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: JansenRit.__init__
    .. automethod:: JansenRit.dfun

    """

    _ui_name = "Jansen-Rit"
    ui_configurable_parameters = ['A', 'B', 'a', 'b', 'v0', 'nu_max', 'r', 'J',
                                  'a_1', 'a_2', 'a_3', 'a_4', 'p_min', 'p_max',
                                  'mu']

    #Define traited attributes for this model, these represent possible kwargs.
    A = arrays.FloatArray(
        label=":math:`A`",
        default=numpy.array([3.25]),
        range=basic.Range(lo=2.6, hi=9.75, step=0.05),
        doc="""Maximum amplitude of EPSP [mV]. Also called average synaptic gain.""",
        order=1)

    B = arrays.FloatArray(
        label=":math:`B`",
        default=numpy.array([22.0]),
        range=basic.Range(lo=17.6, hi=110.0, step=0.2),
        doc="""Maximum amplitude of IPSP [mV]. Also called average synaptic gain.""",
        order=2)

    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([0.1]),
        range=basic.Range(lo=0.05, hi=0.15, step=0.01),
        doc="""Reciprocal of the time constant of passive membrane and all
        other spatially distributed delays in the dendritic network [ms^-1].
        Also called average synaptic time constant.""",
        order=3)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([0.05]),
        range=basic.Range(lo=0.025, hi=0.075, step=0.005),
        doc="""Reciprocal of the time constant of passive membrane and all
        other spatially distributed delays in the dendritic network [ms^-1].
        Also called average synaptic time constant.""",
        order=4)

    v0 = arrays.FloatArray(
        label=":math:`v_0`",
        default=numpy.array([5.52]),
        range=basic.Range(lo=3.12, hi=6.0, step=0.02),
        doc="""Firing threshold (PSP) for which a 50% firing rate is achieved.
        In other words, it is the value of the average membrane potential
        corresponding to the inflection point of the sigmoid [mV].""",
        order=5)

    nu_max = arrays.FloatArray(
        label=r":math:`\nu_{max}`",
        default=numpy.array([0.0025]),
        range=basic.Range(lo=0.00125, hi=0.00375, step=0.00001),
        doc="""Determines the maximum firing rate of the neural population
        [s^-1].""",
        order=6)

    r = arrays.FloatArray(
        label=":math:`r`",
        default=numpy.array([0.56]),
        range=basic.Range(lo=0.28, hi=0.84, step=0.01),
        doc="""Steepness of the sigmoidal transformation [mV^-1].""",
        order=7)

    J = arrays.FloatArray(
        label=":math:`J`",
        default=numpy.array([135.0]),
        range=basic.Range(lo=65.0, hi=1350.0, step=1.),
        doc="""Average number of synapses between populations.""",
        order=8)

    a_1 = arrays.FloatArray(
        label=r":math:`\alpha_1`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=1.5, step=0.1),
        doc="""Average probability of synaptic contacts in the feedback
        excitatory loop.""",
        order=9)

    a_2 = arrays.FloatArray(
        label=r":math:`\alpha_2`",
        default=numpy.array([0.8]),
        range=basic.Range(lo=0.4, hi=1.2, step=0.1),
        doc="""Average probability of synaptic contacts in the feedback
        excitatory loop.""",
        order=10)

    a_3 = arrays.FloatArray(
        label=r":math:`\alpha_3`",
        default=numpy.array([0.25]),
        range=basic.Range(lo=0.125, hi=0.375, step=0.005),
        doc="""Average probability of synaptic contacts in the feedback
        excitatory loop.""",
        order=11)

    a_4 = arrays.FloatArray(
        label=r":math:`\alpha_4`",
        default=numpy.array([0.25]),
        range=basic.Range(lo=0.125, hi=0.375, step=0.005),
        doc="""Average probability of synaptic contacts in the slow feedback
        inhibitory loop.""",
        order=12)

    p_min = arrays.FloatArray(
        label=":math:`p_{min}`",
        default=numpy.array([0.12]),
        range=basic.Range(lo=0.0, hi=0.12, step=0.01),
        doc="""Minimum input firing rate.""",
        order=13)

    p_max = arrays.FloatArray(
        label=":math:`p_{max}`",
        default=numpy.array([0.32]),
        range=basic.Range(lo=0.0, hi=0.32, step=0.01),
        doc="""Maximum input firing rate.""",
        order=14)

    mu = arrays.FloatArray(
        label=r":math:`\mu_{max}`",
        default=numpy.array([0.22]),
        range=basic.Range(lo=0.0, hi=0.22, step=0.01),
        doc="""Mean input firing rate""",
        order=15)

    #Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"y0": numpy.array([-1.0, 1.0]),
                 "y1": numpy.array([-500.0, 500.0]),
                 "y2": numpy.array([-50.0, 50.0]),
                 "y3": numpy.array([-6.0, 6.0]),
                 "y4": numpy.array([-20.0, 20.0]),
                 "y5": numpy.array([-500.0, 500.0])},
        doc="""The values for each state-variable should be set to encompass
        the expected dynamic range of that state-variable for the current 
        parameters, it is used as a mechanism for bounding random inital 
        conditions when the simulation isn't started from an explicit history,
        it is also provides the default range of phase-plane plots.""",
        order=16)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["y0", "y1", "y2", "y3", "y4", "y5"],
        default=["y0", "y1", "y2", "y3"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
                                    monitored. It can be overridden for each Monitor if desired. The 
                                    corresponding state-variable indices for this model are :math:`y0 = 0`,
                                    :math:`y1 = 1`, :math:`y2 = 2`, :math:`y3 = 3`, :math:`y4 = 4`, and
                                    :math:`y5 = 5`""",
        order=17)

    #    variables_of_interest = arrays.IntegerArray(
    #        label = "Variables watched by Monitors",
    #        range = basic.Range(lo = 0.0, hi = 6.0, step = 1.0),
    #        default = numpy.array([0, 3], dtype=numpy.int32),
    #        doc = """This represents the default state-variables of this Model to be
    #        monitored. It can be overridden for each Monitor if desired. The
    #        corresponding state-variable indices for this model are :math:`y0 = 0`,
    #        :math:`y1 = 1`, :math:`y2 = 2`, :math:`y3 = 3`, :math:`y4 = 4`, and
    #        :math:`y5 = 5`""",
    #        order = 17)


    def __init__(self, **kwargs):
        """
        Initialise parameters for the Jansen Rit column, [JR_1995]_.

        """
        LOG.info("%s: initing..." % str(self))
        super(JansenRit, self).__init__(**kwargs)

        #self._state_variables = ["y0", "y1", "y2", "y3", "y4", "y5"]
        self._nvar = 6

        self.cvar = numpy.array([1, 2], dtype=numpy.int32)

        #TODO: adding an update_derived_parameters method to remove some of the
        #      redundant parameter multiplication in dfun should gain about 7%
        #      maybe not worth it... The three exp() kill us at ~90 times *
        #self.nu_max2 = None #2.0 * self.nu_max
        #self.Aa = None # self.A * self.a
        #self.Bb = None # self.B * self.b
        #self.aa = None # self.a**2
        #self.a2 = None # 2.0 * self.a
        #self.b2 = None # 2.0 * self.b
        #self.a_1J = None # self.a_1 * self.J
        #self.a_2J = None # self.a_2 * self.J
        #self.a_3J = None # self.a_3 * self.J
        #self.a_4J = None # self.a_4 * self.J

        LOG.debug('%s: inited.' % repr(self))


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""
        The dynamic equations were taken from [JR_1995]_

        .. math::
            \dot{y_0} &= y_3 \\
            \dot{y_3} &= A a\,S[y_1 - y_2] - 2a\,y_3 - 2a^2\, y_0 \\
            \dot{y_1} &= y_4\\
            \dot{y_4} &= A a \,[p(t) + \alpha_2 J + S[\alpha_1 J\,y_0]+ c_0]
                        -2a\,y - a^2\,y_1 \\
            \dot{y_2} &= y_5 \\
            \dot{y_5} &= B b (\alpha_4 J\, S[\alpha_3 J \,y_0]) - 2 b\, y_5
                        - b^2\,y_2 \\
            S[v] &= \frac{2\, \nu_{max}}{1 + \exp^{r(v_0 - v)}}


        :math:`p(t)` can be any arbitrary function, including white noise or 
        random numbers taken from a uniform distribution, representing a pulse
        density with an amplitude varying between 120 and 320

        For Evoked Potentials, a transient component of the input, 
        representing the impulse density attribuable to a brief visual input is 
        applied. Time should be in seconds.

        .. math::
            p(t) = q\,(\frac{t}{w})^n \, \exp{-\frac{t}{w}} \\
            q = 0.5 \\
            n = 7 \\
            w = 0.005 [s]


        """
        #NOTE: We could speed up this model by making the number below smaller,
        #      because the exp() dominate runtime, though we'd need to validate
        #      the trade-off in numerical accuracy...
        magic_exp_number = 709

        y0 = state_variables[0, :]
        y1 = state_variables[1, :]
        y2 = state_variables[2, :]
        y3 = state_variables[3, :]
        y4 = state_variables[4, :]
        y5 = state_variables[5, :]

        lrc = coupling[0, :] -  coupling[1, :]
        short_range_coupling =  local_coupling*(y1 -  y2)

        # NOTE: for local couplings
        # 0: pyramidal cells
        # 1: excitatory interneurons
        # 2: inhibitory interneurons
        # 0 -> 1,
        # 0 -> 2,  
        # 1 -> 0,
        # 2 -> 0,

        #p_min = self.p_min
        #p_max = self.p_max
        #p = p_min + (p_max - p_min) * numpy.random.uniform()

        #NOTE: We were getting numerical overflow in the three exp()s below...
        temp = self.r * (self.v0 - (y1 - y2))
        sigm_y1_y2 = numpy.where(temp > magic_exp_number, 0.0, 2.0 * self.nu_max / (1.0 + numpy.exp(temp)))

        temp = self.r * (self.v0 - (self.a_1 * self.J * y0))
        sigm_y0_1 = numpy.where(temp > magic_exp_number, 0.0, 2.0 * self.nu_max / (1.0 + numpy.exp(temp)))

        temp = self.r * (self.v0 - (self.a_3 * self.J * y0))
        sigm_y0_3 = numpy.where(temp > magic_exp_number, 0.0, 2.0 * self.nu_max / (1.0 + numpy.exp(temp)))

        dy0 = y3
        dy3 = self.A * self.a * sigm_y1_y2 - 2.0 * self.a * y3 - self.a ** 2 * y0
        dy1 = y4
        dy4 = self.A * self.a * (self.mu + self.a_2 * self.J * sigm_y0_1 + lrc + short_range_coupling) - 2.0 * self.a * y4 - self.a ** 2 * y1
        dy2 = y5
        dy5 = self.B * self.b * (self.a_4 * self.J * sigm_y0_3) - 2.0 * self.b * y5 - self.b ** 2 * y2

        derivative = numpy.array([dy0, dy1, dy2, dy3, dy4, dy5])

        return derivative

    device_info = model_device_info(

        pars=['A', 'B', 'a', 'b', 'v0', 'nu_max', 'r', 'J', 'a_1', 'a_2', 'a_3', 'a_4',
              'p_min', 'p_max', 'mu'],

        kernel="""
        // read parameters
        float A      = P(0)
            , B      = P(1)
            , a      = P(2)
            , b      = P(3)
            , v0     = P(4)
            , nu_max = P(5)
            , r      = P(6)
            , J      = P(7)
            , a_1    = P(8)
            , a_2    = P(9)
            , a_3    = P(10)
            , a_4    = P(11)
            , p_min  = P(12)
            , p_max  = P(13)
            , mu     = P(14)

        // state variables
            , y0 = X(0)
            , y1 = X(1)
            , y2 = X(2)
            , y3 = X(3)
            , y4 = X(4)
            , y5 = X(5)
            , y6 = X(6)

        // aux variables
            , c_0 = I(0)
            , sigm_y1_y2 = 2.0 * nu_max / (1.0 + exp( r * (v0 - (y1 - y2)) ))
            , sigm_y0_1  = 2.0 * nu_max / (1.0 + exp( r * (v0 - (a_1 * J * y0))))
            , sigm_y0_3  = 2.0 * nu_max / (1.0 + exp( r * (v0 - (a_3 * J * y0))));

        // derivatives
        DX(0) = y3;
        DX(1) = y4;
        DX(2) = y5;
        DX(3) = A * a * sigm_y1_y2 - 2.0 * a * y3 - a*a*y0;
        DX(4) = A * a * (mu + a_2 * J * sigm_y0_1 + c_0) - 2.0 * a * y4 - a*a*y1;
        DX(5) = B * b * (a_4 + J * sigm_y0_3) - 2.0 * b * y5 - b*b*y2;
        """
    )



class JRFast(JansenRit):
    """
    This is an optimized version of the above JansenRit model, using numexpr and
    constant memory (as far as is obvious).

    Note that it caches parameters and derivative arrays on the first call to
    the dfun method, so if you change the number of nodes or the parameters, you
    need to invalidate the cache by setting the invalid_dfun_cache attribute to
    True.

    """

    invalid_dfun_cache = True

    #@profile
    def dfun(self, y, coupling, local_coupling=0.0, ev=numexpr.evaluate):

        if self.invalid_dfun_cache:
            self.dy = y.copy() * 0.0
            self.y1m2 = y[1].copy()
            self.dfunlocals = {}
            for k in ['nu_max', 'r', 'v0', 'a_1', 'J', 'a_3', 'A', 'a', 'mu', 
                    'a_2', 'B', 'b', 'a_4']:
                self.dfunlocals[k] = getattr(self, k)
            self.dfunglobals = {}    
            self.invalid_dfun_cache = False

        l = self.dfunlocals
        g = self.dfunglobals

        l['y0'], l['y1'], l['y2'], l['y3'], l['y4'], l['y5'] = y

        l['c0'], l['c1'] = coupling

        # self.cvar = numpy.array([1, 2], dtype=numpy.int32)
        self.y1m2[:] = y[1]
        self.y1m2 -= y[2]
        l['lc'] = local_coupling * self.y1m2

        self.dy[:3] = y[3:]

        ev('A * a * (2.0 * nu_max / (1.0 + exp(r * (v0 - (y1 - y2))))) - 2.0 * a * y3 - a ** 2 * y0', l, g, out=self.dy[3], casting='no')
        ev('A * a * (mu + a_2 * J * (2.0 * nu_max / (1.0 + exp(r * (v0 - (a_1 * J * y0))))) + (c0 - c1) + lc) - 2.0 * a * y4 - a ** 2 * y1', l, g, out=self.dy[4], casting='no')
        ev('B * b * (a_4 * J * (2.0 * nu_max / (1.0 + exp(r * (v0 - (a_3 * J * y0)))))) - 2.0 * b * y5 - b ** 2 * y2', l, g, out=self.dy[5], casting='no')

        return self.dy



class Generic2dOscillator(Model):
    """
    The Generic2dOscillator model is a generic dynamic system with two state
    variables. The dynamic equations of this model are composed of two ordinary
    differential equations comprising two nullclines. The first nullcline is a
    cubic function as it is found in most neuron and population models; the 
    second nullcline is arbitrarily configurable as a polynomial function up to
    second order. The manipulation of the latter nullcline's parameters allows
    to generate a wide range of different behaviors. 

    See:
        
    
        .. [FH_1961] FitzHugh, R., *Impulses and physiological states in theoretical
            models of nerve membrane*, Biophysical Journal 1: 445, 1961. 
    
        .. [Nagumo_1962] Nagumo et.al, *An Active Pulse Transmission Line Simulating
            Nerve Axon*, Proceedings of the IRE 50: 2061, 1962.
        
        .. [SJ_2011] Stefanescu, R., Jirsa, V.K. *Reduced representations of 
            heterogeneous mixed neural networks with synaptic coupling*.  
            Physical Review E, 83, 2011. 

        .. [SJ_2010]	Jirsa VK, Stefanescu R.  *Neural population modes capture 
            biologically realistic large-scale network dynamics*. Bulletin of 
            Mathematical Biology, 2010.    

        .. [SJ_2008_a] Stefanescu, R., Jirsa, V.K. *A low dimensional description
            of globally coupled heterogeneous neural networks of excitatory and
            inhibitory neurons*. PLoS Computational Biology, 4(11), 2008).


    The model's (:math:`V`, :math:`W`) time series and phase-plane its nullclines 
    can be seen in the figure below. 

    The model with its default parameters exhibits FitzHugh-Nagumo like dynamics.

    +---------------------------+
    |  EXCITABLE CONFIGURATION  |
    +--------------+------------+
    |Parameter     |  Value     |
    +==============+============+
    | a            |     -2.0   |
    +--------------+------------+
    | b            |    -10.0   |
    +--------------+------------+
    | c            |      0.0   |
    +--------------+------------+
    | d            |      0.02  |
    +--------------+------------+
    | I            |      0.0   |
    +--------------+------------+
    | * limit cylce if a = 2.0  |
    +---------------------------+
    
    +---------------------------+
    |   BISTABLE CONFIGURATION  |
    +--------------+------------+
    |Parameter     |  Value     |
    +==============+============+
    | a            |      1.0   |
    +--------------+------------+
    | b            |      0.0   |
    +--------------+------------+
    | c            |     -5.0   |
    +--------------+------------+
    | d            |      0.02  |
    +--------------+------------+
    | I            |      0.0   |
    +--------------+------------+
    |* monostable regime:       |
    |* fixed point if Iext=-2.0 |
    |* limit cylce if Iext=-1.0 |
    +---------------------------+
    
    +---------------------------+
    |  EXCITABLE CONFIGURATION  |
    |  (similar to Morris-Lecar)|
    +--------------+------------+
    |Parameter     |  Value     |
    +==============+============+
    | a            |      0.5   |
    +--------------+------------+
    | b            |      0.6   |
    +--------------+------------+
    | c            |     -4.0   |
    +--------------+------------+
    | d            |      0.02  |
    +--------------+------------+
    | I            |      0.0   |
    +--------------+------------+
    |* excitable regime if b=0.6|
    |* oscillatory if b=0.4     |
    +---------------------------+
    
    
    +---------------------------+     
    |  SanzLeonetAl  2013       | 
    +--------------+------------+
    |Parameter     |  Value     |
    +==============+============+
    | a            |    - 0.5   |
    +--------------+------------+
    | b            |    -10.0   |
    +--------------+------------+
    | c            |      0.0   |
    +--------------+------------+
    | d            |      0.02  |
    +--------------+------------+
    | I            |      0.0   |
    +--------------+------------+
    |* excitable regime if      |
    |* intrinsic frequency is   |
    |  approx 10 Hz             |
    +---------------------------+

    .. figure :: img/Generic2dOscillator_01_mode_0_pplane.svg
    .. _phase-plane-Generic2D:
        :alt: Phase plane of the generic 2D population model with (V, W)

        The (:math:`V`, :math:`W`) phase-plane for the generic 2D population 
        model for default parameters. The dynamical system has an equilibrium 
        point.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Generic2dOscillator.__init__
    .. automethod:: Generic2dOscillator.dfun

    """

    _ui_name = "Generic 2d Oscillator"
    ui_configurable_parameters = ['tau', 'a', 'b', 'c', 'I']

    #Define traited attributes for this model, these represent possible kwargs.
    tau = arrays.FloatArray(
        label=r":math:`\tau`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=1.0, hi=5.0, step=0.01),
        doc="""A time-scale hierarchy can be introduced for the state
        variables :math:`V` and :math:`W`. Default parameter is 1, which means
        no time-scale hierarchy.""",
        order=1)

    I = arrays.FloatArray(
        label=":math:`I_{ext}`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=-2.0, hi=2.0, step=0.01),
        doc="""Baseline shift of the cubic nullcline""",
        order=2)

    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([-2.0]),
        range=basic.Range(lo=-5.0, hi=5.0, step=0.01),
        doc="""Vertical shift of the configurable nullcline""",
        order=3)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([-10.0]),
        range=basic.Range(lo=-20.0, hi=15.0, step=0.01),
        doc="""Linear slope of the configurable nullcline""",
        order=4)

    c = arrays.FloatArray(
        label=":math:`c`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=-10.0, hi=10.0, step=0.01),
        doc="""Parabolic term of the configurable nullcline""",
        order=5)

    d = arrays.FloatArray(
        label=":math:`d`",
        default=numpy.array([0.02]),
        range=basic.Range(lo=0.0001, hi=1.0, step=0.0001),
        doc="""Temporal scale factor. Warning: do not use it unless
        you know what you are doing and know about time tides.""",
        order=-1)

    e = arrays.FloatArray(
        label=":math:`e`",
        default=numpy.array([3.0]),
        range=basic.Range(lo=-5.0, hi=5.0, step=0.0001),
        doc="""Coefficient of the quadratic term of the cubic nullcline.""",
        order=-1)

    f = arrays.FloatArray(
        label=":math:`f`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=-5.0, hi=5.0, step=0.0001),
        doc="""Coefficient of the cubic term of the cubic nullcline.""",
        order=-1)

    g = arrays.FloatArray(
        label=":math:`f`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=-5.0, hi=5.0, step=0.5),
        doc="""Coefficient of the linear term of the cubic nullcline.""",
        order=-1)

    alpha = arrays.FloatArray(
        label=r":math:`\alpha`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=-5.0, hi=5.0, step=0.0001),
        doc="""Constant parameter to scale the rate of feedback from the
            slow variable to the fast variable.""",
        order=-1)

    beta = arrays.FloatArray(
        label=r":math:`\beta`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=-5.0, hi=5.0, step=0.0001),
        doc="""Constant parameter to scale the rate of feedback from the
            slow variable to itself""",
        order=-1)

    #Informational attribute, used for phase-plane and initial()
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"V": numpy.array([-2.0, 4.0]),
                 "W": numpy.array([-6.0, 6.0])},
        doc="""The values for each state-variable should be set to encompass
            the expected dynamic range of that state-variable for the current 
            parameters, it is used as a mechanism for bounding random initial 
            conditions when the simulation isn't started from an explicit
            history, it is also provides the default range of phase-plane plots.""",
        order=6)

    #    variables_of_interest = arrays.IntegerArray(
    #        label = "Variables watched by Monitors.",
    #        range = basic.Range(lo = 0.0, hi = 2.0, step = 1.0),
    #        default = numpy.array([0], dtype=numpy.int32),
    #        doc = """This represents the default state-variables of this Model to be
    #        monitored. It can be overridden for each Monitor if desired. The
    #        corresponding state-variable indices for this model are :math:`V = 0`
    #        and :math:`W = 1`""",
    #        order = 7)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["V", "W"],
        default=["V", ],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
                                        monitored. It can be overridden for each Monitor if desired. The 
                                        corresponding state-variable indices for this model are :math:`V = 0`
                                        and :math:`W = 1`.""",
        order=7)


    def __init__(self, **kwargs):
        """
        May need to put kwargs back if we can't get them from trait...

        """

        LOG.info("%s: initing..." % str(self))

        super(Generic2dOscillator, self).__init__(**kwargs)

        #self._state_variables = ["V", "W"]
        self._nvar = 2
        self.cvar = numpy.array([0], dtype=numpy.int32)

        LOG.debug("%s: inited." % repr(self))


    def dfun(self, state_variables, coupling, local_coupling=0.0,
             ev=numexpr.evaluate):
        r"""
        The two state variables :math:`V` and :math:`W` are typically considered 
        to represent a function of the neuron's membrane potential, such as the 
        firing rate or dendritic currents, and a recovery variable, respectively. 
        If there is a time scale hierarchy, then typically :math:`V` is faster 
        than :math:`W` corresponding to a value of :math:`\tau` greater than 1.

        #TODO: update equations

        The equations of the generic 2D population model read

        .. math::
            \dot{V} &= \tau (\alpha W - V^3 +3 V^2 + I) \\
            \dot{W} &= (a\, + b\, V + c\, V^2 - \, beta W) / \tau

        where external currents :math:`I` provide the entry point for local, 
        long-range connectivity and stimulation.

        """

        V = state_variables[0, :]
        W = state_variables[1, :]

        #[State_variables, nodes]
        c_0 = coupling[0, :]

        tau = self.tau
        I = self.I
        a = self.a
        b = self.b
        c = self.c
        d = self.d
        e = self.e
        f = self.f
        g = self.g
        beta = self.beta
        alpha = self.alpha

        lc_0 = local_coupling * V


        #if not hasattr(self, 'derivative'):
        #    self.derivative = numpy.empty((2,)+V.shape)

        ## numexpr       
        dV = ev('d * tau * (alpha * W - f * V**3 + e * V**2 + g * V + I + c_0 + lc_0)')
        dW = ev('d * (a + b * V + c * V**2 - beta * W) / tau')

        ## regular ndarray operation
        ##dV = tau * (W - 0.5* V**3.0 + 3.0 * V**2 + I + c_0 + lc_0)
        ##dW = d * (a + b * V + c * V**2 - W) / tau

        self.derivative = numpy.array([dV, dW])

        return self.derivative

    device_info = model_device_info(
        pars=['tau', 'a', 'b', 'c', 'd', 'I'],
        kernel="""

        // read parameters
        float tau  = P(0)
            , a    = P(1)
            , b    = P(2)
            , c    = P(3)
            , d    = P(4)
            , I    = P(5)

        // state variables
            , v    = X(0)
            , w    = X(1)

        // aux variables
            , c_0  = I(0)   ;

        // derivatives
        DX(0) = d * (tau * (w - v*v*v + 3.0*v*v + I + c_0));
        DX(1) = d * ((a + b*v + c*v*v - w) / tau);
        """
    )


class LarterBreakspear(Model):
    """
    A modified Morris-Lecar model that includes a third equation which simulates
    the effect of a population of inhibitory interneurons synapsing on
    the pyramidal cells.
    
    .. [Larteretal_1999] Larter et.al. *A coupled ordinary differential equation
        lattice model for the simulation of epileptic seizures.* Chaos. 9(3):
        795, 1999.
    
    .. [Breaksetal_2003_a] Breakspear, M.; Terry, J. R. & Friston, K. J.  *Modulation of excitatory
        synaptic coupling facilitates synchronization and complex dynamics in an
        onlinear model of neuronal dynamics*. Neurocomputing 52–54 (2003).151–158

    .. [Breaksetal_2003_b] M. J. Breakspear et.al. *Modulation of excitatory 
        synaptic coupling facilitates synchronization and complex dynamics in a
        biophysical model of neuronal dynamics.* Network: Computation in Neural
        Systems 14: 703-732, 2003.

    .. [Honeyetal_2007] Honey, C.; Kötter, R.; Breakspear, M. & Sporns, O. * Network structure of
        cerebral cortex shapes functional connectivity on multiple time scales*. (2007)
        PNAS, 104, 10240

    .. [Honeyetal_2009] Honey, C. J.; Sporns, O.; Cammoun, L.; Gigandet, X.; Thiran, J. P.; Meuli,
        R. & Hagmann, P. *Predicting human resting-state functional connectivity
        from structural connectivity.* (2009), PNAS, 106, 2035-2040

    .. [Alstottetal_2009] Alstott, J.; Breakspear, M.; Hagmann, P.; Cammoun, L. & Sporns, O.
        *Modeling the impact of lesions in the human brain*. (2009)),  PLoS Comput Biol, 5, e1000408

    Equations and default parameters are taken from [Breaksetal_2003_b]_. 
    All equations and parameters are non-dimensional and normalized.
    For values of d_v  < 0.55, the dynamics of a single column settles onto a 
    solitary fixed point attractor.


    Parameters used for simulations in [Breaksetal_2003_a]_ Table 1. Page 153.
    Two nodes were coupled. C=0.1

    +---------------------------+
    |          Table 1          | 
    +--------------+------------+
    |Parameter     |  Value     |
    +--------------+------------+
    | I            |      0.3   |
    | a_ee         |      0.4   |
    | a_ei         |      0.1   |
    | a_ie         |      1.0   |
    | a_ne         |      1.0   |
    | a_ni         |      0.4   |
    | r_NMDA       |      0.2   |
    | delta        |      0.001 |
    +---------------------------+
    |   Breakspear et al. 2003  |
    +---------------------------+


    +---------------------------+
    |          Table 2          | 
    +--------------+------------+
    |Parameter     |  Value     |
    +--------------+------------+
    | gK           |      2.0   |
    | gL           |      0.5   |
    | gNa          |      6.7   |
    | gCa          |      1.0   |
    | a_ne         |      1.0   |
    | a_ni         |      0.4   |
    | a_ee         |      0.36  |
    | a_ei         |      2.0   |
    | a_ie         |      2.0   |
    | VK           |     -0.7   |
    | VL           |     -0.5   |
    | VNa          |      0.53  |
    | VCa          |      1.0   |
    | phi          |      0.7   | 
    | b            |      0.1   |
    | I            |      0.3   |
    | r_NMDA       |      0.25  |
    | C            |      0.1   |
    | TCa          |     -0.01  |
    | d_Ca         |      0.15  |
    | TK           |      0.0   |
    | d_K          |      0.3   |
    | VT           |      0.0   |
    | ZT           |      0.0   |
    | TNa          |      0.3   |
    | d_Na         |      0.15  |
    | d_V          |      0.65  |
    | d_Z          |      d_V   |
    | QV_max       |      1.0   |
    | QZ_max       |      1.0   |
    +---------------------------+
    |   Alstott et al. 2009     |
    +---------------------------+


    NOTES about parameters

    d_V
    For d_V < 0.55, uncoupled network, the system exhibits fixed point dynamics; 
    for 55 < lb.d_V < 0.59, limit cycle atractors; 
    and for d_V > 0.59 chaotic attractors (eg, d_V=0.6,aee=0.5,aie=0.5, gNa=0, Iext=0.165)

    d_Z
    this parameter might be spatialized: ones(N,1).*0.65 + modn*(rand(N,1)-0.5);

    C
    The long-range coupling 'C' is ‘weak’ in the sense that 
    they investigated parameter values for which C < a_ee and C << a_ie.


    
    .. figure :: img/LarterBreakspear_01_mode_0_pplane.svg
            :alt: Larter-Breaskpear phase plane (V, W)
            
            The (:math:`V`, :math:`W`) phase-plane for the Larter-Breakspear model.
    
    .. automethod:: LarterBreakspear.__init__
    
    """
    
    _ui_name = "Larter-Breakspear"
    ui_configurable_parameters = ['gCa', 'gK', 'gL', 'phi', 'gNa', 'TK', 'TCa',
                                  'TNa', 'VCa', 'VK', 'VL', 'VNa', 'd_K', 'tau_K',
                                  'd_Na', 'd_Ca', 'aei', 'aie', 'b', 'C', 'ane',
                                  'ani', 'aee', 'Iext', 'rNMDA', 'VT', 'd_V', 'ZT',
                                  'd_Z', 'QV_max', 'QZ_max']
    
    #Define traited attributes for this model, these represent possible kwargs.
    gCa = arrays.FloatArray(
        label = ":math:`g_{Ca}`",
        default = numpy.array([1.1]),
        range = basic.Range(lo = 0.9, hi = 1.5, step = 0.1),
        doc = """Conductance of population of Ca++ channels.""")
    
    gK = arrays.FloatArray(
        label = ":math:`g_{K}`",
        default = numpy.array([2.0]),
        range = basic.Range(lo = 1.95, hi= 2.05, step = 0.025),
        doc = """Conductance of population of K channels.""")
    
    gL = arrays.FloatArray(
        label = ":math:`g_{L}`",
        default = numpy.array([0.5]),
        range = basic.Range(lo = 0.45 , hi = 0.55, step = 0.05),
        doc = """Conductance of population of leak channels.""")
    
    phi = arrays.FloatArray(
        label = r":math:`\phi`",
        default = numpy.array([0.7]),
        range = basic.Range(lo = 0.3, hi = 0.9, step = 0.1),
        doc = """Temperature scaling factor.""")
    
    gNa = arrays.FloatArray(
        label = ":math:`g_{Na}`",
        default = numpy.array([6.7]),
        range = basic.Range(lo = 0.0, hi = 10.0, step = 0.1),
        doc = """Conductance of population of Na channels.""")
    
    TK = arrays.FloatArray(
        label = ":math:`T_{K}`",
        default = numpy.array([0.0]),
        range = basic.Range(lo = 0.0, hi = 0.0001, step = 0.00001),
        doc = """Threshold value for K channels.""")
    
    TCa = arrays.FloatArray(
        label = ":math:`T_{Ca}`",
        default = numpy.array([-0.01]),
        range = basic.Range(lo = -0.02, hi=-0.01, step = 0.0025),
        doc = "Threshold value for Ca channels.")
    
    TNa = arrays.FloatArray(
        label = ":math:`T_{Na}`",
        default = numpy.array([0.3]),
        range = basic.Range(lo = 0.25, hi= 0.3, step = 0.025),
        doc = "Threshold value for Na channels.")
    
    VCa = arrays.FloatArray(
        label = ":math:`V_{Ca}`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = 0.9, hi = 1.1, step = 0.05),
        doc = """Ca Nernst potential.""")
    
    VK = arrays.FloatArray(
        label = ":math:`V_{K}`",
        default = numpy.array([-0.7]),
        range = basic.Range(lo = -0.8, hi = 1., step = 0.1),
        doc = """K Nernst potential.""")
    
    VL = arrays.FloatArray(
        label = ":math:`V_{L}`",
        default = numpy.array([-0.5]),
        range = basic.Range(lo = -0.7, hi = -0.4, step = 0.1),
        doc = """Nernst potential leak channels.""")
    
    VNa = arrays.FloatArray(
        label = ":math:`V_{Na}`",
        default = numpy.array([0.53]),
        range = basic.Range(lo = 0.51, hi = 0.55, step = 0.01),
        doc = """Na Nernst potential.""")
    
    d_K = arrays.FloatArray(
        label = r":math:`\delta_{K}`",
        default = numpy.array([0.3]),
        range = basic.Range(lo = 0.1, hi = 0.4, step = 0.1),
        doc = """Variance of K channel threshold.""")
    
    tau_K = arrays.FloatArray(
        label = r":math:`\tau_{K}`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = 0.01, hi = 0.0, step = 0.1),
        doc = """Time constant for K relaxation time (ms)""")
    
    d_Na = arrays.FloatArray(
        label = r":math:`\delta_{Na}`",
        default = numpy.array([0.15]),
        range = basic.Range(lo = 0.1, hi = 0.2, step = 0.05),
        doc = "Variance of Na channel threshold.")
    
    d_Ca = arrays.FloatArray(
        label = r":math:`\delta_{Ca}`",
        default = numpy.array([0.15]),
        range = basic.Range(lo = 05.1, hi = 0.2, step = 0.05),
        doc = "Variance of Ca channel threshold.")
    
    aei = arrays.FloatArray(
        label = ":math:`a_{ei}`",
        default = numpy.array([2.0]),
        range = basic.Range(lo = 0.1, hi = 2.0, step = 0.1),
        doc = """Excitatory-to-inhibitory synaptic strength.""")
    
    aie = arrays.FloatArray(
        label = ":math:`a_{ie}`",
        default = numpy.array([2.0]),
        range = basic.Range(lo = 0.5, hi = 2.0, step = 0.1),
        doc = """Inhibitory-to-excitatory synaptic strength.""")
    
    b = arrays.FloatArray(
        label = ":math:`b`",
        default = numpy.array([0.1]),
        range = basic.Range(lo = 0.0001, hi = 1.0, step = 0.0001),
        doc = """Time constant scaling factor. The original value is 0.1""")
    
    C = arrays.FloatArray(
        label = ":math:`C`",    
        default = numpy.array([0.1]),
        range = basic.Range(lo = 0.0, hi = 0.2, step = 0.01),
        doc = """Strength of excitatory coupling. Balance between internal and
        local (and global) coupling strength. C > 0 introduces interdependences between 
        consecutive columns/nodes. C=1 corresponds to maximum coupling.
        This strenght should be set to sensible values when a whole network is connected. """)
    
    ane = arrays.FloatArray(
        label = ":math:`a_{ne}`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = 0.4, hi = 1.0, step = 0.05),
        doc = """Non-specific-to-excitatory synaptic strength.""")
    
    ani = arrays.FloatArray(
        label = ":math:`a_{ni}`",
        default = numpy.array([0.4]),
        range = basic.Range(lo = 0.3, hi = 0.5, step = 0.05),
        doc = """Non-specific-to-inhibitory synaptic strength.""")
    
    aee = arrays.FloatArray(
        label = ":math:`a_{ee}`",
        default = numpy.array([0.4]),
        range = basic.Range(lo = 0.4, hi = 0.6, step = 0.05),
        doc = """Excitatory-to-excitatory synaptic strength.""")
    
    Iext = arrays.FloatArray(
       label = ":math:`I_{ext}`",
       default = numpy.array([0.3]),
       range = basic.Range(lo = 0.165, hi = 0.3, step = 0.005),
       doc = """Subcortical input strength. It represents a non-specific
       excitation or thalamic inputs.""")
    
    rNMDA = arrays.FloatArray(
        label = ":math:`r_{NMDA}`",
        default = numpy.array([0.25]),
        range = basic.Range(lo = 0.2, hi = 0.3, step = 0.05),
        doc = """Ratio of NMDA to AMPA receptors.""")
    
    VT = arrays.FloatArray(
        label = ":math:`V_{T}`",
        default = numpy.array([0.0]),
        range = basic.Range(lo = 0.0, hi = 0.7, step = 0.01),
        doc = """Threshold potential (mean) for excitatory neurons. 
        In [Breaksetal_2003_b]_ this values is 0.""")
    
    d_V = arrays.FloatArray(
        label = r":math:`\delta_{V}`",
        default = numpy.array([0.65]),
        range = basic.Range(lo = 0.49, hi = 0.7, step = 0.01),
        doc = """Variance of the excitatory threshold. It is one of the main
        parameters explored in [Breaksetal_2003_b]_.""")
    
    ZT = arrays.FloatArray(
        label = ":math:`Z_{T}`",
        default = numpy.array([0.0]),
        range = basic.Range(lo = 0.0, hi = 0.1, step = 0.005),
        doc = """Threshold potential (mean) for inihibtory neurons.""")
    
    d_Z = arrays.FloatArray(
        label = r":math:`\delta_{Z}`",
        default = numpy.array([0.7]),
        range = basic.Range(lo = 0.001, hi = 0.75, step = 0.05),
        doc = """Variance of the inhibitory threshold.""")
        
    # NOTE: the values were not in the article. 
    QV_max = arrays.FloatArray(
        label = ":math:`Q_{max}`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = 0.1, hi = 1., step = 0.001),
        doc = """Maximal firing rate for excitatory populations (kHz)""")

    QZ_max = arrays.FloatArray(
        label = ":math:`Q_{max}`",
        default = numpy.array([1.0]),
        range = basic.Range(lo = 0.1, hi = 1., step = 0.001),
        doc = """Maximal firing rate for excitatory populations (kHz)""")


    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["V", "W", "Z"],
        default=["V"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
        monitored. It can be overridden for each Monitor if desired.""",
        order=10)
    
    #Informational attribute, used for phase-plane and initial()
    state_variable_range = basic.Dict(
        label = "State Variable ranges [lo, hi]",
        default = {"V": numpy.array([-0.5, 0.5]),
                   "W": numpy.array([-0.5, 0.5]),
                   "Z": numpy.array([-0.5, 0.5])},
        doc = """The values for each state-variable should be set to encompass
            the expected dynamic range of that state-variable for the current 
            parameters, it is used as a mechanism for bounding random inital 
            conditions when the simulation isn't started from an explicit
            history, it is also provides the default range of phase-plane plots.""")
    
    
    def __init__(self, **kwargs):
        """
        .. May need to put kwargs back if we can't get them from trait...
        
        """
        
        LOG.info('%s: initing...' % str(self))
        
        super(LarterBreakspear, self).__init__(**kwargs)
        
        self._state_variables = ["V", "W", "Z"]
        
        self._nvar = 3
        self.cvar = numpy.array([0], dtype=numpy.int32)
        
        LOG.debug('%s: inited.' % repr(self))
    
    
    def dfun(self, state_variables, coupling, local_coupling=0.0):
        """
        .. math::
             \\dot{V} &= - (g_{Ca} + (1 - C) \\, r_{NMDA} \\, a_{ee} Q_V^i +
            C \\, r_{NMDA} \\, a_{ee} \\langle Q_V \\rangle) \\, m_{Ca} \\,(V - V_{Ca})
            - g_K\\, W\\, (V - V_K) - g_L\\, (V - V_L)
            - (g_{Na} m_{Na} + (1 - C) \\, a_{ee} Q_V^i + 
            C \\, a_{ee} \\langle Q_V \\rangle) \\, (V - V_{Na})
            - a_{ie}\\, Z \\, Q_Z^i + a_{ne} \\, I_{\\delta}
            
            \\dot{W} &= \\frac{\\phi \\, (m_K - W)}{\\tau_K} \\\\
            \\dot{Z} &= b \\, (a_{ni} \\, I_{\\delta} + a_{ei} \\, V \\, Q_V)\\\\
            
            m_{ion}(X) &= 0.5 \\, (1 + tanh(\\frac{V-T_{ion}}{\\delta_{ion}})
            
        See Equations (7), (3), (6) and (2) respectively in [Breaksetal_2003]_.
        Pag: 705-706
        
        """
        V = state_variables[0, :]
        W = state_variables[1, :]
        Z = state_variables[2, :]

        c_0   = coupling[0, :]    
        lc_0  = local_coupling
        
        # relationship between membrane voltage and channel conductance
        m_Ca = 0.5 * (1 + numpy.tanh((V - self.TCa) / self.d_Ca))
        m_Na = 0.5 * (1 + numpy.tanh((V - self.TNa) / self.d_Na))
        m_K  = 0.5 * (1 + numpy.tanh((V - self.TK )  / self.d_K))
        
        # voltage to firing rate
        QV  = 0.5 * self.QV_max * (1 + numpy.tanh((V - self.VT) / self.d_V))
        QZ  = 0.5 * self.QZ_max * (1 + numpy.tanh((Z - self.ZT) / self.d_Z))
        
        dV = (- (self.gCa + (1.0 - self.C) * self.rNMDA * self.aee * QV + self.C * self.rNMDA * self.aee * c_0) * m_Ca * (V - self.VCa) - self.gK * W * (V - self.VK) -  self.gL * (V - self.VL) - (self.gNa * m_Na + (1.0 - self.C) * self.aee * QV + self.C * self.aee * c_0) * (V - self.VNa) - self.aei * Z * QZ + self.ane * self.Iext)

        dW = (self.phi * (m_K - W) / self.tau_K)
        
        dZ = (self.b * (self.ani * self.Iext + self.aei * V * QV))
        
        derivative = numpy.array([dV, dW, dZ])
        
        return derivative


class ReducedWongWang(Model):
    """
    .. [WW_2006] Kong-Fatt Wong and Xiao-Jing Wang,  *A Recurrent Network 
                Mechanism of Time Integration in Perceptual Decisions*. 
                Journal of Neuroscience 26(4), 1314-1328, 2006.

    .. [DPA_2013] Deco Gustavo, Ponce Alvarez Adrian, Dante Mantini, Gian Luca
                  Romani, Patric Hagmann and Maurizio Corbetta. *Resting-State
                  Functional Connectivity Emerges from Structurally and
                  Dynamically Shaped Slow Linear Fluctuations*. The Journal of
                  Neuroscience 32(27), 11239-11252, 2013.



    .. automethod:: ReducedWongWang.__init__

    """
    _ui_name = "Reduced Wong-Wang"

    #Define traited attributes for this model, these represent possible kwargs.
    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([0.270, ]),
        range=basic.Range(lo=0.0, hi=0.270),
        doc=""" [nC]^{-1}. Parameter chosen to ﬁt numerical solutions.""",
        order=1)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([0.108, ]),
        range=basic.Range(lo=0.0, hi=1.0),
        doc="""[kHz]. Parameter chosen to ﬁt numerical solutions.""",
        order=2)

    d = arrays.FloatArray(
        label=":math:`d`",
        default=numpy.array([154., ]),
        range=basic.Range(lo=0.0, hi=200.0),
        doc="""[ms]. Parameter chosen to ﬁt numerical solutions.""",
        order=3)

    gamma = arrays.FloatArray(
        label=r":math:`\gamma`",
        default=numpy.array([0.641, ]),
        range=basic.Range(lo=0.0, hi=1.0),
        doc="""Kinetic parameter""",
        order=4)

    tau_s = arrays.FloatArray(
        label=r":math:`\tau_S`",
        default=numpy.array([100., ]),
        range=basic.Range(lo=50.0, hi=150.0),
        doc="""Kinetic parameter. NMDA decay time constant.""",
        order=5)

    w = arrays.FloatArray(
        label=r":math:`w`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.1),
        doc="""Excitatory recurrence""",
        order=6)

    J_N = arrays.FloatArray(
        label=r":math:`J_{N}`",
        default=numpy.array([0.2609, ]),
        range=basic.Range(lo=0.2609, hi=0.5, step=0.01),
        doc="""Excitatory recurrence""",
        order=7)

    I_o = arrays.FloatArray(
        label=":math:`I_{o}`",
        default=numpy.array([0.33, ]),
        range=basic.Range(lo=0.0, hi=1.0),
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

    #    variables_of_interest = arrays.IntegerArray(
    #        label="Variables watched by Monitors",
    #        range=basic.Range(lo=0.0, hi=1.0, step=1.0),
    #        default=numpy.array([0], dtype=numpy.int32),
    #        doc="default state variables to be monitored",
    #        order=10)


    def __init__(self, **kwargs):
        """
        .. May need to put kwargs back if we can't get them from trait...

        """

        #LOG.info('%s: initing...' % str(self))

        super(ReducedWongWang, self).__init__(**kwargs)

        #self._state_variables = ["S1"]
        self._nvar = 1
        self.cvar = numpy.array([0], dtype=numpy.int32)

        LOG.debug('%s: inited.' % repr(self))

    def configure(self):
        """  """
        super(ReducedWongWang, self).configure()
        self.update_derived_parameters()


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""
        Equations taken from [DPA_2013]_ , page 11242

        ..math:: 
                \frac{dS}{dt} &= -\frac{S}{\tau_s} + (1- S) \, H \, \gamma
                H(x) &= \frac{ax - b}{1 - \exp(-d(ax -b))}
                x &= wJ_{N}S + I_o + J_N c_0 + J_N lc_0 

        """

        S   = state_variables[0, :]
        S[S<0] = 0.
        S[S>1] = 1.
        c_0 = coupling[0, :]

        
        # if applicable
        lc_0 = local_coupling * S

        x  = self.w * self.J_N * S + self.I_o + self.J_N * c_0 + self.J_N * lc_0
        H = ((self.a * x ) - self.b) / (1 - numpy.exp(-self.d * ((self.a *x)- self.b)))
        dS = - (S / self.tau_s) + (1 - S) * H * self.gamma

        derivative = numpy.array([dS])
        return derivative



class Kuramoto(Model):
    """
    The Kuramoto model is a model of synchronization phenomena derived by
    Yoshiki Kuramoto in 1975 which has since been applied to diverse domains
    including the study of neuronal oscillations and synchronization.

    See:

        .. [YK_1975] Y. Kuramoto, in: H. Arakai (Ed.), International Symposium
            on Mathematical Problems in Theoretical Physics, *Lecture Notes in
            Physics*, page 420, vol. 39, 1975.

        .. [SS_2000] S. H. Strogatz. *From Kuramoto to Crawford: exploring the
            onset of synchronization in populations of coupled oscillators*.
            Physica D, 143, 2000.

        .. [JC_2011] J. Cabral, E. Hugues, O. Sporns, G. Deco. *Role of local
            network oscillations in resting-state functional connectivity*.
            NeuroImage, 57, 1, 2011.

    """

    _ui_name = "Kuramoto Oscillator"
    ui_configurable_parameters = ['omega']

    #Define traited attributes for this model, these represent possible kwargs.
    omega = arrays.FloatArray(
        label=r":math:`\omega`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.01, hi=200.0, step=0.1),
        doc=""":math:`\omega` sets the base line frequency for the
            Kuramoto oscillator""",
        order=1)

    #Informational attribute, used for phase-plane and initial()
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"theta": numpy.array([0.0, numpy.pi * 2.0]),
        },
        doc="""The values for each state-variable should be set to encompass
            the expected dynamic range of that state-variable for the current 
            parameters, it is used as a mechanism for bounding random initial 
            conditions when the simulation isn't started from an explicit
            history, it is also provides the default range of phase-plane plots.""",
        order=6)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["theta"],
        default=["theta"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
                            monitored. It can be overridden for each Monitor if desired. The Kuramoto
                            model, however, only has one state variable with and index of 0, so it
                            is not necessary to change the default here.""",
        order=7)

    #    variables_of_interest = arrays.IntegerArray(
    #        label = "Variables watched by Monitors.",
    #        default = numpy.array([0], dtype=numpy.int32),
    #        doc = """This represents the default state-variables of this Model to be
    #        monitored. It can be overridden for each Monitor if desired. The Kuramoto
    #        model, however, only has one state variable with and index of 0, so it
    #        is not necessary to change the default here.""",
    #        order = 7)


    def __init__(self, **kwargs):
        """
        May need to put kwargs back if we can't get them from trait...

        """

        LOG.info("%s: initing..." % str(self))

        super(Kuramoto, self).__init__(**kwargs)

        #self._state_variables = ["theta"]
        self._nvar = 1
        self.cvar = numpy.array([0], dtype=numpy.int32)

        LOG.debug("%s: inited." % repr(self))


    def dfun(self, state_variables, coupling, local_coupling=0.0,
             ev=numexpr.evaluate, sin=numpy.sin, pi2=numpy.pi * 2):
        r"""
        The :math:`\theta` variable is the phase angle of the oscillation.

        .. math::
            \dot{\theta} = \omega + I

        where :math:`I` is the input via local and long range connectivity, 
        passing first through the Kuramoto coupling function, 
        :py:class:tvb.simulator.coupling.Kuramoto.

        """

        # reset if over 2*pi
        state_variables[state_variables > pi2] -= pi2

        theta = state_variables[0, :]


        #                   TODO CHECKME FIXME ME ME
        I = coupling[0, :] + sin(local_coupling * theta)

        if not hasattr(self, 'derivative'):
            self.derivative = numpy.empty((1,) + theta.shape)

        # phase update 
        self.derivative[0] = self.omega + I

        # all this pi makeh me have great hungary, can has sum NaN?
        return self.derivative

    device_info = model_device_info(
        pars=['omega'],
        kernel="""
        float omega = P(0)
            , theta = X(0)
            , c_0 = I(0) ; 

                    // update state array
        if (theta>(2*PI)) X(0)-= 2*PI;

        DX(0) = omega + c_0;

        """
    )


class BreakspearRobinsonRennieWright(Model):
    """

    A reduced version of a corticothalamic neural field model [Robinson_1997]_ as 
    but without the second order derivative (Laplacian) [Robinson_2002]_ [Breakspear_2005]_ [Freyer_2011]_

    The model describes the interaction of 4 neural populations:
      + cortical pyramidal cells
      + cortical inhibitory cells
      + thalamic specific nucleus cells
      + thalamic reticular nucleaus cells


    Cross check with:
    https://github.com/stuart-knock/BrainNetworkModels/blob/master/BRRW_heun.m



    **References**:
    
        .. [Robinson_2002]
    
        .. [Robinson_1997]

        .. [Breakspear_2005]

        .. [Wilson]

        .. [LopesDaSilva]

        .. [Freyer_2011]

        .. [Freyer_2009]

        .. [Freyer_2012_Model] Freyer, F.; Reinacher, M.; Nolte, G.; Dinse, H. R. and
                                Ritter, P. *Repetitive tactile stimulation changes resting-state
                                functional connectivity-implications for treatment of sensorimotor decline*.
                                Front Hum Neurosci, Bernstein Focus State Dependencies of Learning and
                                Bernstein Center for Computational Neuroscience Berlin, Germany., 2012, 6, 144
    
    Equations and default parameters are taken from [Freyer_2011]_.


    
    .. figure :: img/BreakspearRobinsonRennieWright_01_mode_0_pplane.svg
            :alt: Robinson phase plane (V, W)
            
            The (:math:`V`, :math:`W`) phase-plane for the Robinson model.
    
    .. automethod:: BreakspearRobinsonRennieWright.__init__
    .. automethod:: BreakspearRobinsonRennieWright.dfun
    .. automethod:: BreakspearRobinsonRennieWright.sigma_fun

    """
    
    _ui_name = "Breakspear-Robinson-Rennie-Wright"
    ui_configurable_parameters = ['Q_max', 'theta', 'sigma', 'gamma_e', 'alpha',
                                  'beta', 't_0', 'nu_ee', 'nu_ie', 'nu_ei', 'nu_ii',
                                  'nu_es', 'nu_is', 'nu_se', 'nu_sr', 'nu_sn', 'nu_re',
                                  'nu_rs', 'nu_ss', 'nu_rr', 'chi', 'sigma_n']
    
    #Define traited attributes for this model, these represent possible kwargs.
    Q_max = arrays.FloatArray(
        label = ":math:`Q_{max}`",
        default = numpy.array([0.250]),
        range = basic.Range(lo = 0.100, hi = 0.250, step = 0.01),
        doc = """Maximum firing rate [ms^-1].""")
    
    theta = arrays.FloatArray(
        label = r":math:`\theta`",
        default = numpy.array([15.]),
        range = basic.Range(lo = 14., hi= 16., step = 0.01),
        doc = """Mean neuronal threshold [mV]""")
    
    sigma = arrays.FloatArray(
        label = r":math:`\sigma`",
        default = numpy.array([6.]),
        range = basic.Range(lo = 1.0 , hi = 10., step = 1.0),
        doc = """Threshold SD [mV]""")
    
    gamma_e = arrays.FloatArray(
        label = r":math:`\gamma_e`",
        default = numpy.array([0.100]),
        range = basic.Range(lo = 0.05, hi = 0.15, step = 0.01),
        doc = """Ratio conduction velocity/mean range of axons [ms^-1]""")
    
    alpha = arrays.FloatArray(
        label = r":math:`\alpha`",
        default = numpy.array([0.06]),
        range = basic.Range(lo = 0.04, hi = 0.01, step = 0.1),
        doc = """Inverse decay time of membrane potential [ms^-1]""")
    
    beta = arrays.FloatArray(
        label = r":math:`\beta`",
        default = numpy.array([0.240]),
        range = basic.Range(lo = 0.2, hi = 0.3, step = 0.02),
        doc = """Inverse rise time of membrane potential [ms^-1]""")
    
    t_0 = arrays.FloatArray(
        label = ":math:`t_{0}`",
        default = numpy.array([80.]),
        range = basic.Range(lo = -0.02, hi=-0.01, step = 0.0025),
        doc = "Corticothalamic return time (complete return loop) [ms]")
    
    nu_ee = arrays.FloatArray(
        label = r":math:`\nu_{ee}`",
        default = numpy.array([1.06e3]),
        range = basic.Range(lo = 1.0e3, hi= 1.1e3, step = 10.),
        doc = "Excitatory-to-excitatory (cortico-cortical) synaptic strength [mVms].")
    
    nu_ie = arrays.FloatArray(
        label = r":math:`\nu_{ie}`",
        default = numpy.array([1.06e3]),
        range = basic.Range(lo = 1.0e3, hi= 1.1e3, step = 10.),
        doc = "Excitatory-to-inhibitory (cortico-cortical) synaptic strength [mVms].")
    
    nu_ei = arrays.FloatArray(
        label = r":math:`\nu_{ei}`",
        default = numpy.array([-1.8e3]),
        range = basic.Range(lo = -2.0e3, hi= -1.0e3, step = 10.),
        doc = "Inhibitory-to-excitatory (cortico-cortical) synaptic strength [mVms].")
    
    nu_ii = arrays.FloatArray(
        label = r":math:`\nu_{ii}`",
        default = numpy.array([-1.8e3]),
        range = basic.Range(lo = -2.0e3, hi= -1.0e3, step = 10.),
        doc = "Inhibitory-to-inhibitory (cortico-cortical) synaptic strength [mVms].")
    
    nu_es = arrays.FloatArray(
        label = r":math:`\nu_{es}`",
        default = numpy.array([2.2e3]),
        range = basic.Range(lo = 2.0e3, hi= 2.5e3, step = 10.),
        doc = "Specific nucleus-to-excitatory (thalamo-cortical) synaptic strength [mVms].")
    
    nu_is = arrays.FloatArray(
        label = r":math:`\nu_{is}`",
        default = numpy.array([2.2e3]),
        range = basic.Range(lo = 2.0e3, hi= 2.5e3, step = 10.),
        doc = "Specific nucleus-to-inhibitory (thalamo-cortical) synaptic strength [mVms].")

    nu_se = arrays.FloatArray(
        label = r":math:`\nu_{se}`",
        default = numpy.array([2.28e3]),
        range = basic.Range(lo = 2.2e3, hi= 2.3e3, step = 1.),
        doc = "Excitatory-to-specific nucleus (cortico-thalamic) synaptic strength [mVms].")
    
    nu_sr = arrays.FloatArray(
        label = r":math:`\nu_{sr}`",
        default = numpy.array([-0.845e3]),
        range = basic.Range(lo = -0.88e3, hi= -0.84e3, step = 0.01e3),
        doc = "Reticular-to-specific nucleus (thalamo-thalamic) synaptic strength [mVms].")
    
    nu_sn = arrays.FloatArray(
        label = r":math:`\nu_{sn}`",
        default = numpy.array([1.2e3]),
        range = basic.Range(lo = 1.1e3, hi= 1.3e3, step = 0.1e3),
        doc = "Nonspecific-to-specific nucleus synaptic strength.")
    
    nu_re = arrays.FloatArray(
        label = r":math:`\nu_{re}`",
        default = numpy.array([0.91e3]),
        range = basic.Range(lo = 0.9e3, hi= 0.92e3, step = 0.005e3),
        doc = "Excitatory-to-reticular nucleus (cortico-thalamic) synaptic strength [mVms].")
    
    nu_rs = arrays.FloatArray(
        label = r":math:`\nu_{rs}`",
        default = numpy.array([0.41e3]),
        range = basic.Range(lo = 0.4e3, hi= 0.42e3, step = 0.005e3),
        doc = "Specific nucleus-to-reticular nucleus (intra-thalamic) synaptic strength [mVms].")

    nu_ss = arrays.FloatArray(
        label = r":math:`\nu_{ss}`",
        default = numpy.array([0.0e3]),
        range = basic.Range(lo = 0.0e3, hi= 0.0e3, step = 0.001e3),
        doc = "Specific nucleus self connection (intra-thalamic) synaptic strength [mVms].")

    nu_rr = arrays.FloatArray(
        label = r":math:`\nu_{rr}`",
        default = numpy.array([0.0e3]),
        range = basic.Range(lo = 0.0e3, hi= 0.0e3, step = 0.001e3),
        doc = "Reticular nucleus self connection (intra-thalamic) synaptic strength [mVms].")
    
    chi = arrays.FloatArray(
        label = r":math:`\chi`",
        default = numpy.array([0.64]),
        range = basic.Range(lo = 0.0, hi = 1.0, step = 0.01),
        doc = r"""Ratio of multiplicative to additive noise (dimensionless). If :math:`\chi` is 0
                 then noise is only additive.""")
    
    
    sigma_n = arrays.FloatArray(
        label = r":math:`\sigma_n`",
        default = numpy.array([0.56]),
        range = basic.Range(lo = 0.0, hi = 0.2, step = 0.01),
        doc = """ SD of stochastic influence :math:`\phi_n` (fraction of the stable
                  limit cycle attractor amplitude) (dimensionless) """)


    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["phi_e", "dphi_e", "V_e", "dV_e", "V_s", "dV_s", "V_r", "dV_r"],
        default=["phi_e"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
        monitored. It can be overridden for each Monitor if desired.""",
        order=10)
    
    #Informational attribute, used for phase-plane and initial()
    state_variable_range = basic.Dict(
        label = "State Variable ranges [lo, hi]",
        default = {"phi_e" : numpy.array([ 0.0, 0.25]),
                   "dphi_e": numpy.array([-0.5, 0.5]),
                   "V_e"   : numpy.array([-0.5, 0.5]),
                   "dV_e"  : numpy.array([-0.5, 0.5]),
                   "V_s"   : numpy.array([-0.5, 0.5]),
                   "dV_s"  : numpy.array([-0.5, 0.5]),
                   "V_r"   : numpy.array([-0.5, 0.5]),
                   "dV_r"  : numpy.array([-0.5, 0.5])},
        doc = """The values for each state-variable should be set to encompass
            the expected dynamic range of that state-variable for the current 
            parameters, it is used as a mechanism for bounding random initial
            conditions when the simulation isn't started from an explicit
            history, it is also provides the default range of phase-plane plots.""")
    
    
    def __init__(self, **kwargs):
        """
        We may need to put kwargs back if we can't get them from traits.
        
        """
        
        LOG.info('%s: initing...' % str(self))
        
        super(BreakspearRobinsonRennieWright, self).__init__(**kwargs)
        
        self._state_variables = ["phi_e", "dphi_e", 
                                 "V_e", "dV_e", 
                                 "V_s", "dV_s",
                                 "V_r", "dV_r"]
        
        self._nvar = 8
        self.cvar = numpy.array([0,4], dtype=numpy.int32)
        
        LOG.debug('%s: inited.' % repr(self))
    
    
    def dfun(self, state_variables, coupling, local_coupling=0.0):
        """
        The activity in each neural population is described by three state variables: 

        * the mean soma membrane potentials :math:`V_a(x,t)` measured relative to resting;

        * the mean firing rate at the cell soma :math:`Q_a(x,t)`; and

        * the local presynaptic activity :math:`\phi_a(x,t)`


        a: (e, i, r, s, n)


        Presynaptic activity :math:`\phi_a(x,t)` couples through synaptic
        transmission to post- synaptic potentials. Therefore in this framework,
        :math:`\phi_a(x,t)` is the coupling variable.

        For stochastics simulations fluctuations the term is introduced 
        to dV_e, dV_r, dV_s and it should be white noise with 0 mean and SD = sigma_n
        and a scaling of ab * nu_sn.


        """
        phi_e  = state_variables[0, :]
        dphi_e = state_variables[1, :]
        V_e    = state_variables[2, :]
        dV_e   = state_variables[3, :]
        V_s    = state_variables[4, :]
        dV_s   = state_variables[5, :]
        V_r    = state_variables[6, :]
        dV_r   = state_variables[7, :]

        long_range_phi_e    =  coupling[0, :]
        delayed_V_s         =  coupling[1, :] 

        short_range_phi_e   = local_coupling * phi_e  

        # voltage to firing rate
        Q_e = self.sigma_fun(V_e)
        Q_s = self.sigma_fun(V_s) # Note Qs should be the delayed activity from the specific nucleus of the thalamus
        delayed_Q_s = self.sigma_fun(delayed_V_s)
        Q_r = self.sigma_fun(V_r) 

        v   = 10.**2  # NOTE: hardcode the conduction speed for short range connections
        ab  = self.alpha * self.beta
        apb = self.alpha + self.beta

        # state-variables
        d_phi_e  = (dphi_e)
        d_dphi_e = (self.gamma_e**2 * (Q_e - phi_e) - 2.* self.gamma_e * dphi_e + v * short_range_phi_e)
        d_V_e    = (dV_e)
        d_dV_e   = (ab  *        (self.nu_ee * phi_e + self.nu_ee * long_range_phi_e
                                + self.nu_ei * Q_e 
                                + self.nu_es * delayed_Q_s 
                                - V_e) - apb * dV_e)
        d_V_s  = dV_s

        d_dV_s = (ab  *          (self.nu_se * phi_e + self.nu_se * long_range_phi_e
                                + self.nu_sr * Q_r 
                                - V_s) - apb * dV_s)
        d_V_r  = dV_r
        d_dV_r = d_dV_s = (ab *  (self.nu_re * phi_e + self.nu_re * long_range_phi_e
                                + self.nu_rs * Q_s 
                                - V_r) - apb * dV_r)

        
        derivative = numpy.array([d_phi_e, d_dphi_e,
                                  d_V_e, d_dV_e,
                                  d_V_s, d_dV_s,
                                  d_V_r, d_dV_r])
        
        return derivative

    def sigma_fun(self, sv):
        """
        Neuronal activation function. This sigmoidal function 
        increases from 0 to Q_max as "sv" increases.
        sv represents a membrane potential state variable (V).

        #TODO: test performance using equations.Sigmoid dtype. 
        That's why they are implemented, right? 

        """
        #HACKERY: Hackery for exponential s that blow up. 
        # Set to inf, so the result will be effectively zero.
        magic_exp_number = 709
        temp = (-numpy.pi * (sv - self.theta) / (self.sigma * numpy.sqrt(3.)))
        temp = numpy.where(temp > magic_exp_number, numpy.inf, temp)
        sigma_v_to_q = self.Q_max / (1. + numpy.exp(temp))


        return sigma_v_to_q
    

class ContinuousHopfield(Model):
    """
    The Hopfield neural network is a discrete time dynamical system composed of multiple binary nodes,
    with a connectivity matrix built from a predetermined set of patterns. The update, inspired
    from the spin-glass model (used to describe magnetic properties of dilute alloys), is based
    on a random scanning of every node. The existence of a fixed point dynamics is guaranteed
    by a Lyapunov function. The Hopfield network is expected to have those multiple patterns as
    attractors (multistable dynamical system). When the initial conditions are close to one of
    the “learned” patterns, the dynamical system is expected to relax on the corresponding attractor.
    A possible output of the system is the final attractive state (interpreted as an associative memory).

    Various extensions of the initial model have been proposed, among which a noiseless and
    continuous version [Hopfield_1984]_ having a slightly different Lyapunov function, but essentially
    the same dynamical properties, with more straightforward physiological interpretation.
    A continuous Hopfield neural network (with a sigmoid transfer function) can indeed be interpreted
    as a network of neural masses with every node corresponding to the mean field activity of a local
    brain region, with many bridges with the Wilson Cowan model [WC_1973]_.

    **References**:

        .. [Hopfield_1982] Hopfield, J. J., *Neural networks and physical systems with emergent collective
                        computational abilities*, Proc. Nat. Acad. Sci. (USA) 79, 2554–2558, 1982.

        .. [Hopfield_1984] Hopfield, J. J., *Neurons with graded response have collective computational
                        properties like those of two-sate neurons*, Proc. Nat. Acad. Sci. (USA) 81, 3088-3092, 1984.


    See also, http://www.scholarpedia.org/article/Hopfield_network

    .. automethod:: ContinuousHopfield.__init__
    .. automethod:: ContinuousHopfield.dfun

    """

    _ui_name = "Continuous Hopfield"
    ui_configurable_parameters = ['taux']

    #Define traited attributes for this model, these represent possible kwargs.
    taux = arrays.FloatArray(
        label = r":math:`\tau_{x}`",
        default = numpy.array([1.]),
        range = basic.Range(lo = 0.01, hi = 100., step = 0.01),
        doc = """The fast time-scale for potential calculus :math:`x`, state-variable of the model.""",
        order=1)

    #Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label = "State Variable ranges [lo, hi]",
        default = {"x": numpy.array([-1., 2.])},
        doc = """The values for each state-variable should be set to encompass
            the expected dynamic range of that state-variable for the current
            parameters, it is used as a mechanism for bounding random inital
            conditions when the simulation isn't started from an explicit
            history, it is also provides the default range of phase-plane plots.""",
        order = 2)

    variables_of_interest = basic.Enumerate(
        label = "Variables watched by Monitors",
        options=["x"],
        default=["x"],
        select_multiple=True,
        doc = """The values for each state-variable should be set to encompass
            the expected dynamic range of that state-variable for the current
            parameters, it is used as a mechanism for bounding random inital
            conditions when the simulation isn't started from an explicit
            history, it is also provides the default range of phase-plane plots.""",
        #doc="""This represents the default state-variables of this Model to be
                                    #monitored. It can be overridden for each Monitor if desired. The
                                    #corresponding state-variable indices for this model are :math:`E = 0`
                                    #and :math:`I = 1`.""",
        order = 3)


    def __init__(self, **kwargs):
        """Initialize the Hopfield Based model's traited attributes, any provided as
        keywords will overide their traited default.
        """
        LOG.info("%s: initing..." % str(self))
        super(ContinuousHopfield, self).__init__(**kwargs)

        self._state_variables = ["x"]
        self._nvar = len(self._state_variables)
        self.cvar = numpy.array([0], dtype=numpy.int32)

        LOG.debug("%s: inited." % repr(self))


    def dfun(self, state_variables, coupling, local_coupling=0.0):
        """The fast, :math:`x`, and slow, :math:`\\theta`, state variables are typically
        considered to represent a membrane potentials of nodes and the global inhibition term,
        respectively:

            .. math::
                \\dot{x_{i}} &= 1 / \\tau_{x} (-x_{i} + sum(W_{i,j} * A_{j}) + \\sigma^{2}_{x} * \\eta_{i})
                A_{i} &= 1/2 * (1 + tanh(G * (P * x_{i} - \\theta_{i})))

        where :math:`\\eta` is a centered gaussian noise and :math:`\\sigma` its standard deviation.
        """

        x = state_variables[0, :]
        WAx = coupling[0]
        dx = (- x + WAx) / self.taux

        derivative = numpy.array([dx])
        return derivative

    # info for device_data
    device_info = model_device_info(

        pars=['taux'],

        kernel="""
        // read parameters
        float taux = P(0)

        // state variables
            , x = X(0)

        // aux variables
            , WAx = I(0);

        // set derivatives
        DX(0) = (-x + WAx) / taux;
        """
    )
