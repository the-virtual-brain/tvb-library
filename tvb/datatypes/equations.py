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

    
    
    

