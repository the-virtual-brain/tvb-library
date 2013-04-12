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
Created on Apr 8, 2013

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
### Try to import extra module when running with Python 2.6 (where unittest2 is not default)
try:
    import unittest2 as unittest
except Exception, _:
    import unittest
from tvb.basic.config.settings import TVBSettings as cfg

class BaseTestCase(unittest.TestCase):
    """
        This class should implement basic functionality which 
        is common to all TVB tests.
    """
    def setUp(self):
        self.assertFalse(cfg.TRAITS_CONFIGURATION.use_storage)
    
    def assertEqual(self, expected, actual, message=""):
        super(BaseTestCase, self).assertEqual(expected, actual, message + " Expected %s but got %s."%(expected, actual))
        
        