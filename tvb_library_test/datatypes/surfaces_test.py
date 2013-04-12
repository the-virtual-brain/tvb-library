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
    
import os
import sys
try:
    import unittest2 as unittest
except Exception, _:
    import unittest

from tvb.datatypes import surfaces
from tvb_library_test.base_testcase import BaseTestCase
        
class SurfacesTest(BaseTestCase):
    
    def test_surface(self):
        dt = surfaces.Surface()
        dt.configure()
        summary_info = dt.summary_info
        self.assertEqual(summary_info['Number of edges'], 49140)
        self.assertEqual(summary_info['Number of triangles'], 32760)
        self.assertEqual(summary_info['Number of vertices'], 16384)
        self.assertEqual(summary_info['Surface type'], 'Surface')
        self.assertEqual(len(dt.vertex_neighbours), 16384)
        self.assertTrue(isinstance(dt.vertex_neighbours[0], frozenset))
        self.assertEqual(len(dt.vertex_triangles), 16384)
        self.assertTrue(isinstance(dt.vertex_triangles[0], frozenset))
        self.assertEqual(len(dt.nth_ring(0)), 17)
        self.assertEqual(dt.triangle_areas.shape, (32760, 1))
        self.assertEqual(dt.triangle_angles.shape, (32760, 3))
        self.assertEqual(len(dt.edges), 49140)
        self.assertTrue(abs(dt.edge_length_mean - 3.97605292887) < 0.00000001)
        self.assertTrue(abs(dt.edge_length_min - 0.663807567201) < 0.00000001)
        self.assertTrue(abs(dt.edge_length_max - 7.75671853782) < 0.00000001)
        self.assertEqual(len(dt.edge_triangles), 49140)
        self.assertEqual(dt.check(), (True, 4, [], [], []))
        self.assertEqual(dt.get_data_shape('vertices'), (16384, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (16384, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (32760, 3))
        
        
    def test_surface_reload(self):
        dt = surfaces.Surface()
        dt.default.reload(dt, folder_path = os.path.join("surfaces", "cortex_tvb_whitematter"))
        self.assertEqual(dt.get_data_shape('vertices'), (81924, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (81924, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (163840, 3))
        
        
    def test_corticalsurface(self):
        dt = surfaces.CorticalSurface()
        self.assertEqual(dt.get_data_shape('vertices'), (81924, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (81924, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (163840, 3))
        
        
    def test_skinair(self):
        dt = surfaces.SkinAir()
        self.assertEqual(dt.get_data_shape('vertices'), (4096, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (4096, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (8188, 3))
        
        
    def test_brainskull(self):
        dt = surfaces.BrainSkull()
        self.assertEqual(dt.get_data_shape('vertices'), (4096, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (4096, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (8188, 3))
        
        
    def test_skullskin(self):
        dt = surfaces.SkullSkin()
        self.assertEqual(dt.get_data_shape('vertices'), (4096, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (4096, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (8188, 3))
        
        
    def test_eegcap(self):
        dt = surfaces.EEGCap()
        self.assertEqual(dt.get_data_shape('vertices'), (16384, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (16384, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (32760, 3))
        
        
    def test_facesurface(self):
        dt = surfaces.FaceSurface()
        self.assertEqual(dt.get_data_shape('vertices'), (16384, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (16384, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (32760, 3))
        
        
    def test_regionmapping(self):
        dt = surfaces.RegionMapping()
        self.assertEqual(dt.shape, (16384,))
        
        
    def test_localconnectivity(self):
        dt = surfaces.LocalConnectivity()
        self.assertTrue(dt.surface is None)
        
    
    @unittest.skipIf(sys.maxsize <= 2147483647, "Cannot compute local connectivity on 32-bit machine.")    
    def test_cortexdata(self):
        dt = surfaces.Cortex()
        dt.configure()
        summary_info = dt.summary_info
        self.assertTrue(abs(summary_info['Region area, maximum (mm:math:`^2`)']- 9119.4540365252615) < 0.00000001)
        self.assertTrue(abs(summary_info['Region area, mean (mm:math:`^2`)'] - 3366.2542250541251) < 0.00000001)
        self.assertTrue(abs(summary_info['Region area, minimum (mm:math:`^2`)'] - 366.48271886512993) < 0.00000001)
        self.assertEqual(dt.get_data_shape('vertices'), (16384, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (16384, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (32760, 3))
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(SurfacesTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 
    
    