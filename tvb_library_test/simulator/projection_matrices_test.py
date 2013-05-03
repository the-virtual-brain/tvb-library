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
Test for tvb.simulator.projection_matrices module
This would make sense if OpenMEEG was integrated to TVB and functional, 
in which case we could test the methods in this module.

.. moduleauthor:: Paula Sanz Leon <sanzleon.paula@gmail.com>

"""

if __name__ == "__main__":
    from tvb_library_test import setup_test_console_env
    setup_test_console_env()
    
import unittest

from tvb_library_test.base_testcase import BaseTestCase
from tvb.simulator import projection_matrices


class ProjectionMatricesTest(BaseTestCase):
    """
    This test is checking correspondance between cortical surface and connectivity.
    """
    def test_projection_matrices(self):
        """
        do nothing
        """

    
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ProjectionMatricesTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 