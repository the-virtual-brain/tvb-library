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

from tvb.datatypes import graph, time_series, connectivity
from tvb_library_test.base_testcase import BaseTestCase
        
class GraphTest(BaseTestCase):
    
    def test_covariance(self):
        data = numpy.random.random((10, 10))
        ts = time_series.TimeSeries(data=data)
        dt = graph.Covariance(source=ts)
        self.assertEqual(dt.shape, (0,))
        self.assertEqual(dt.array_data.shape, (0,))
        summary = dt.summary_info
        self.assertEqual(summary['Graph type'], "Covariance")
        self.assertEqual(summary['Shape'], (0,))
        
        
    def test_connectivitymeasure(self):
        conn = connectivity.Connectivity()
        dt = graph.ConnectivityMeasure(connectivity=conn)
        self.assertEqual(dt.shape, (0,))
        self.assertTrue(dt.dimensions_labels is None)
        self.assertTrue(dt.connectivity is not None)
        summary = dt.summary_info
        self.assertEqual(summary['Graph type'], 'ConnectivityMeasure')
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(GraphTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 