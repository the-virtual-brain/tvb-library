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

The Data component of the Equation datatypes. These are intended to be 
evaluated via numexp and are used in defining things like stimuli and local 
connectivity.

We only make use of single variable equations, the variable is written as var ?use x?
in the equation...

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Paula Sanz Leon <paula@tvb.invalid>

"""
#TODO: Need to consider a split into zero-mean and not zero-mean for FiniteSupportEquations...
#TODO: Consider adding an attribute of default range, sensible for default parameters...

import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.core as core
from tvb.basic.logger.builder import get_logger


LOG = get_logger(__name__)



class EquationData(basic.MapAsJson, core.Type):
    """
    
    Within the UI we'll access via the specific Equation subclasses implemented
    below.
    
    """
    _base_classes = ['Equation', 'FiniteSupportEquation', "Discrete", "SpatialApplicableEquation",
                     'Coupling', 'CouplingData', 'CouplingScientific', 'CouplingFramework', 
                     #TODO: There should be a refactor of Coupling which may make these unnecessary
                     'LinearCoupling', 'LinearCouplingData', 'LinearCouplingScientific', 'LinearCouplingFramework',
                     'SigmoidalCoupling', 'SigmoidalCouplingData', 'SigmoidalCouplingScientific', 'SigmoidalCouplingFramework']

    equation = basic.String(
        label = "Equation as a string",
        doc = """A latex representation of the equation, with the extra
            escaping needed for interpretation via sphinx.""")
    
    parameters = basic.Dict(
        label = "Parameters in a dictionary.", 
        default = {},
        doc = """Should be a list of the parameters and their meaning, Traits
            should be able to take defaults and sensible ranges from any 
            traited information that was provided.""")
    


class FiniteSupportEquationData(EquationData):
    """
    Equations that decay to zero as the variable moves away from zero. It is 
    necessary to restrict spatial equation evaluated on a surface to this 
    class, are . The main purpose of this class is to facilitate filtering in the UI.
    """
    pass



class DiscreteData(FiniteSupportEquationData):
    """
    A special case for 'discrete' spaces, such as the regions, where each point
    in the space is effectively just assigned a value.
    """

    equation = basic.String( 
        label = "Discrete Equation",
        default = "var",
        locked = True,
        doc = """The equation defines a function of :math:`x`""")


#class ScalingData(EquationData):
#    """
#    """
#
#    equation = basic.String( 
#        label = "Scaling Equation",
#        default = "amp * var",
#        locked = True,
#        doc = """:math:`result = amp * x`""")
#    
#    parameters = basic.Dict( 
#        label = "Scaling Parameters",
#        default = {"amp": 1.0})


class LinearData(EquationData):
    """
    A linear equation.
    """

    equation = basic.String( 
        label = "Linear Equation",
        default = "a * var + b",
        locked = True,
        doc = """:math:`result = a * x + b`""")
    
    parameters = basic.Dict( 
        label = "Linear Parameters",
        default = {"a": 1.0,
                   "b": 0.0})



class GaussianData(FiniteSupportEquationData):
    """
    A Gaussian equation.
    """

    equation = basic.String( 
        label = "Gaussian Equation",
        default = "amp * exp(-((var-midpoint)**2 / (2.0 * sigma**2)))",
        locked = True,
        doc = """:math:`amp \\exp\\left(-\\left(\\left(x-midpoint\\right)^2 /
        \\left(2.0 \\sigma^2\\right)\\right)\\right)`""")
    
    parameters = basic.Dict( 
        label = "Gaussian Parameters",
        default = {"amp": 1.0, "sigma": 1.0, "midpoint": 0.0})



class DoubleGaussianData(FiniteSupportEquationData):
    """
    A Mexican-hat function approximated by the difference of Gaussians functions.
    """
    _ui_name = "Mexican-hat"
    
    equation = basic.String( 
        label = "Double Gaussian Equation",
        default = "(amp_1 * exp(-((var-midpoint_1)**2 / (2.0 * sigma_1**2)))) - (amp_2 * exp(-((var-midpoint_2)**2 / (2.0 * sigma_2**2))))",
        locked = True,
        doc = """:math:`amp_1 \\exp\\left(-\\left((x-midpoint_1)^2 / \\left(2.0  
        \\sigma_1^2\\right)\\right)\\right) - 
        amp_2 \\exp\\left(-\\left((x-midpoint_2)^2 / \\left(2.0  
        \\sigma_2^2\\right)\\right)\\right)`""")
    
    parameters = basic.Dict( 
        label = "Double Gaussian Parameters",
        default = {"amp_1": 0.5, "sigma_1": 20.0, "midpoint_1": 0.0,
                   "amp_2": 1.0, "sigma_2": 10.0, "midpoint_2": 0.0})



class SigmoidData(FiniteSupportEquationData):
    """
    A Sigmoid equation.
    """

    equation = basic.String( 
        label = "Sigmoid Equation",
        default = "amp / (1.0 + exp(-1.8137993642342178 * (radius-var)/sigma))",
        locked = True,
        doc = """:math:`amp / (1.0 + \\exp(-\\pi/\\sqrt(3.0) 
            (radius-x)/\\sigma))`""")
    
    parameters = basic.Dict( 
        label = "Sigmoid Parameters",
        default = {"amp": 1.0, "radius": 5.0, "sigma": 1.0}) #"pi": numpy.pi,



class GeneralizedSigmoidData(EquationData):
    """
    A General Sigmoid equation.
    """
    
    equation = basic.String(
        label = "Generalized Sigmoid Equation",
        default = "low + (high - low) / (1.0 + exp(-1.8137993642342178 * (var-midpoint)/sigma))",
        locked = True,
        doc = """:math:`low + (high - low) / (1.0 + \\exp(-\\pi/\\sqrt(3.0) 
            (x-midpoint)/\\sigma))`""")
    
    parameters = basic.Dict( 
        label = "Sigmoid Parameters",
        default = {"low": 0.0, "high": 1.0, "midpoint": 1.0, "sigma": 0.3}) #, 
                   #"pi": numpy.pi})



class SinusoidData(EquationData):
    """
    A Sinusoid equation.
    """
    
    equation = basic.String(  
        label = "Sinusoid Equation",
        default = "amp * sin(6.283185307179586 * frequency * var)",
        locked = True,
        doc = """:math:`amp \\sin(2.0 \\pi frequency x)` """)
    
    parameters = basic.Dict( 
        label = "Sinusoid Parameters",
        default = {"amp": 1.0, "frequency": 0.01}) #kHz #"pi": numpy.pi,
       


class CosineData(EquationData):
    """
    A Cosine equation.
    """
    
    equation = basic.String(  
        label = "Cosine Equation",
        default = "amp * cos(6.283185307179586 * frequency * var)",
        locked = True,
        doc = """:math:`amp \\cos(2.0 \\pi frequency x)` """)
    
    parameters = basic.Dict( 
        label = "Cosine Parameters",
        default = {"amp": 1.0, "frequency": 0.01}) #kHz #"pi": numpy.pi, 



class AlphaData(EquationData):
    """
    An Alpha function belonging to the Exponential function family.
    """
    
    equation = basic.String( 
        label = "Alpha Equation",
        default = "where((var-onset) > 0, (alpha * beta) / (beta - alpha) * (exp(-alpha * (var-onset)) - exp(-beta * (var-onset))), 0.0 * var)",
        locked = True,
        doc = """:math:`(\\alpha * \\beta) / (\\beta - \\alpha) * 
            (\\exp(-\\alpha * (x-onset)) - \\exp(-\\beta * (x-onset)))` for :math:`(x-onset) > 0`""")
    
    parameters = basic.Dict( 
        label = "Alpha Parameters",
        default = {"onset": 0.5, "alpha": 13.0, "beta":  42.0})


class PulseTrainData(EquationData):
    """
    A pulse train , offseted with respect to the time axis.
    
    Parameters:
        :math:`\\tau` :  pulse width or pulse duration
        :math:`T`     :  pulse repetition period
        :math:`f`     :  pulse repetition frequency (1/T)
        duty cycle    :  :math:``\\frac{\\tau}{T} (for a square wave: 0.5)
        onset time    :
    """
    
    equation = basic.String(
        label = "Pulse Train",
        default = "where((var % T) < tau, amp, 0)",
        locked = True,
        doc = """:math:`\\frac{\\tau}{T} 
        +\sum_{n=1}^{\\infty}\\frac{2}{n\\pi}
        \\sin\\left(\\frac{\\pin\\tau}{T}\\right)
        \\cos\\left(\\frac{2\\pi\\,n}{T} var\\right)`. 
        The starting time is halfway through the first pulse. 
        The phase can be offset t with t - tau/2""")
        
     # onset is in milliseconds
     # T and tau are in milliseconds as well
        
    parameters = basic.Dict(
        default = {"T": 42.0, "tau": 13.0, "amp": 1.0, "onset": 30.0},   
        label = "Pulse Train Parameters")
    

        


