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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
if __name__ == "__main__":
    from tvb_library_test import setup_test_console_env
    setup_test_console_env()
    
import unittest

import tvb.datatypes.surfaces as surfaces
import tvb.datatypes.connectivity as connectivity
from tvb_library_test.base_testcase import BaseTestCase

            
class ConsoleTraitedTest(BaseTestCase):
    """
    Test using traited classes from console.
    """

    def test_default_attributes(self):
        """
        Test that default_console attributes are populated.
        """
        cortex = surfaces.CorticalSurface()
        cortex.configure()
        self.assertTrue(cortex.vertices is not None)
        self.assertEqual(81924, cortex.number_of_vertices)
        self.assertEqual((81924, 3), cortex.vertices.shape)
        self.assertEqual((81924, 3), cortex.vertex_normals.shape)
        self.assertEqual(163840, cortex.number_of_triangles)
        self.assertEqual((163840, 3), cortex.triangles.shape)
        
        conn = connectivity.Connectivity()
        conn.configure()
        self.assertTrue(conn.centres is not None)
        self.assertEqual((74,), conn.region_labels.shape)
        self.assertEqual('lA1', conn.region_labels[0])
        self.assertEquals((74, 3), conn.centres.shape)
        self.assertEquals((74, 74), conn.weights.shape)
        self.assertEquals((74, 74), conn.tract_lengths.shape)
        self.assertEquals(conn.delays.shape, conn.tract_lengths.shape)
        self.assertEqual(74, conn.number_of_regions)
       
        
    def test_assign_complex_attr(self):
        """
        Test scientific methods are executed
        """
        local_coupling_strength = 0.0121 #2**-10
        grey_matter = surfaces.LocalConnectivity(cutoff = 10.0)
        default_cortex = surfaces.Cortex(coupling_strength=local_coupling_strength)
        #self.assertTrue(default_cortex.local_connectivity is None)
        default_cortex.local_connectivity = grey_matter
        #default_cortex.region_average = default_cortex.region_mapping
        default_cortex.compute_local_connectivity()
        self.assertTrue(default_cortex.local_connectivity is not None)


def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ConsoleTraitedTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 
    
    
