# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
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
import unittest

from tvb.datatypes import patterns
from tvb_library_test.base_testcase import BaseTestCase
        
class PatternsTest(BaseTestCase):
    
    def test_principalcomponents(self):
        dt = patterns.SpatialPattern()
        self.assertTrue(dt.space is None)
        self.assertTrue(dt.spatial is None)
        self.assertTrue(dt.spatial_pattern is None)
        
        
    def test_spatiotemporalpattern(self):
        dt = patterns.SpatioTemporalPattern()
        self.assertTrue(dt.space is None)
        self.assertTrue(dt.spatial is None)
        self.assertTrue(dt.spatial_pattern is None)
        self.assertTrue(dt.temporal is None)
        self.assertTrue(dt.temporal_pattern is None)
        self.assertTrue(dt.time is None)
        
        
    def test_stimuliregion(self):
        dt = patterns.StimuliRegion()
        self.assertTrue(dt.connectivity is None)
        self.assertTrue(dt.space is None)
        self.assertTrue(dt.spatial_pattern is None)
        self.assertTrue(dt.temporal is None)
        self.assertTrue(dt.temporal_pattern is None)
        self.assertTrue(dt.time is None)
        
        
    def test_stimulisurface(self):
        dt = patterns.StimuliSurface()
        self.assertTrue(dt.space is None)
        self.assertTrue(dt.spatial is None)
        self.assertTrue(dt.spatial_pattern is None)
        self.assertTrue(dt.surface is None)
        self.assertTrue(dt.temporal is None)
        self.assertTrue(dt.temporal_pattern is None)
        self.assertTrue(dt.time is None)
        
        
    def test_spatialpatternvolume(self):
        dt = patterns.SpatialPatternVolume()
        self.assertTrue(dt.space is None)
        self.assertTrue(dt.spatial is None)
        self.assertTrue(dt.spatial_pattern is None)
        self.assertTrue(dt.volume is None)
        self.assertEqual(dt.focal_points_volume.shape, (0,))
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(PatternsTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 