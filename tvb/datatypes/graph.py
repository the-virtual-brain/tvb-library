# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
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

The Graph datatypes. This brings together the scientific and framework methods
that are associated with the Graph datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <paula.sanz-leon@univ-amu.fr>

"""
import numpy
from tvb.basic.logger.builder import get_logger
from tvb.basic.neotraits.api import HasTraits, Attr, NArray, List
from tvb.datatypes import time_series, connectivity

LOG = get_logger(__name__)


class Covariance(HasTraits):
    """Covariance datatype."""

    array_data = NArray(dtype=numpy.complex128) # file_storage=core.FILE_STORAGE_EXPAND
    # FROM ComplexArray: stored_metadata = [key for key in MappedType.DEFAULT_STORED_ARRAY_METADATA if key != MappedType.METADATA_ARRAY_VAR]

    source = Attr(
        field_type=time_series.TimeSeries,
        label="Source time-series",
        doc="Links to the time-series on which NodeCovariance is applied.")

    __generate_table__ = True

    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked
        self.nr_dimensions = self.array_data.ndim
        # for i in range(self.nr_dimensions):
        #     setattr(self, 'length_%dd' % (i + 1), int(self.read_data_shape()[i]))

    def _find_summary_info(self):
        summary = {"Graph type": self.__class__.__name__,
                   "Source": self.source.title}

        summary.update(self.get_info_about_array('array_data'))
        return summary


class CorrelationCoefficients(HasTraits):
    """Correlation coefficients datatype."""

    # Extreme values for pearson Correlation Coefficients
    PEARSON_MIN = -1
    PEARSON_MAX = 1

    array_data = NArray() # file_storage=core.FILE_STORAGE_DEFAULT

    source = Attr(
        field_type=time_series.TimeSeries,
        label="Source time-series",
        doc="Links to the time-series on which Correlation (coefficients) is applied.")

    labels_ordering = List(
        of=str,
        label="Dimension Names",
        default=("Node", "Node", "State Variable", "Mode"),
        doc="""List of strings representing names of each data dimension""")

    __generate_table__ = True

    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked
        self.nr_dimensions = self.array_data.ndim
        # for i in range(self.nr_dimensions):
        #     setattr(self, 'length_%dd' % (i + 1), int(self.read_data_shape()[i]))

    def _find_summary_info(self):
        summary = {"Graph type": self.__class__.__name__,
                   "Source": self.source.title,
                   "Dimensions": self.labels_ordering}
        summary.update(self.get_info_about_array('array_data'))
        return summary

    def get_correlation_data(self, selected_state, selected_mode):
        matrix_to_display = self.array_data[:, :, int(selected_state), int(selected_mode)]
        return list(matrix_to_display.flat)


class ConnectivityMeasure(HasTraits):
    """Measurement of based on a connectivity."""

    array_data = NArray()

    connectivity = Attr(field_type=connectivity.Connectivity)

    def _find_summary_info(self):
        summary = {"Graph type": self.__class__.__name__}
        # summary["Source"] = self.connectivity.title
        summary.update(self.get_info_about_array('array_data'))
        return summary

    __generate_table__ = True
