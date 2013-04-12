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
Created on Mar 20, 2013

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
if __name__ == "__main__":
    from tvb_library_test import setup_test_console_env
    setup_test_console_env()
    
import unittest

from tvb.datatypes import sensors, surfaces
from tvb_library_test.base_testcase import BaseTestCase
        
class SensorsTest(BaseTestCase):
    
    def test_sensors(self):
        surf = surfaces.SkinAir()
        surf.configure()
        dt = sensors.Sensors()
        dt.configure()
        mapping = dt.sensors_to_surface(surf)
        self.assertEqual(mapping[0].shape, (62, 1))
        self.assertEqual(mapping[1].shape, (62, 3))
        summary_info = dt.summary_info
        self.assertEqual(summary_info['Sensor type'], '')
        self.assertEqual(summary_info['Number of Sensors'], 62)
        self.assertFalse(dt.has_orientation)
        self.assertEqual(dt.labels.shape, (62,))
        self.assertEqual(dt.locations.shape, (62, 3))
        self.assertEqual(dt.number_of_sensors, 62)
        self.assertEqual(dt.orientations.shape, (0,))
        self.assertEqual(dt.sensors_type, '')

        
    def test_sensorseeg(self):
        dt = sensors.SensorsEEG()
        dt.configure()
        self.assertFalse(dt.has_orientation)
        self.assertEqual(dt.labels.shape, (62,))
        self.assertEqual(dt.locations.shape, (62, 3))
        self.assertEqual(dt.number_of_sensors, 62)
        self.assertEqual(dt.orientations.shape, (0,))
        self.assertEqual(dt.sensors_type, 'EEG')
        
        
    def test_sensorsmeg(self):
        dt = sensors.SensorsMEG()
        dt.configure()
        self.assertTrue(dt.has_orientation)
        self.assertEqual(dt.labels.shape, (151,))
        self.assertEqual(dt.locations.shape, (151, 3))
        self.assertEqual(dt.number_of_sensors, 151)
        self.assertEqual(dt.orientations.shape, (151, 3))
        self.assertEqual(dt.sensors_type, 'MEG')
        
        
    def test_sensorsinternal(self):
        dt = sensors.SensorsInternal()
        dt.configure()
        self.assertFalse(dt.has_orientation)
        self.assertEqual(dt.labels.shape, (62,))
        self.assertEqual(dt.locations.shape, (62, 3))
        self.assertEqual(dt.number_of_sensors, 62)
        self.assertEqual(dt.orientations.shape, (0,))
        self.assertEqual(dt.sensors_type, 'Internal')
        
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(SensorsTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 