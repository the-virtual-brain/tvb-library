"""
Test the simulator module. Original: simulator_tester.py
Tests all the possible combinations of (available) models and integration 
schemes. 

By default it runs region-based simulations, but it can be configured to use
the default surface and thus it run surface-based simulations.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <sanzleon.paula@gmail.com@>

"""

#TODO: Adapt (or create an alternative test) to use the unittest.TestCase 
# framework and then remove deprecated files.
#TODO: continuation support or maybe test that particular feature elsewhere
#XXX: The BrunelWang model is giving me headaches again ...

# Third party python libraries
import numpy
#import unittest 

from matplotlib.pyplot import figure, plot, title, show

# From "The Virtual Brain"
from tvb.simulator.lab import *
import tvb.datatypes.sensors as sensors


sens_meg = sensors.SensorsMEG()
sens_eeg = sensors.SensorsEEG()

"""
from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.monitors as monitors
import tvb.simulator.integrators as integrators
import tvb.simulator.noise as noise
"""


class SimulatorTestCase(object): #unittest.TestCase
    """
    Simulator test class
    
    """
    def __init__(self): #setUp
        """
        Initialise the structural information, coupling function, and monitors.
        
        """

        #Initialise some Monitors with period in physical time
        raw     = monitors.Raw()
        gavg    = monitors.GlobalAverage(period=2**-2)
        subsamp = monitors.SubSample(period=2**-2)
        tavg    = monitors.TemporalAverage(period=2**-2)
        spheeg  = monitors.SphericalEEG(sensors=sens_eeg, period=2**-2)
        sphmeg  = monitors.SphericalMEG(sensors=sens_meg, period=2**-2)
        
        self.monitors = (raw, gavg, subsamp, tavg, spheeg, sphmeg) 
        
        self.model   = None
        self.method  = None
        self.sim     = None


    def test(self, simulation_length=2**4, display=False, return_data=False):
        """
        Test a simulator constructed with one of the <model>_<scheme> methods. 
        
        """

        raw_data, gavg_data, subsamp_data, tavg_data = [], [], [], []
        spheeg_data, sphmeg_data  = [], []
        #import pdb; pdb.set_trace()

        for raw, gavg, subsamp, tavg, spheeg, sphmeg in self.sim(simulation_length=simulation_length):  #  

            if not raw is None:
                raw_data.append(raw)

            if not gavg is None:
                gavg_data.append(gavg)

            if not subsamp is None:
                subsamp_data.append(subsamp)

            if not tavg is None:
                tavg_data.append(tavg)
                
            if not spheeg is None:
                spheeg_data.append(spheeg)
                
            if not sphmeg is None:
                sphmeg_data.append(sphmeg)
                
        #Display results, if requested
        if display:
            display_results(**{"Raw, " + self.model + ", "+ self.method : numpy.array(raw_data)[:, 0, :, 0], 
                               "GlobalAverage, " +self.model+", "+self.method : numpy.array(gavg_data)[:, 0, :, 0],
                               "SubSampled, "+ self.model+", "+self.method : numpy.array(subsamp_data)[:, 0, :, 0], 
                               "TemporalAverage, "+ self.model+", "+self.method : numpy.array(tavg_data)[:, 0, :, 0], 
                               "SphericalEEG, "+ self.model+", "+self.method : numpy.array(spheeg_data)[:, 0, :, 0], 
                               "SphericalMEG, "+ self.model+", "+self.method : numpy.array(sphmeg_data)[:, 0, :, 0]})

        #Return results, if requested
        if return_data:
            LOG.info("Converting lists to numpy.ndarrays before returning.")
            raw_data = numpy.array(raw_data)
            gavg_data = numpy.array(gavg_data)
            subsamp_data = numpy.array(subsamp_data)
            tavg_data = numpy.array(tavg_data)
            spheeg_data = numpy.array(spheeg_data)
            sphmeg_data = numpy.array(sphmeg_data)
            
            return raw_data, gavg_data, subsamp_data, tavg_data, spheeg_data, sphmeg_data


    def configure(self, dt=2**-4, model="Generic2dOscillator", speed=4.0, 
                  coupling_strength=0.00042, method="HeunDeterministic", 
                  surface_sim=False):
        """
        Create an instance of the Simulator class, by default use the
        generic plane oscillator local dynamic model and the deterministic 
        version of Heun's method for the numerical integration.
        
        """
        
        self.model = model
        self.method = method
        
        white_matter = connectivity.Connectivity()
        white_matter_coupling = coupling.Linear(a=coupling_strength)
        white_matter.speed = speed

        dynamics = eval("models." + model + "()")
        
        if method[-10:] == "Stochastic":
            hisss = noise.Additive(nsig = numpy.array([2**-11,]))
            integrator = eval("integrators." + method + "(dt=dt, noise=hisss)")
        else:
            integrator = eval("integrators." + method + "(dt=dt)")
        
        if surface_sim:
            local_coupling_strength = numpy.array([2**-10])
            default_cortex = surfaces.Cortex(coupling_strength=local_coupling_strength) 
        else: 
            default_cortex  = None

        # Order of monitors determines order of returned values.
        self.sim = simulator.Simulator(model = dynamics, 
                                       connectivity = white_matter,
                                       coupling =  white_matter_coupling,
                                       integrator = integrator, 
                                       monitors = self.monitors,
                                       surface=default_cortex)
        self.sim.configure()
                                       
            
            
def display_results(**kwargs):
    """
    Display a plot for each set of data provided as a keyword argument, the 
    keyword will become the title of the plot.
    
    """
    for keyword in kwargs:
        figure()
        plot(kwargs[keyword])
        title(keyword)

    show()
    

if __name__ == '__main__':
    
    
    import itertools
    from tvb.basic.traits.parameters_factory import get_traited_subclasses
    
    AVAILABLE_MODELS = get_traited_subclasses(models.Model)
    AVAILABLE_METHODS = get_traited_subclasses(integrators.Integrator)
    MODEL_NAMES = AVAILABLE_MODELS.keys()
    METHOD_NAMES = AVAILABLE_METHODS.keys()
    METHOD_NAMES.append('RungeKutta4thOrderDeterministic')
    
    #init
    test_simulator = SimulatorTestCase()
    
    #test cases
    for model_name, method_name in itertools.product(MODEL_NAMES, METHOD_NAMES):        
        test_simulator.configure(model= model_name,
                                 method=method_name,
                                 surface_sim=False)
        test_simulator.test()
#EoF