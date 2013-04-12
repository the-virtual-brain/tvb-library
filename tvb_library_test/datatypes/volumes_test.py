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

from tvb.datatypes import volumes
from tvb_library_test.base_testcase import BaseTestCase
        
class VolumesTest(BaseTestCase):
    
    def test_volume(self):
        dt = volumes.Volume()
        summary_info = dt.summary_info
        self.assertEqual(summary_info['Origin'].shape, (0,))
        self.assertEqual(summary_info['Voxel size'].shape, (0,))
        self.assertEqual(summary_info['Volume type'], 'Volume')
        self.assertEqual(summary_info['Units'], 'mm')
        self.assertEqual(dt.origin.shape, (0,))
        self.assertEqual(dt.voxel_size.shape, (0,))
        self.assertEqual(dt.voxel_unit, 'mm')
        
        
    def test_parcellationmask(self):
        dt = volumes.ParcellationMask()
        summary_info = dt.summary_info
        self.assertEqual(summary_info['Number of regions'], 0)
        self.assertEqual(summary_info['Origin'].shape, (0,))
        self.assertEqual(summary_info['Voxel size'].shape, (0,))
        self.assertEqual(summary_info['Volume shape'], (0,))
        self.assertEqual(summary_info['Volume type'], 'ParcellationMask')
        self.assertEqual(summary_info['Units'], 'mm')
        self.assertEqual(dt.origin.shape, (0,))
        self.assertEqual(dt.region_labels.shape, (0,))
        self.assertEqual(dt.voxel_size.shape, (0,))
        
        
    def test_structuralmri(self):
        dt = volumes.StructuralMRI()
        self.assertEqual(dt.origin.shape, (0,))
        self.assertEqual(dt.voxel_size.shape, (0,))
        self.assertEqual(dt.voxel_unit, 'mm')
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(VolumesTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 