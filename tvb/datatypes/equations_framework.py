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

Framework methods for the Equation datatypes.

.. moduleauthor:: Ionel Ortelecan <ionel.ortelecan@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import re
import json
import parser
import numpy
import tvb.datatypes.equations_data as equations_data
import tvb.basic.traits.parameters_factory as parameters_factory
from tvb.basic.logger.builder import get_logger


LOG = get_logger(__name__)

# In how many points should the equation be evaluated for the plot. Increasing this will
# give smoother results at the cost of some performance
DEFAULT_PLOT_GRANULARITY = 1024



class EquationFramework(equations_data.EquationData):
    """ This class exists to add framework methods to EquationData. """
    __tablename__ = None


    @property
    def ui_equation(self):
        """
        The string representation of this equation that will be used for computing the values in certain points.

        Because some equations contains operations that python doesn't know how to interpret
        we replaced those operations with others known by python.
        E.g.: exp($expression) replaced with 2.71**($expression)
        """
        return self.equation


    def get_parsed_equation(self):
        """
        Parses the string representation of the equation and replaces
        all the parameters placeholders with their values.
        """
        equation_str = self.ui_equation
        for param in self.parameters:
            equation_str = re.sub('\\b' + param + '\\b', str(self.parameters[param]), equation_str)
        return equation_str


    def get_series_data(self, min_range=0, max_range=100, step=None):
        """
        NOTE: The symbol from the equation which varies should be named: var
        Returns the series data needed for plotting this equation.
        """
        if step is None:
            step = float(max_range - min_range) / DEFAULT_PLOT_GRANULARITY

        from math import sin, cos, sqrt, exp

        result = []
        parsed_equation = self.get_parsed_equation()
        parsed_equation = parser.expr(parsed_equation).compile()
        last_valid_point_value = 0
        was_exception_thrown = False
        for var in numpy.arange(min_range, max_range + step, step):
            try:
                point_value = eval(parsed_equation)
                #the number should have max 20 decimals
                point_value = round(point_value, 19)
                result.append([float(var), point_value])
                last_valid_point_value = point_value
            except OverflowError, exc:
                LOG.exception(exc)
                LOG.error("Could not evaluate the equation at step var = " + str(var))
                result.append([var, last_valid_point_value])
                was_exception_thrown = True
        return result, was_exception_thrown


        ## TODO Try to make the commented code bellow usable. Currently it is not.
        # result = []
        # try:
        #     x_array = numpy.arange(min_range, max_range + step, step)
        #     self.pattern = x_array
        #     y_array = self.pattern
        #     for i in numpy.arrange(0, x_array.size):
        #         result.append([float(x_array[i]), round(y_array[i], 19)])
        #
        # except Exception, exc:
        #     LOG.exception(exc)
        #     LOG.error("Could not evaluate the equation")
        #     was_exception_thrown = True
        #
        # return result, was_exception_thrown



    @staticmethod
    def build_equation_from_dict(equation_field_name, submitted_data_dict, alter_submitted_dictionary=False):
        """
        Builds from the given data dictionary the equation for the specified field name.
        The dictionary should have the data collapsed.
        """
        equation = None
        if equation_field_name in submitted_data_dict:
            equation_type = submitted_data_dict[equation_field_name]
            equation_parameters = {}
            eq_param_str = equation_field_name + '_parameters'

            if eq_param_str in submitted_data_dict and 'parameters' in submitted_data_dict[eq_param_str]:
                equation_parameters = submitted_data_dict[eq_param_str]['parameters']
            if eq_param_str in submitted_data_dict and 'parameters_parameters' in submitted_data_dict[eq_param_str]:
                equation_parameters = submitted_data_dict[eq_param_str]['parameters_parameters']
            equation = parameters_factory.get_traited_instance_for_name(equation_type, equations_data.EquationData,
                                                                        {'parameters': equation_parameters})
            if alter_submitted_dictionary:
                del submitted_data_dict[eq_param_str]
                submitted_data_dict[equation_field_name] = equation

        return equation


    @staticmethod
    def to_json(entity):
        """
        Returns the json representation of this equation.

        The representation of an equation is a dictionary with the following form:
        {'equation_type': '$equation_type', 'parameters': {'$param_name': '$param_value', ...}}
        """
        if entity is not None:
            result = {'__mapped_module': entity.__class__.__module__,
                      '__mapped_class': entity.__class__.__name__,
                      'parameters': entity.parameters}
            return json.dumps(result)
        return None


    @staticmethod
    def from_json(string):
        """
        Retrieves an instance to an equation represented as JSON.

        :param string: the JSON representation of the equation
        :returns: a `tvb.datatypes.equations_data` equation instance
        """
        loaded_dict = json.loads(string)
        if loaded_dict is None:
            return None
        modulename = loaded_dict['__mapped_module']
        classname = loaded_dict['__mapped_class']
        module_entity = __import__(modulename, globals(), locals(), [classname])
        class_entity = eval('module_entity.' + classname)
        loaded_instance = class_entity()
        loaded_instance.parameters = loaded_dict['parameters']
        return loaded_instance



class DiscreteEquationFramework(equations_data.DiscreteEquationData, EquationFramework):
    """ This class exists to add framework methods to DiscreteData """
    pass



class LinearFramework(equations_data.LinearData, EquationFramework):
    """ This class exists to add framework methods to LinearData """
    pass



class GaussianFramework(equations_data.GaussianData, EquationFramework):
    """ This class exists to add framework methods to GaussianData """


    @property
    def ui_equation(self):
        return "amp * 2.71**(-((var-midpoint)**2 / (2.0 * sigma**2)))"



class DoubleGaussianFramework(equations_data.DoubleGaussianData, EquationFramework):
    """ This class exists to add framework methods to DoubleGaussianData """


    @property
    def ui_equation(self):
        return "(amp_1 * 2.71**(-((var-midpoint_1)**2 / (2.0 * sigma_1**2)))) - (amp_2 * 2.71**(-((var-midpoint_2)**2 / (2.0 * sigma_2**2))))"



class SigmoidFramework(equations_data.SigmoidData, EquationFramework):
    """ This class exists to add framework methods to SigmoidData """


    @property
    def ui_equation(self):
        return "amp / (1.0 + 2.71**(-1.8137993642342178 * (radius-var)/sigma))"



class GeneralizedSigmoidFramework(equations_data.GeneralizedSigmoidData, EquationFramework):
    """ This class exists to add framework methods to GeneralizedSigmoidData """


    @property
    def ui_equation(self):
        return "low + (high - low) / (1.0 + 2.71**(-1.8137993642342178 * (var-midpoint)/sigma))"



class SinusoidFramework(equations_data.SinusoidData, EquationFramework):
    """ This class exists to add framework methods to SinusoidData """
    pass



class CosineFramework(equations_data.CosineData, EquationFramework):
    """ This class exists to add framework methods to CosineData """
    pass



class AlphaFramework(equations_data.AlphaData, EquationFramework):
    """ This class exists to add framework methods to AlphaData """


    @property
    def ui_equation(self):
        return "(alpha * beta) / (beta - alpha) * (2.71**(-alpha * (var-onset)) - 2.71**(-beta * (var-onset))) if (var-onset) > 0 else  0.0 * var"



class PulseTrainFramework(equations_data.PulseTrainData, EquationFramework):
    """ This class exists to add framework methods to PulseTrainData """


    @property
    def ui_equation(self):
        return "amp if (var % T) <= tau and var >= onset else 0.0 * var"



class GammaFramework(equations_data.GammaData, EquationFramework):
    """ This class exists to add framework methods to GammaData """
    pass



class DoubleExponentialFramework(equations_data.DoubleExponentialData, EquationFramework):
    """ This class exists to add framework methods to GammaData """
    pass



class FirstOrderVolterraFramework(equations_data.DoubleExponentialData, EquationFramework):
    """ This class exists to add framework methods to GammaData """
    pass


class MixtureOfGammasFramework(equations_data.MixtureOfGammasData, EquationFramework):
    """ This class exists to add framework methods to GammaData """
    pass
    
    