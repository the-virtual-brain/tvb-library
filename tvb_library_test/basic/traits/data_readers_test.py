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
    
import os
import numpy
import unittest

from tvb_library_test.base_testcase import BaseTestCase
from tvb.basic.config.settings import TVBSettings as cfg
from tvb.basic.traits.data_readers import File
        
class DataReadersTest(BaseTestCase):
    
    def test_read_data_txt(self):
        """
        Test that reading data from numpy txt files works as expected.
        """
        test_data = numpy.arange(16).reshape(4, 4)
        test_data_file = os.path.join(cfg.TVB_TEMP_FOLDER, 'test_data.txt')
        numpy.savetxt(test_data_file, test_data)
        tvb_file = File(cfg.TVB_TEMP_FOLDER)
        read_data = tvb_file.read_data(file_name='test_data.txt')
        for x_idx in range(test_data.shape[0]):
            for y_idx in range(test_data.shape[1]):
                self.assertEqual(test_data[x_idx][y_idx], read_data[x_idx][y_idx], 
                                 "Loaded data from file is different from data that was saved.")
        self._test_file_object(tvb_file, 'test_data.txt')
        os.remove(test_data_file)
        
    def test_read_data_npz(self):
        """
        Test that a npz file is properly read by our method.
        """
        test_array_1 = numpy.array([1, 2, 3, 4])
        test_array_2 = numpy.array([[10, 10], [15, 15]])
        test_data_file = os.path.join(cfg.TVB_TEMP_FOLDER, 'test_data.npz')
        tvb_file = File(cfg.TVB_TEMP_FOLDER)
        numpy.savez(test_data_file, array1=test_array_1, array2=test_array_2)
        read_data = tvb_file.read_data(file_name='test_data.npz')
        for idx in xrange(len(test_array_1)):
            self.assertEqual(test_array_1[idx], read_data['array1'][idx], 
                             "Loaded data from file is different from data that was saved.")
        for x_idx in range(test_array_2.shape[0]):
            for y_idx in range(test_array_2.shape[1]):
                self.assertEqual(test_array_2[x_idx][y_idx], read_data['array2'][x_idx][y_idx], 
                                 "Loaded data from file is different from data that was saved.")
        self._test_file_object(tvb_file, 'test_data.npz')
        read_data.close()
        os.remove(test_data_file)
        
    def _test_file_object(self, file_object, data_file_name):
        """
        Test tha specific parameters like lazy_load or field work as expected.
        """
        self.assertTrue(file_object.read_data(file_name=data_file_name, lazy_load=True) is None, 
                          "Lazy load flag should assure None is returned.")
        self.assertEqual(file_object.references, {}, 
                         "Since no field was passed, references should be empty")
        file_object.read_data(lazy_load=True, field="test_field")
        self.assertTrue('test_field' in file_object.references)

        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(DataReadersTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 