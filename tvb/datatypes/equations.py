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

The Equation datatypes. This brings together the scientific and framework 
methods that are associated with the Equation datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.equations_scientific as equations_scientific
import tvb.datatypes.equations_framework as equations_framework
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class Equation(equations_scientific.EquationScientific, equations_framework.EquationFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Equation dataTypes.
    
    ::
        
                           EquationData
                                 |
                                / \\
               EquationFramework   EquationScientific
                                \ /
                                 |
                              Equation
        
    
    """
    pass


class FiniteSupportEquation(equations_scientific.FiniteSupportEquationScientific,
                            equations_framework.FiniteSupportEquationFramework,
                            Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the FiniteSupportEquation dataTypes.
    
    ::
        
                           FiniteSupportEquationData
                                       |
                                      / \\
        FiniteSupportEquationFramework   FiniteSupportEquationScientific
                                      \ /
                                       |
                              FiniteSupportEquation
        
    
    """
    pass

class SpatialApplicableEquation(Equation):
    pass


class Discrete(equations_scientific.DiscreteScientific,
               equations_framework.DiscreteFramework, FiniteSupportEquation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Discrete datatypes.
    
    ::
        
                           DiscreteData
                                 |
                                / \\
               DiscreteFramework   DiscreteScientific
                                \ /
                                 |
                              Discrete
        
    
    """
    pass


#class Scaling(equations_scientific.ScalingScientific,
#            equations_framework.ScalingFramework, Equation):
#    """
#    This class brings together the scientific and framework methods that are
#    associated with the Scaling datatypes.
#    
#    ::
#        
#                            ScalingData
#                                 |
#                                / \\
#                ScalingFramework   ScalingScientific
#                                \ /
#                                 |
#                              Scaling
#        
#    
#    """
#    pass


class Linear(equations_scientific.LinearScientific,
            equations_framework.LinearFramework, Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Linear datatypes.
    
    ::
        
                             LinearData
                                 |
                                / \\
                 LinearFramework   LinearScientific
                                \ /
                                 |
                               Linear
        
    
    """
    pass


class Gaussian(equations_scientific.GaussianScientific,
               equations_framework.GaussianFramework, SpatialApplicableEquation, FiniteSupportEquation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Gaussian datatypes.
    
    ::
        
                           GaussianData
                                 |
                                / \\
               GaussianFramework   GaussianScientific
                                \ /
                                 |
                              Gaussian
        
    
    """
    pass


class DoubleGaussian(equations_scientific.DoubleGaussianScientific,
               equations_framework.DoubleGaussianFramework, FiniteSupportEquation):
    """
    This class brings together the scientific and framework methods that are
    associated with the DoubleGaussian datatypes.
    
    ::
        
                         DoubleGaussianData
                                 |
                                / \\
         DoubleGaussianFramework   DoubleGaussianScientific
                                \ /
                                 |
                            DoubleGaussian
        
    
    """
    pass


class Sigmoid(equations_scientific.SigmoidScientific,
               equations_framework.SigmoidFramework, SpatialApplicableEquation, FiniteSupportEquation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Sigmoid datatypes.
    
    ::
        
                            SigmoidData
                                 |
                                / \\
                SigmoidFramework   SigmoidScientific
                                \ /
                                 |
                              Sigmoid
        
    
    """
    pass


class GeneralizedSigmoid(equations_scientific.GeneralizedSigmoidScientific,
               equations_framework.GeneralizedSigmoidFramework, Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Generalized Sigmoid datatypes.
    
    ::
        
                            GeneralizedSigmoidData
                                     |
                                    / \\
         GeneralizedSigmoidFramework   GeneralizedSigmoidScientific
                                    \ /
                                     |
                            GeneralizedSigmoid
        
    
    """
    pass

class Sinusoid(equations_scientific.SinusoidScientific,
               equations_framework.SinusoidFramework, Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Sinusoid datatypes.
    
    ::
        
                           SinusoidData
                                 |
                                / \\
               SinusoidFramework   SinusoidScientific
                                \ /
                                 |
                              Sinusoid
        
    
    """
    pass
    

class Cosine(equations_scientific.CosineScientific,
               equations_framework.CosineFramework, Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Sinusoid datatypes.
    
    ::
        
                           CosineData
                                 |
                                / \\
                 CosineFramework   CosineScientific
                                \ /
                                 |
                              Cosine
        
    
    """
    pass


class Alpha(equations_scientific.AlphaScientific,
            equations_framework.AlphaFramework, Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the Alpha datatypes.
    
    ::
        
                             AlphaData
                                 |
                                / \\
                  AlphaFramework   AlphaScientific
                                \ /
                                 |
                               Alpha
        
    
    """
    pass


class PulseTrain(equations_scientific.PulseTrainScientific,
            equations_framework.PulseTrainFramework, Equation):
    """
    This class brings together the scientific and framework methods that are
    associated with the PulseTrain datatypes.
    
    ::
        
                            PulseTrainData
                                 |
                                / \\
            PulseTrainFramework    PulseScientific
                                \ /
                                 |
                               Pulsetrain
        
    
    """
    pass





if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Equations datatypes initialize without error.
    EQUATION = Equation()
    FINITE_SUPPORT_EQUATION = FiniteSupportEquation()
    DISCRETE = Discrete()
    LINEAR = Linear()
    GAUSSIAN = Gaussian()
    DOUBLE_GAUSSIAN = DoubleGaussian()
    SIGMOID = Sigmoid()
    GENERALIZED_SIGMOID = GeneralizedSigmoid()
    #import pdb
    #pdb.set_trace()
    SINUSOID = Sinusoid()
    ALPHA = Alpha()
    PULSE = PulseTrain()
    
    LOG.info("Default Equation datatypes initialized without error...")
    
    #A display of all the equations
        
    from numpy import linspace
    import pylab
    import numexpr    
    from itertools import izip, count 

    
    EQS = [SINUSOID, ALPHA, GAUSSIAN, DOUBLE_GAUSSIAN, SIGMOID, 
           GENERALIZED_SIGMOID, LINEAR, PULSE]
    
    for i, EQ in izip(count(), EQS):
        var = linspace(-i-50, i+50, 1000)
        #import pdb; pdb.set_trace()
        result = numexpr.evaluate(EQ.equation, global_dict = EQ.parameters)
        pylab.subplot(2, 4, i)
        pylab.plot(var, result, alpha = 0.65)
        pylab.title(str(EQ.__class__.__name__)) #type
    pylab.show()

    
    
    

