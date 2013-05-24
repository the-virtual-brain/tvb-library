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

Scientific methods for the Equation datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# from third-party python packages
import numexpr
import numpy

# From "The Virtual Brain"
import tvb.datatypes.equations_data as equations_data

#NOTE: Maybe create a Waveform or PerioodicEquation datatype

class EquationScientific(equations_data.EquationData):
    """ This class exists to add scientific methods to EquationData. """
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Equation type": self.__class__.__name__}
        summary["equation"] = self.trait["equation"].doc
        summary["parameters"] = self.parameters
        return summary
        
    #------------------------------ pattern -----------------------------------#
    def _get_pattern(self):
        """
        Return a discrete representation of the equation.
        """
        return self._pattern
        
    def _set_pattern(self, var):
        """
        Generate a discrete representation of the equation for the space
        represented by ``var``.
        
        The argument ``var`` can represent a distance, or effective distance,
        for each node in a simulation. Or a time, or in principle any arbitrary
        `` space ``. ``var`` can be a single number, a numpy.ndarray or a
        ?scipy.sparse_matrix? TODO: think this last one is true, need to check
        as we need it for LocalConnectivity...
        
        """
        
        self._pattern = numexpr.evaluate(self.equation,
                                         global_dict = self.parameters)
    
    pattern = property(fget=_get_pattern, fset=_set_pattern)
    #--------------------------------------------------------------------------#


class FiniteSupportEquationScientific(equations_data.FiniteSupportEquationData,
                                      EquationScientific):
    """ This class exists to add scientific methods to FiniteSupportEquationData """
    pass


class DiscreteScientific(equations_data.DiscreteData,
                         FiniteSupportEquationScientific):
    """ This class exists to add scientific methods to DiscreteData """
    pass


#class ScalingScientific(equations_data.ScalingData, EquationScientific):
#    """ This class exists to add scientific methods to ScalingData """
#    pass


class LinearScientific(equations_data.LinearData, EquationScientific):
    """ This class exists to add scientific methods to LinearData """
    pass


class GaussianScientific(equations_data.GaussianData,
                         FiniteSupportEquationScientific):
    """ This class exists to add scientific methods to GaussianData """
    pass


class DoubleGaussianScientific(equations_data.DoubleGaussianData,
                               FiniteSupportEquationScientific):
    """ This class exists to add scientific methods to DoubleGaussianData """
    pass


class SigmoidScientific(equations_data.SigmoidData,
                        FiniteSupportEquationScientific):
    """ This class exists to add scientific methods to SigmoidData """
    pass
    

class GeneralizedSigmoidScientific(equations_data.GeneralizedSigmoidData,
                                   EquationScientific):
    """ This class exists to add scientific methods to GeneralizedSigmoidData """
    pass


class SinusoidScientific(equations_data.SinusoidData, EquationScientific):
    """ This class exists to add scientific methods to SinusoidData """
    pass


class CosineScientific(equations_data.CosineData, EquationScientific):
    """ This class exists to add scientific methods to CosineData """
    pass
    
class AlphaScientific(equations_data.AlphaData, EquationScientific):
    """ This class exists to add scientific methods to AlphaData """
    pass
    
class PulseTrainScientific(equations_data.PulseTrainData, EquationScientific):
    """ This class exists to add scientific methods to PulseTrainData """
    
    def _get_pattern(self):
        """
        Return a discrete representation of the equation.
        """
        return self._pattern
        
    def _set_pattern(self, var):
        """
        Generate a discrete representation of the equation for the space
        represented by ``var``.
        
        The argument ``var`` can represent a distance, or effective distance,
        for each node in a simulation. Or a time, or in principle any arbitrary
        `` space ``. ``var`` can be a single number, a numpy.ndarray or a
        ?scipy.sparse_matrix? TODO: think this last one is true, need to check
        as we need it for LocalConnectivity...
        
        """
       
        # rolling in the deep ...  
        onset = self.parameters["onset"]
        off = var < onset 
        var = numpy.roll(var, int(off.sum()+1))
        var[:,0:off.sum()] = 0.0
        self._pattern = numexpr.evaluate(self.equation,
                                         global_dict = self.parameters)
        self._pattern[:,0:off.sum()] = 0.0
    
    pattern = property(fget=_get_pattern, fset=_set_pattern)
        
    
    pass

