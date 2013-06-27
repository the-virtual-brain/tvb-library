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
from tvb.datatypes import connectivity
from tvb_library_test.base_testcase import BaseTestCase


class ConnectivityTest(BaseTestCase):
    """
    Tests the defaults for `tvb.datatypes.connectivity` module.
    """
    
    def test_connectivity_defaults(self):
        """
        Create a connectivity and see that all defaults are loaded properly.
        """
        conn = connectivity.Connectivity()
        conn.configure()
        # Check for value from demodata/connectivity/o52r00_irp2008
        self.assertEqual(conn.weights.shape, (74, 74))
        self.assertEqual(conn.weights.max(), 3.0)
        self.assertEqual(conn.weights.min(), 0.0)
        self.assertEqual(conn.tract_lengths.shape, (74, 74))
        self.assertEqual(conn.tract_lengths.max(), 153.48574)
        self.assertEqual(conn.tract_lengths.min(), 0.0)
        self.assertEqual(conn.centres.shape, (74, 3))
        self.assertEqual(conn.orientations.shape, (74, 3))
        self.assertEqual(conn.region_labels.shape, (74,))
        self.assertEqual(conn.areas.shape, (74,))
        self.assertEqual(conn.unidirectional, 0)
        self.assertEqual(conn.speed, numpy.array([3.0]))
        self.assertTrue(conn.cortical.all())
        self.assertEqual(conn.hemispheres.shape, (74,))
        self.assertEqual(conn.idelays.shape, (0,))
        self.assertEqual(conn.delays.shape, (74, 74,))
        self.assertEqual(conn.number_of_regions, 74)
        self.assertTrue(conn.parcellation_mask is None)
        self.assertTrue(conn.nose_correction is None)
        self.assertTrue(conn.saved_selection is None)
        self.assertEqual(conn.parent_connectivity, '')
        summary = conn.summary_info
        self.assertEqual(summary['Number of regions'], 74)
        ## Call connectivity methods and make sure no compilation or runtime erros
        conn.compute_tract_lengths()
        conn.compute_region_labels()
        conn.try_compute_hemispheres()
        self.assertEqual(conn.normalised_weights().shape, (74, 74))
        for mode in ['normal', 'shuffle', 'mean', 'analytical']:
            # Empirical seems to fail on some scipy installations. Error is not pinned down
            # so far, it seems to only happen on some machines. Most relevant related to this:
            #
            # http://projects.scipy.org/scipy/ticket/1735
            # http://comments.gmane.org/gmane.comp.python.scientific.devel/14816
            # http://permalink.gmane.org/gmane.comp.python.numeric.general/42082
            conn.switch_distribution(mode=mode)
        
        
    def test_connectivity_reload(self):
        """
        Reload a connectivity and check that defaults changes accordingly.
        """
        conn = connectivity.Connectivity()
        conn.default.reload(conn,
                            folder_path=os.path.join("connectivity",
                                                     "o52r00_irp2008_hemisphere_both_subcortical_true_regions_190"))
        self.assertEqual(conn.weights.shape, (190, 190))
        self.assertEqual(conn.weights.max(), 3.0)
        self.assertEqual(conn.weights.min(), 0.0)
        self.assertEqual(conn.tract_lengths.shape, (190, 190))
        self.assertEqual(conn.tract_lengths.max(), 142.1458)
        self.assertEqual(conn.tract_lengths.min(), 0.0)
        self.assertEqual(conn.centres.shape, (190, 3))
        self.assertEqual(conn.orientations.shape, (190, 3))
        self.assertEqual(conn.region_labels.shape, (190,))
        self.assertEqual(conn.areas.shape, (190,))
        self.assertEqual(conn.unidirectional, 0)
        self.assertEqual(conn.speed, numpy.array([3.0]))
        self.assertFalse(conn.cortical.all())
        self.assertEqual(conn.hemispheres.shape, (0,))
        self.assertEqual(conn.idelays.shape, (0,))
        self.assertEqual(conn.delays.shape, (0,))
        self.assertEqual(conn.number_of_regions, 0)
        self.assertTrue(conn.parcellation_mask is None)
        self.assertTrue(conn.nose_correction is None)
        self.assertTrue(conn.saved_selection is None)
        self.assertEqual(conn.parent_connectivity, '')



def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ConnectivityTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 