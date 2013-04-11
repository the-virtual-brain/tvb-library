# -*- coding: utf-8 -*-

"""
A contributed model: Larter model revisited by Breaskpear M.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

# Third party python libraries
import numpy

#The Virtual Brain
try:
    from tvb.basic.logger.builder import get_logger
    LOG = get_logger(__name__)
except ImportError:
    import logging
    LOG = logging.getLogger(__name__)

from tvb.datatypes.arrays import FloatArray, IntegerArray

from tvb.basic.traits.types_basic import Range, Dict

import tvb.simulator.models as models


class LarterBreakspear(models.Model):
    """
    A modified Morris-Lecar model that includes a third equation which simulates
    the effect of a population of inhibitory interneurons synapsing on
    the pyramidal cells.
    
    .. [Larteretal_1999] Larter et.al. *A coupled ordinary differential equation
        lattice model for the simulation of epileptic seizures.* Chaos. 9(3):
        795, 1999.
    
    .. [Breaksetal_2003] M. J. Breakspear et.al. *Modulation of excitatory 
        synaptic coupling facilitates synchronization and complex dynamics in a
        biophysical model of neuronal dynamics.* Network: Computation in Neural
        Systems 14: 703-732, 2003.
    
    Equations are taken from [Breaksetal_2003]_. All equations and parameters 
    are non-dimensional and normalized.
    
    .. figure :: img/LarterBreakspear_01_mode_0_pplane.svg
            :alt: Larter-Breaskpear phase plane (V, W)
            
            The (:math:`V`, :math:`W`) phase-plane for the Larter-Breakspear model.
    
    .. automethod:: __init__
    
    """
    
    _ui_name = "Larter-Breakspear"
    ui_configurable_parameters = ['gCa', 'gK', 'gL', 'phi', 'gNa', 'TK', 'TCa',
                                  'TNa', 'VCa', 'VK', 'VL', 'VNa', 'd_K', 'tau_K',
                                  'd_Na', 'd_Ca', 'aei', 'aie', 'b', 'c', 'ane',
                                  'ani', 'aee', 'Iext', 'rNMDA', 'VT', 'd_V', 'ZT',
                                  'd_Z', 'beta', 'Q_max']
    
    #Define traited attributes for this model, these represent possible kwargs.
    gCa = FloatArray(
        label = ":math:`g_{Ca}`",
        default = numpy.array([1.1]),
        range = Range(lo = 0.9, hi = 1.5, step = 0.1),
        doc = """Conductance of population of Ca++ channels.""")
    
    gK = FloatArray(
        label = ":math:`g_{K}`",
        default = numpy.array([2.0]),
        range = Range(lo = 1.95, hi= 2.05, step = 0.025),
        doc = """Conductance of population of K channels.""")
    
    gL = FloatArray(
        label = ":math:`g_{L}`",
        default = numpy.array([0.5]),
        range = Range(lo = 0.45 , hi = 0.55, step = 0.05),
        doc = """Conductance of population of leak channels.""")
    
    phi = FloatArray(
        label = ":math:`\\phi`",
        default = numpy.array([0.7]),
        range = Range(lo = 0.3, hi = 0.9, step = 0.1),
        doc = """Temperature scaling factor.""")
    
    gNa = FloatArray(
        label = ":math:`g_{Na}`",
        default = numpy.array([0.0]),
        range = Range(lo = 0.0, hi = 6.7, step = 0.1),
        doc = """Conductance of population of Na channels.""")
    
    TK = FloatArray(
        label = ":math:`T_{K}`",
        default = numpy.array([0.0]),
        range = Range(lo = 0.0, hi = 0.0001, step = 0.00001),
        doc = """Threshold value for K channels.""")
    
    TCa = FloatArray(
        label = ":math:`T_{Ca}`",
        default = numpy.array([-0.01]),
        range = Range(lo = -0.02, hi=-0.01, step = 0.0025),
        doc = "Threshold value for Ca channels.")
    
    TNa = FloatArray(
        label = ":math:`T_{Na}`",
        default = numpy.array([0.3]),
        range = Range(lo = 0.25, hi= 0.3, step = 0.025),
        doc = "Threshold value for Na channels.")
    
    VCa = FloatArray(
        label = ":matj:`V_{Ca}`",
        default = numpy.array([1.0]),
        range = Range(lo = 0.9, hi = 1.1, step = 0.05),
        doc = """Ca Nernst potential.""")
    
    VK = FloatArray(
        label = ":math:`V_{K}`",
        default = numpy.array([-0.7]),
        range = Range(lo = -0.8, hi = 1., step = 0.1),
        doc = """K Nernst potential.""")
    
    VL = FloatArray(
        label = ":math:`V_{L}`",
        default = numpy.array([-0.5]),
        range = Range(lo = -0.7, hi = -0.4, step = 0.1),
        doc = """Nernst potential leak channels.""")
    
    VNa = FloatArray(
        label = ":math:`V_{Na}`",
        default = numpy.array([0.53]),
        range = Range(lo = 0.51, hi = 0.55, step = 0.01),
        doc = """Na Nernst potential.""")
    
    d_K = FloatArray(
        label = ":math:`\\delta_{K}`",
        default = numpy.array([0.3]),
        range = Range(lo = 0.1, hi = 0.4, step = 0.1),
        doc = """Variance of K channel threshold.""")
    
    tau_K = FloatArray(
        label = ":math:`\\tau_{K}`",
        default = numpy.array([1.0]),
        range = Range(lo = 0.1, hi = 1.0, step = 0.1),
        doc = """Time constant for K relaxation time (ms)""")
    
    d_Na = FloatArray(
        label = ":math:`\\delta_{Na}`",
        default = numpy.array([0.15]),
        range = Range(lo = 0.1, hi = 0.2, step = 0.05),
        doc = "Variance of Na channel threshold.")
    
    d_Ca = FloatArray(
        label = ":math:`\\delta_{Ca}`",
        default = numpy.array([0.15]),
        range = Range(lo = 0.1, hi = 0.2, step = 0.05),
        doc = "Variance of Ca channel threshold.")
    
    aei = FloatArray(
        label = ":math:`a_{ei}`",
        default = numpy.array([0.1]),
        range = Range(lo = 0.1, hi = 2.0, step = 0.1),
        doc = """Excitatory-to-inhibitory synaptic strength.""")
    
    aie = FloatArray(
        label = ":math:`a_{ie}`",
        default = numpy.array([2.0]),
        range = Range(lo = 0.5, hi = 2.0, step = 0.1),
        doc = """Inhibitory-to-excitatory synaptic strength.""")
    
    b = FloatArray(
        label = ":math:`b`",
        default = numpy.array([0.01]),
        range = Range(lo = 0.0001, hi = 0.1, step = 0.0001),
        doc = """Time constant scaling factor.""")
    
    c = FloatArray(
        label = ":math:`c`",
        default = numpy.array([0.0]),
        range = Range(lo = 0.0, hi = 0.2, step = 0.05),
        doc = """Strength of excitatory coupling. Balance between internal and
        local (and global) coupling strength.""")
    
    ane = FloatArray(
        label = ":math:`a_{ne}`",
        default = numpy.array([0.4]),
        range = Range(lo = 0.4, hi = 1.0, step = 0.05),
        doc = """Non-specific-to-excitatory synaptic strength.""")
    
    ani = FloatArray(
        label = ":math:`a_{ni}`",
        default = numpy.array([0.4]),
        range = Range(lo = 0.3, hi = 0.5, step = 0.05),
        doc = """Non-specific-to-inhibitory synaptic strength.""")
    
    aee = FloatArray(
        label = ":math:`a_{ee}`",
        default = numpy.array([0.5]),
        range = Range(lo = 0.4, hi = 0.6, step = 0.05),
        doc = """Excitatory-to-excitatory synaptic strength.""")
    
    Iext = FloatArray(
       label = ":math:`I_{ext}`",
       default = numpy.array([0.165]),
       range = Range(lo = 0.165, hi = 0.3, step = 0.005),
       doc = """Subcortical input strength. It represents a non-specific
       excitation.""")
    
    rNMDA = FloatArray(
        label = ":math:`r_{NMDA}`",
        default = numpy.array([0.25]),
        range = Range(lo = 0.2, hi = 0.3, step = 0.05),
        doc = """Ratio of NMDA to AMPA receptors.""")
    
    VT = FloatArray(
        label = ":math:`V_{T}`",
        default = numpy.array([0.54]),
        range = Range(lo = 0.0, hi = 0.7, step = 0.01),
        doc = """Threshold potential (mean) for excitatory neurons.""")
    
    d_V = FloatArray(
        label = ":math:`\\delta_{V}`",
        default = numpy.array([0.65]),
        range = Range(lo = 0.1, hi = 0.7, step = 0.05),
        doc = """Variance of the excitatory threshold. It is one of the main
        parameters explored in [Breaksetal_2003]_.""")
    
    ZT = FloatArray(
        label = ":math:`Z_{T}`",
        default = numpy.array([0.0]),
        range = Range(lo = 0.0, hi = 0.1, step = 0.005),
        doc = """Threshold potential (mean) for inihibtory neurons.""")
    
    d_Z = FloatArray(
        label = ":math:`\\delta_{Z}`",
        default = numpy.array([0.7]),
        range = Range(lo = 0.001, hi = 0.75, step = 0.05),
        doc = """Variance of the inhibitory threshold.""")
    
    beta = FloatArray(
        label = ":math:`\\beta`",
        default = numpy.array([0.0]),
        range = Range(lo = 0.0, hi = 0.1, step = 0.01),
        doc = """Random modulation of subcortical input.""")
    
    # NOTE: the values were not in the article. 
    #I took these ones from DESTEXHE 2001
    Q_max = FloatArray(
        label = ":math:`Q_{max}`",
        default = numpy.array([0.001]),
        range = Range(lo = 0.001, hi = 0.005, step = 0.0001),
        doc = """Maximal firing rate for excitatory and inihibtory populations (kHz)""")
    
    variables_of_interest = IntegerArray(
        label = "Variables watched by Monitors.",
        range = Range(lo = 0, hi = 3, step=1),
        default = numpy.array([0, 2], dtype=numpy.int32),
        doc = """This represents the default state-variables of this Model to be
        monitored. It can be overridden for each Monitor if desired.""")
    
    #Informational attribute, used for phase-plane and initial()
    state_variable_range = Dict(
        label = "State Variable ranges [lo, hi]",
        default = {"V": numpy.array([-2.0, 2.0]),
                   "W": numpy.array([-10.0, 10.0]),
                   "Z": numpy.array([-3.0, 3.0])},
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
             \\dot{V} &= - (g_{Ca} + (1 - C) \\, r_{NMDA} \\, a_{ee} Q_{V}^{i} +
            C \\, r_{NMDA} \\, a_{ee} \\langle Q_V \\rangle) \\,
            m_{Ca} \\,(V - V_{Ca})
            - g_{K}\\, W\\, (V - V_{K}) - g_{L}\\, (V - V_{L})
            - (g_{Na} m_{Na} + (1 - C) \\, a_{ee} Q_{V}^{i} +
            C \\, a_{ee} \\langle Q_V \\rangle) \\, (V - V_{Na})
            + a_{ie}\\, Z \\, Q_{Z}^{i} + a_{ne} \\, I_{\\delta}
            
            \\dot{W} &= \\frac{\\phi \\, (m_{K} - W)}{\\tau_{K}} \\\\
            \\dot{Z} &= b \\, (a_{ni} \\, I_{\\delta} + a_{ei} \\, V \\, Q_{V})
            \\\\
            
            m_{ion}(X) &= 0.5 \\, (1 + tanh(\\frac{X-T_{ion}}{\\delta_{ion}})
            
        See Equations (7), (3), (6) and (2) respectively in [Breaksetal_2003]_.
        Pag: 705-706
        
        """
        V = state_variables[0, :]
        W = state_variables[1, :]
        Z = state_variables[2, :]
        
        c_0 = coupling[0, :]
        lc_0 = local_coupling
        
        m_Ca = 0.5 * (1 + numpy.tanh((V - self.TCa) / self.d_Ca))
        m_Na = 0.5 * (1 + numpy.tanh((V - self.TNa) / self.d_Na))
        m_K = 0.5 * (1 + numpy.tanh((V - self.TK) / self.d_K))
        
        Q_V = 0.5 * self.Q_max * (1 + numpy.tanh((V - self.VT) / self.d_V))
        Q_Z = 0.5 * self.Q_max * (1 + numpy.tanh((Z - self.ZT) / self.d_Z))
        
        dV = - (self.gCa + (1.0 - self.c) * self.rNMDA * self.aee * Q_V + \
        self.c * self.rNMDA * self.aee * (lc_0 * Q_V + c_0)) * m_Ca * (V - self.VCa) - \
        self.gK * W * (V - self.VK) -  self.gL * (V - self.VL) - (self.gNa * m_Na + \
        (1.0 - self.c) * self.aee * Q_V + self.c * self.aee * (lc_0 * Q_V + c_0)) *\
        (V - self.VNa) + self.aei * Z * Q_Z + self.ane * self.Iext
        
        # Single node equation
#        dV = - (self.gCa + (1.0 - self.c) * self.rNMDA * self.aee * Q_V ) *  \
#        m_Ca * (V - self.VCa) - self.gK * W * (V - self.VK) -  self.gL * \
#        (V - self.VL) + self.aei * Z * Q_Z + self.ane * self.Iext
        
        dW = self.phi * (m_K - W) / self.tau_K
        
        dZ = self.b * (self.ani * self.Iext + self.aei * V * Q_V)
        
        derivative = numpy.array([dV, dW, dZ])
        
        return derivative


if __name__ == "__main__":
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()
    
    #Initialise Models in their default state:
    LARTER_BREAKS_MODEL = LarterBreakspear()
    
    LOG.info("Model initialised in its default state without error...")
    
    LOG.info("Testing phase plane interactive ... ")
    
    from tvb.simulator.phase_plane_interactive import PhasePlaneInteractive
    import tvb.simulator.integrators
        
    INTEGRATOR = tvb.simulator.integrators.HeunDeterministic(dt=2**-5)
    ppi_fig = PhasePlaneInteractive(model=LARTER_BREAKS_MODEL, integrator=INTEGRATOR)
    ppi_fig.show()

    
    
    
