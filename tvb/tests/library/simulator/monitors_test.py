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
Test monitors for specific properties such as default periods, correct
handling of projection matrices, etc.

.. moduleauthor:: Paula Sanz Leon <sanzleon.paula@gmail.com>
.. moduleauthor:: Marmaduke Woodman <marmaduke.woodman@univ-amu.fr>

"""

import unittest

if __name__ == "__main__":
    from tvb.tests.library import setup_test_console_env
    setup_test_console_env()

from tvb.basic.logger.builder import get_logger
from tvb.tests.library.base_testcase import BaseTestCase
from tvb.simulator.lab import *
from tvb.datatypes.cortex import Cortex
from tvb.datatypes.region_mapping import RegionMapping


LOG = get_logger(__name__)


class MonitorsTest(BaseTestCase):
    """
    Define test cases for monitors:
        - initialise each class
        - check default parameters (period)
        - 
    """

    default_period = 0.9765625  # 1024Hz

    def test_monitor_raw(self):
        monitors.Raw()
    
    
    def test_monitor_tavg(self):
        monitor = monitors.TemporalAverage()
        self.assertEqual(monitor.period, self.default_period)
        
        
    def test_monitor_gavg(self):
        monitor = monitors.GlobalAverage()
        self.assertEqual(monitor.period, self.default_period)
        
        
    def test_monitor_savg(self):
        monitor = monitors.SpatialAverage()
        self.assertEqual(monitor.period, self.default_period)
        
        
    def test_monitor_subsample(self):
        monitor = monitors.SubSample()
        self.assertEqual(monitor.period, self.default_period)
    

    def test_monitor_eeg(self):
        monitor = monitors.EEG()
        self.assertEqual(monitor.period, self.default_period)


    def test_monitor_meg(self):
        monitor = monitors.MEG()
        self.assertEqual(monitor.period, self.default_period)
        
    def test_monitor_stereoeeg(self):
        """
        This has to be verified.
        """
        monitor = monitors.iEEG()
        monitor.sensors = sensors.SensorsInternal(load_default=True)
        self.assertEqual(monitor.period, self.default_period)


    def test_monitor_bold(self):
        """
        This has to be verified.
        """
        monitor = monitors.Bold()
        self.assertEqual(monitor.period, 2000.0)

        
class MonitorsConfigurationTest(BaseTestCase):
    """
    Configure Monitors
    
    """
    def test_monitor_bold(self):
        """
        This has to be verified.
        """
        monitor = monitors.Bold()
        self.assertEqual(monitor.period, 2000.0)


class SubcorticalProjectionTest(BaseTestCase):
    """
    Cortical surface with subcortical regions, sEEG, EEG & MEG, using a stochastic
    integration. This test verifies the shapes of the projection matrices, and
    indirectly covers region mapping, etc.

    """

    # hard code parameters to smoke test
    speed = 4.0
    period = 1e3/1024.0 # 1024 Hz
    coupling_a = 0.014
    n_regions = 192

    def setUp(self):
        oscillator = models.Generic2dOscillator()
        white_matter = connectivity.Connectivity.from_file('connectivity_%d.zip' % (self.n_regions, ))
        white_matter.speed = numpy.array([self.speed])
        white_matter_coupling = coupling.Difference(a=self.coupling_a)
        heunint = integrators.HeunStochastic(
            dt=2**-4,
            noise=noise.Additive(nsig=numpy.array([2 ** -10, ]))
        )
        mons = (
            monitors.EEG.from_files('eeg-brainstorm-65.txt', 'projection_EEG_surface.npy', period=self.period),
            monitors.MEG.from_files('meg-brainstorm-276.txt', 'projection_MEG_surface.npy', period=self.period),
            monitors.iEEG.from_files('seeg-brainstorm-960.txt', 'projection_SEEG_surface.npy', period=self.period),
        )
        local_coupling_strength = numpy.array([2 ** -10])
        region_mapping = RegionMapping.from_file('regionMapping_16k_%d.txt' % (self.n_regions, ))
        default_cortex = Cortex(region_mapping_data=region_mapping, load_default=True)
        default_cortex.coupling_strength = local_coupling_strength
        self.sim = simulator.Simulator(model=oscillator, connectivity=white_matter, coupling=white_matter_coupling,
                                       integrator=heunint, monitors=mons, surface=default_cortex)
        self.sim.configure()

    def test_connectivity(self):
        conn = self.sim.connectivity
        self.assertEqual(conn.number_of_regions, self.n_regions)
        self.assertEqual(conn.speed, self.speed)

    def test_monitor_properties(self):
        lc_n_node = self.sim.surface.local_connectivity.matrix.shape[0]
        for mon in self.sim.monitors:
            self.assertEqual(mon.period, self.period)
            n_sens, g_n_node = mon.gain.shape
            _, _, h_n_node, _ = self.sim.history.shape
            self.assertEqual(g_n_node, h_n_node)
            self.assertEqual(n_sens, mon.sensors.number_of_sensors)
            self.assertEqual(lc_n_node, g_n_node)

    def test_output_shape(self):
        ys = {}
        mons = 'eeg meg seeg'.split()
        for key in mons:
            ys[key] = []
        for data in self.sim(simulation_length=3.0):
            for key, dat in zip(mons, data):
                if dat:
                    _, y = dat
                    ys[key].append(y)
        for mon, key in zip(self.sim.monitors, mons):
            ys[key] = numpy.array(ys[key])
            self.assertEqual(ys[key].shape[2], mon.gain.shape[0])

    def tearDown(self):
        # gc sim so multiple test suites don't hog memory
        del self.sim


class NoSubCorticalProjection(SubcorticalProjectionTest):
    "Idem. but with 76 region connectivity"
    n_regions = 76


def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    for obj in globals().itervalues():
        if isinstance(obj, type) and issubclass(obj, BaseTestCase):
            test_suite.addTest(unittest.makeSuite(obj))
            LOG.info('adding test suite from class %r' % (obj, ))
    return test_suite


if __name__ == "__main__":
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE)