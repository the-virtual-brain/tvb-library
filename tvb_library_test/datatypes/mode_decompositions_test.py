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
if __name__ == "__main__":
    from tvb_library_test import setup_test_console_env
    setup_test_console_env()
    
import unittest

from tvb.datatypes import mode_decompositions
from tvb_library_test.base_testcase import BaseTestCase
        
class ModeDecompositionsTest(BaseTestCase):
    
    def test_principalcomponents(self):
        dt = mode_decompositions.PrincipalComponents()
        self.assertTrue(dt.source is None)
        self.assertEqual(dt.weights.shape, (0,))
        self.assertEqual(dt.fractions.shape, (0,))
        self.assertEqual(dt.norm_source.shape, (0,))
        self.assertEqual(dt.component_time_series.shape, (0,))
        self.assertEqual(dt.normalised_component_time_series.shape, (0,))
        
        
    def test_independentcomponents(self):
        dt = mode_decompositions.IndependentComponents()
        self.assertTrue(dt.source is None)
        self.assertEqual(dt.mixing_matrix.shape, (0,))
        self.assertEqual(dt.unmixing_matrix.shape, (0,))
        self.assertEqual(dt.prewhitening_matrix.shape, (0,))
        self.assertEqual(dt.norm_source.shape, (0,))
        self.assertEqual(dt.component_time_series.shape, (0,))
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ModeDecompositionsTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 