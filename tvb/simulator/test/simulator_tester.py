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

"""
Test the simulator module... should this be in the simulator module, so that 
the module contains the test of its own main class???

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""
#TODO: Adapt to use the unittest.TestCase framework...

# From standard python libraries
##import unittest #NOTE: To use unitest framework meaningfully, reference data
#                        needs to be created with which results can be compared.


# Third party python libraries
import numpy
from matplotlib.pyplot import figure, plot, title, show

# From "The Virtual Brain"
try:
    from tvb.basic.logger.builder import get_logger
    LOG = get_logger(__name__)
except ImportError:
    import logging
    LOG = logging.getLogger(__name__)
    LOG.warning("Failed to import tvb.basic.logger.builder, falling back to logging")
    
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
try:
    import tvb.datatypes.connectivity as connectivity
except ImportError:
    msg = "Failed to import tvb.datatypes.connectivity, falling back to "
    msg = msg + "tvb.simulator.connectivity."
    LOG.warning(msg)  
import tvb.simulator.connectivity as connectivity
    
    
import tvb.simulator.monitors as monitors
import tvb.simulator.integrators as integrators
import tvb.simulator.noise as noise


class TestSimulator(object): #unittest.TestCase
    """
    Simulator test class...
    
    """
    def __init__(self): #setUp
        """
        Initialise the structural information, coupling function, and monitors.
        
        """

        #Initialise some Monitors with period in physical time
        raw = monitors.Raw()
        gavg = monitors.GlobalAverage(period=2**-2)
        subsamp = monitors.SubSample(period=2**-2)
        tavg = monitors.TemporalAverage(period=2**-2)
        spheeg = monitors.SphericalEEG(period=2**-2)
        sphmeg = monitors.SphericalMEG(period=2**-2)
        
        self.monitors = (raw, gavg, subsamp, tavg, spheeg, sphmeg) 
        
        self.model = None
        self.method = None
        self.sim = None


    def test(self, simulation_length=2**4, display=False, return_data=False):
        """
        Test a simulator constructed with one of the <model>_<scheme> methods. 
        
        """

        raw_data = []
        gavg_data  = []
        subsamp_data  = []
        tavg_data = []
        spheeg_data = []
        sphmeg_data = []
        for _, raw, gavg, subsamp, tavg, spheeg, sphmeg in self.sim(simulation_length=simulation_length):  #  

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
                
        #assertAlmostEqual(avg_data, refAVG) #TODO: Need to construct reference
        #                                           data to compare against, for
        #                                           testing when run on a new
        #                                           system or after code update.
        
        #Display results, if requested
        if display:
            #import pdb; pdb.set_trace()
            display_results(**{"Raw, "+self.model+", "+self.method : numpy.array(raw_data)[:, 0, :, 0], 
                               "GlobalAverage, "+self.model+", "+self.method : numpy.array(gavg_data)[:, 0, :, 0],
                               "SubSampled, "+self.model+", "+self.method : numpy.array(subsamp_data)[:, 0, :, 0], 
                               "TemporalAverage, "+self.model+", "+self.method : numpy.array(tavg_data)[:, 0, :, 0], 
                               "SphericalEEG, "+self.model+", "+self.method : numpy.array(spheeg_data)[:, 0, :, 0], 
                               "SphericalMEG, "+self.model+", "+self.method : numpy.array(sphmeg_data)[:, 0, :, 0]})

        #Return results, if requested
        if return_data:
            LOG.info("Converting lists to numpy.ndarrays before returning.")
            #import pdb; pdb.set_trace()
            raw_data = numpy.array(raw_data)
            gavg_data = numpy.array(gavg_data)
            subsamp_data = numpy.array(subsamp_data)
            tavg_data = numpy.array(tavg_data)
            spheeg_data = numpy.array(spheeg_data)
            sphmeg_data = numpy.array(sphmeg_data)
            
            return raw_data, gavg_data, subsamp_data, tavg_data, spheeg_data, sphmeg_data


    def configure(self, dt=2**-4, model="Generic2dOscillator", speed=4.0, 
                  coupling_strength=0.016, method="HeunDeterministic"):
        """
        Configure a Simulator and assign it to the sim class, by default use the
        Fitz-Hugh Nagumo local dynamic model and the deterministic version of 
        Heun's method for the numerical integration.
        
        """
        
        self.model = model
        self.method = method
        
        #white_matter = connectivity.Connectivity(coupling=coupling.Linear(a=coupling_strength))
        white_matter = connectivity.Connectivity()
        white_matter.coupling = coupling.Linear(a=coupling_strength)
        white_matter.speed = speed

        dynamics = eval("models." + model + "()")
        
        if method[-10:] == "Stochastic":
            hisss = noise.Additive(nsig = numpy.array([0.00390625,]))
            integrator = eval("integrators." + method + "(dt=dt, noise=hisss)")
        else:
            integrator = eval("integrators." + method + "(dt=dt)")

        # Order of monitors determines order of returned values.
        self.sim = simulator.Simulator(dynamics, white_matter, integrator, 
                                       self.monitors)
            
            
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
    # Check that the docstring examples, if there are any, are accurate.
    import doctest
    doctest.testmod()

##    # Test code using unittest framework
##    unittest.main()

    # Test code with display
    test_simulator = TestSimulator()
    
    #Generic2dOscillator, HeunDeterministic, 
    test_simulator.configure()
    test_simulator.test(display=True)
    
    #Generic2dOscillator, EulerDeterministic, 
    test_simulator.configure(method="EulerDeterministic")
    test_simulator.test(display=True)
    
    #Generic2dOscillator, HeunStochastic, 
    test_simulator.configure(method="HeunStochastic")
    test_simulator.test(display=True)
    
    #Generic2dOscillator, EulerStochastic, 
    test_simulator.configure(method="EulerStochastic")
    test_simulator.test(display=True)
    
    #Generic2dOscillator, RungeKutta4thOrderDeterministic, 
    test_simulator.configure(method="RungeKutta4thOrderDeterministic")
    test_simulator.test(display=True)
    
    #HindmarshRose, HeunDeterministic, 
    test_simulator.configure(model="HindmarshRose")
    test_simulator.test(display=True)
    
    #HindmarshRose, EulerDeterministic, 
    test_simulator.configure(model="HindmarshRose",
                             method="EulerDeterministic")
    test_simulator.test(display=True)
    
    #HindmarshRose, HeunStochastic, 
    test_simulator.configure(model="HindmarshRose",
                             method="HeunStochastic")
    test_simulator.test(display=True)
    
    #HindmarshRose, EulerStochastic, 
    test_simulator.configure(model="HindmarshRose",
                             method="EulerStochastic")
    test_simulator.test(display=True)
    
    #HindmarshRose, RungeKutta4thOrderDeterministic, 
    test_simulator.configure(model="HindmarshRose",
                             method="RungeKutta4thOrderDeterministic")
    test_simulator.test(display=True)
    
    #MorrisLecar, HeunDeterministic, 
    test_simulator.configure(model="MorrisLecar")
    test_simulator.test(display=True)
    
    #MorrisLecar, HeunStochastic, 
    test_simulator.configure(model="MorrisLecar",
                             method="HeunStochastic")
    test_simulator.test(display=True)
    
    #MorrisLecar, RungeKutta4thOrderDeterministic, 
    test_simulator.configure(model="MorrisLecar",
                             method="RungeKutta4thOrderDeterministic")
    test_simulator.test(display=True)
    
#    #Larter, HeunDeterministic, 
#    test_simulator.configure(model="Larter")
#    test_simulator.test(display=True)
#    
#    #Larter, HeunStochastic, 
#    test_simulator.configure(model="Larter", 
#                             method="HeunStochastic")
#    test_simulator.test(display=True)
#    
#    #Larter, RungeKutta4thOrderDeterministic, 
#    test_simulator.configure(model="Larter",
#                             method="RungeKutta4thOrderDeterministic")
#    test_simulator.test(display=True)
    
    #WilsonCowan, HeunDeterministic, 
    test_simulator.configure(model="WilsonCowan")
    test_simulator.test(display=True)
    
    #WilsonCowan, HeunStochastic, 
    test_simulator.configure(model="WilsonCowan",
                             method="HeunStochastic")
    test_simulator.test(display=True)
    
    #WilsonCowan, RungeKutta4thOrderDeterministic, 
    test_simulator.configure(model="WilsonCowan",
                             method="RungeKutta4thOrderDeterministic")
    test_simulator.test(display=True)
    
    #ReducedSetHindmarshRose, HeunDeterministic, 
    test_simulator.configure(model="ReducedSetHindmarshRose")
    test_simulator.test(display=True)
#    
    #ReducedSetHindmarshRose, HeunStochastic, 
    test_simulator.configure(model="ReducedSetHindmarshRose", 
                             method="HeunStochastic")
    test_simulator.test(display=True)
    
    #ReducedSetHindmarshRose, RungeKutta4thOrderDeterministic, 
    test_simulator.configure(model="ReducedSetHindmarshRose",
                             method="RungeKutta4thOrderDeterministic")
    test_simulator.test(display=True)
    
    #ReducedSetFitzHughNagumo, HeunDeterministic, 
    test_simulator.configure(model="ReducedSetFitzHughNagumo")
    test_simulator.test(display=True)
    
    #ReducedSetFitzHughNagumo, HeunStochastic, 
    test_simulator.configure(model="ReducedSetFitzHughNagumo", 
                             method="HeunStochastic")
    test_simulator.test(display=True)
    
    #ReducedSetFitzHughNagumo, RungeKutta4thOrderDeterministic, 
    test_simulator.configure(model="ReducedSetFitzHughNagumo",
                             method="RungeKutta4thOrderDeterministic")
    test_simulator.test(display=True)
    
    

##    # Test the code with profiling
##    import cProfile
##    test_simulator = TestSimulator()
##    test_simulator.fhn_heun()
##    cProfile.run('test_simulator.test()')
##    cProfile.run('runthetest.test_fhn_euler()')
##    cProfile.run('runthetest.test_hr_heun()')
##    cProfile.run('runthetest.test_hr_euler()')

#EoF
