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
#   Frontiers in Neuroinformatics (in press)
#
#
"""
Created on Mar 20, 2013

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
if __name__ == "__main__":
    from tvb_library_test import setup_test_console_env
    setup_test_console_env()

import sys
import numpy    
import unittest

from tvb.datatypes import patterns, equations, connectivity, surfaces
from tvb_library_test.base_testcase import BaseTestCase
        
class PatternsTest(BaseTestCase):
    """
    Tests the defaults for `tvb.datatypes.patterns` module.
    """

    def test_spatialpattern(self):
        dt = patterns.SpatialPattern()
        dt.spatial = equations.DoubleGaussian()
        dt.spatial_pattern = numpy.arange(100).reshape((10, 10))
        dt.configure_space(numpy.arange(100).reshape((10, 10)))
        dt.configure()
        summary = dt.summary_info
        self.assertEqual(summary['Type'], 'SpatialPattern')
        self.assertEqual(dt.space.shape, (10, 10))
        self.assertTrue(isinstance(dt.spatial, equations.DoubleGaussian))
        self.assertTrue(dt.spatial_pattern.shape, (10, 1))
        
        
    def test_spatiotemporalpattern(self):
        dt = patterns.SpatioTemporalPattern()
        dt.spatial = equations.DoubleGaussian()
        dt.temporal = equations.Gaussian()
        dt.spatial_pattern = numpy.arange(100).reshape((10, 10))
        dt.configure_space(numpy.arange(100).reshape((10, 10)))
        dt.configure()
        summary = dt.summary_info
        self.assertEqual(summary['Type'], 'SpatioTemporalPattern')
        self.assertEqual(dt.space.shape, (10, 10))
        self.assertTrue(isinstance(dt.spatial, equations.DoubleGaussian))
        self.assertEqual(dt.spatial_pattern.shape, (10, 1))
        self.assertTrue(isinstance(dt.temporal, equations.Gaussian))
        self.assertTrue(dt.temporal_pattern is None)
        self.assertTrue(dt.time is None)
        
        
    def test_stimuliregion(self):
        conn = connectivity.Connectivity()
        conn.configure()
        dt = patterns.StimuliRegion()
        dt.connectivity = conn
        dt.spatial = equations.Discrete()
        dt.temporal = equations.Gaussian()
        dt.weight = [0 for _ in range(conn.number_of_regions)]
        dt.configure_space()
        self.assertEqual(dt.summary_info['Type'], 'StimuliRegion')
        self.assertTrue(dt.connectivity is not None)
        self.assertEqual(dt.space.shape, (74, 1))
        self.assertEqual(dt.spatial_pattern.shape, (74, 1))
        self.assertTrue(isinstance(dt.temporal, equations.Gaussian))
        self.assertTrue(dt.temporal_pattern is None)
        self.assertTrue(dt.time is None)
        
     
    def test_stimulisurface(self):
        srf = surfaces.CorticalSurface()
        srf.configure()
        dt = patterns.StimuliSurface()
        dt.surface = srf
        dt.spatial = equations.Discrete()
        dt.temporal = equations.Gaussian()
        dt.focal_points_surface = [0, 1, 2]
        dt.focal_points_triangles = [0, 1, 2]
        dt.configure()
        dt.configure_space()
        summary = dt.summary_info
        self.assertEqual(summary['Type'], "StimuliSurface")
        self.assertEqual(dt.space.shape, (81924, 3))
        self.assertTrue(isinstance(dt.spatial, equations.Discrete))
        self.assertEqual(dt.spatial_pattern.shape, (81924, 1))
        self.assertTrue(dt.surface is not None)
        self.assertTrue(isinstance(dt.temporal, equations.Gaussian))
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