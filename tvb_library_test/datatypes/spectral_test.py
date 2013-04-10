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

from tvb.datatypes import spectral
from tvb_library_test.base_testcase import BaseTestCase
        
class SpectralTest(BaseTestCase):
    
    def test_fourierspectrum(self):
        dt = spectral.FourierSpectrum()
        self.assertTrue(dt.aggregation_functions is None)
        self.assertEqual(dt.normalised_average_power.shape, (0,))
        self.assertEqual(dt.segment_length, 0.0)
        self.assertEqual(dt.shape, (0,))
        self.assertTrue(dt.source is None)
        self.assertEqual(dt.windowing_function, '')
        
        
    def test_waveletcoefficients(self):
        dt = spectral.WaveletCoefficients()
        self.assertEqual(dt.q_ratio, 5.0)
        self.assertEqual(dt.sample_period, 0.0)
        self.assertEqual(dt.shape, (0,))
        self.assertTrue(dt.source is None)
        
        
    def test_coherencespectrum(self):
        dt = spectral.CoherenceSpectrum()
        self.assertEqual(dt.nfft, 256)
        self.assertEqual(dt.shape, (0,))
        self.assertTrue(dt.source is None)
        
        
    def test_complexcoherence(self):
        dt = spectral.ComplexCoherenceSpectrum()
        self.assertTrue(dt.aggregation_functions is None)
        self.assertEqual(dt.epoch_length, 0.0)
        self.assertEqual(dt.segment_length, 0.0)
        self.assertEqual(dt.shape, (0,))
        self.assertTrue(dt.source is None)
        self.assertEqual(dt.windowing_function, '')
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(SpectralTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 