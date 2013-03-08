# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution, clinical use or commercial re-sale is permitted.
# Usage-license is only granted for personal or academic usage.
# You may change sources for your private or academic use.
# If you want to contribute to the project, you need to sign a contributor's license. 
# Please contact info@thevirtualbrain.org for further details.
# Neither the name of Baycrest nor the names of any TVB contributors may be used to endorse or 
# promote products or services derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY BAYCREST ''AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL BAYCREST BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
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

