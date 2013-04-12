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
 
import numpy   
import unittest

from tvb.datatypes import mapped_values, time_series
from tvb_library_test.base_testcase import BaseTestCase
        
class MappedTest(BaseTestCase):
    
    def test_valuewrapper(self):
        dt = mapped_values.ValueWrapper(data_value=10,
                                         data_type="Integer",
                                         data_name="TestVale")
        self.assertEqual(dt.display_name, "Value Wrapper - TestVale : 10 (Integer)")
        
        
    def test_datatypemeasure(self):
        data = numpy.random.random((10, 10, 10, 10))
        ts = time_series.TimeSeries(data=data)
        dt = mapped_values.DatatypeMeasure(analyzed_datatype=ts,
                                           metrics={"Dummy" : 1})
        self.assertEqual(dt.display_name, "\nDummy : 1\n")
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(MappedTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 