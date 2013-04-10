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

from tvb.datatypes import surfaces
from tvb_library_test.base_testcase import BaseTestCase
        
class SurfacesTest(BaseTestCase):
    
    def test_surface(self):
        dt = surfaces.Surface()
        self.assertEqual(dt.get_data_shape('vertices'), (16384, 3))
        self.assertEqual(dt.get_data_shape('vertex_normals'), (16384, 3))
        self.assertEqual(dt.get_data_shape('triangles'), (32760, 3))
        
        
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
        
        
    def test_cortexdata(self):
        dt = surfaces.Cortex()
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