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
    
import numpy    
import unittest

from tvb.datatypes import temporal_correlations, time_series
from tvb_library_test.base_testcase import BaseTestCase
        
class TemporalCorrelationsTest(BaseTestCase):
    """
    Tests the defaults for `tvb.datatypes.temporal_correlations` module.
    """
    
    def test_crosscorrelation(self):
        data = numpy.random.random((10, 10))
        ts = time_series.TimeSeries(data=data)
        dt = temporal_correlations.CrossCorrelation(source=ts)
        summary_info = dt.summary_info
        self.assertEqual(summary_info['Dimensions'], ['Offsets', 'Node', 'Node', 'State Variable', 'Mode'])
        self.assertEqual(summary_info['Source'], '')
        self.assertEqual(summary_info['Temporal correlation type'], 'CrossCorrelation')
        self.assertEqual(dt.labels_ordering, ['Offsets', 'Node', 'Node', 'State Variable', 'Mode'])
        self.assertTrue(dt.source is not None)
        self.assertEqual(dt.time.shape, (0,))
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TemporalCorrelationsTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 