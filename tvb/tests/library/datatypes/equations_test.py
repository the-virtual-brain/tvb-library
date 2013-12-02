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
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#
"""
Created on Mar 20, 2013

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
    
import unittest
from tvb.datatypes import equations
from tvb.tests.library.base_testcase import BaseTestCase


class EquationsTest(BaseTestCase):
    """
    Tests the defaults for `tvb.datatypes.equations` module.
    """
    
    def test_equation(self):
        dt = equations.Equation()
        self.assertEqual(dt.parameters, {})
        self.assertEqual(dt.ui_equation, '')

        
    def test_finitesupportequation(self):
        dt = equations.FiniteSupportEquation()
        self.assertEqual(dt.parameters, {})
        self.assertEqual(dt.ui_equation, '')


    def test_discrete(self):
        dt = equations.DiscreteEquation()
        self.assertEqual(dt.parameters, {})
        self.assertEqual(dt.ui_equation, 'var')
        
        
    def test_linear(self):
        dt = equations.Linear()
        self.assertEqual(dt.parameters, {'a': 1.0, 'b': 0.0})
        self.assertEqual(dt.ui_equation, 'a * var + b')
        
        
    def test_gaussian(self):
        dt = equations.Gaussian()
        self.assertEqual(dt.parameters, {'amp': 1.0, 'sigma': 1.0, 'midpoint': 0.0})
        self.assertEqual(dt.ui_equation, 'amp * 2.71**(-((var-midpoint)**2 / (2.0 * sigma**2)))')
        
        
    def test_doublegaussian(self):
        dt = equations.DoubleGaussian()
        self.assertEqual(dt.parameters, {'midpoint_2': 0.0, 'midpoint_1': 0.0, 
                                         'amp_2': 1.0, 'amp_1': 0.5, 'sigma_2': 10.0, 
                                         'sigma_1': 20.0})
        self.assertEqual(dt.ui_equation, '(amp_1 * 2.71**(-((var-midpoint_1)**2 / (2.0 * sigma_1**2)))) - '
                                         '(amp_2 * 2.71**(-((var-midpoint_2)**2 / (2.0 * sigma_2**2))))')


    def test_sigmoid(self):
        dt = equations.Sigmoid()
        self.assertEqual(dt.parameters, {'amp': 1.0, 'radius': 5.0, 'sigma': 1.0})
        self.assertEqual(dt.ui_equation, 'amp / (1.0 + 2.71**(-1.8137993642342178 * (radius-var)/sigma))')
        
        
    def test_generalizedsigmoid(self):
        dt = equations.GeneralizedSigmoid() 
        self.assertEqual(dt.parameters, {'high': 1.0, 'midpoint': 1.0, 'sigma': 0.3, 'low': 0.0})
        self.assertEqual(dt.ui_equation, 'low + (high - low) / (1.0 + 2.71**(-1.8137993642342178 * '
                                         '(var-midpoint)/sigma))')
        
        
    def test_sinusoiddata(self):
        dt = equations.Sinusoid()
        self.assertEqual(dt.parameters, {'amp': 1.0, 'frequency': 0.01})
        self.assertEqual(dt.ui_equation, 'amp * sin(6.283185307179586 * frequency * var)')
        
        
    def test_cosine(self):
        dt = equations.Cosine()
        self.assertEqual(dt.parameters, {'amp': 1.0, 'frequency': 0.01})
        self.assertEqual(dt.ui_equation, 'amp * cos(6.283185307179586 * frequency * var)')
        
        
    def test_alpha(self):
        dt = equations.Alpha()
        self.assertEqual(dt.parameters, {'onset': 0.5, 'alpha': 13.0, 'beta': 42.0})
        self.assertEqual(dt.ui_equation, "(alpha * beta) / (beta - alpha) * (2.71**(-alpha * (var-onset)) - "
                                         "2.71**(-beta * (var-onset))) if (var-onset) > 0 else  0.0 * var")
        
        
    def test_pulsetrain(self):
        dt = equations.PulseTrain()
        self.assertEqual(dt.parameters, {'onset': 30.0, 'tau': 13.0, 'T': 42.0, 'amp': 1.0})
        self.assertEqual(dt.ui_equation, 'amp if (var % T) <= tau and var >= onset else 0.0 * var')
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(EquationsTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE) 