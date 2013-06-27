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
Mapped super-classes are defined here.

Important:

- Type - traited, possible mapped to db *col*
- MappedType - traited, mapped to db *table*


.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: marmaduke <mw@eml.cc>

"""

import numpy
from scipy import sparse
from tvb.basic.logger.builder import get_logger
from tvb.basic.traits.util import get
from tvb.basic.traits.core import Type
from tvb.basic.traits.types_basic import DType



class MappedTypeLight(Type):
    """
    Light base class for all entities which are about to be mapped in storage.
    Current light implementation is to be used with the scientific-library stand-alone mode.
    """

    METADATA_EXCLUDE_PARAMS = ['id', 'LINKS', 'fk_datatype_group', 'visible', 'disk_size',
                               'fk_from_operation', 'parent_operation', 'fk_parent_burst']

    ### Constants when retrieving meta-data about Array attributes on the current instance.
    METADATA_ARRAY_MAX = "Maximum"
    METADATA_ARRAY_MIN = "Minimum"
    METADATA_ARRAY_MEAN = "Mean"
    METADATA_ARRAY_VAR = "Variance"
    METADATA_ARRAY_SHAPE = "Shape"
    _METADATA_ARRAY_SIZE = "Size"

    ALL_METADATA_ARRAY = {METADATA_ARRAY_MAX: 'max', METADATA_ARRAY_MIN: 'min',
                          METADATA_ARRAY_MEAN: 'mean', METADATA_ARRAY_VAR: 'var',
                          METADATA_ARRAY_SHAPE: 'shape'}

    logger = get_logger(__module__)


    def __init__(self, **kwargs):
        super(MappedTypeLight, self).__init__(**kwargs)
        self._current_metadata = dict()


    def accepted_filters(self):
        """
        Just offer dummy functionality in library mode.
        """
        return {}


    def get_info_about_array(self, array_name, included_info=None):
        """
        :return: dictionary {label: value} about an attribute of type mapped.Array
                 Generic informations, like Max/Min/Mean/Var are to be retrieved for this array_attr
        """
        included_info = included_info or {}
        summary = self.__get_summary_info(array_name, included_info)
        ### Before return, prepare names for UI display.                
        result = dict()
        for key, value in summary.iteritems():
            result[array_name.capitalize().replace("_", " ") + " - " + key] = value
        return result


    def __get_summary_info(self, array_name, included_info):
        """
        Get a summary from the metadata of the current array.
        """
        summary = dict()
        array_attr = getattr(self, array_name)
        if isinstance(array_attr, numpy.ndarray):
            for key in included_info:
                if key in self.ALL_METADATA_ARRAY:
                    summary[key] = eval("array_attr." + self.ALL_METADATA_ARRAY[key] + "()")
                else:
                    self.logger.warning("Not supported meta-data will be ignored " + str(key))
        return summary


    def get_data_shape(self, data_name):
        """
        This method reads data-shape from the given data set
            ::param data_name: Name of the attribute from where to read size
            ::return: a shape tuple
        """
        array_data = getattr(self, data_name)
        if hasattr(array_data, 'shape'):
            return getattr(array_data, 'shape')
        self.logger.warning("Could not find 'shape' attribute on " + str(data_name) + " returning empty shape!!")
        return ()



class Array(Type):
    """
    Traits type that wraps a NumPy NDArray.

    Initialization requires at least shape, and when not given, will be set to (), an empty, 0-dimension array.
    """

    wraps = numpy.ndarray
    dtype = DType()
    defaults = ((0, ), {})
    data = None
    _stored_metadata = MappedTypeLight.ALL_METADATA_ARRAY.keys()
    logger = get_logger(__module__)


    @property
    def shape(self):
        """  
        Property SHAPE for the wrapped array.
        """
        return self.data.shape


    @property
    def array_path(self):
        """  
        Property PATH relative.
        """
        return self.trait.name


    def __get__(self, inst, cls):
        """
        When an attribute of class Array is retrieved on another class.
        :param inst: It is a MappedType instance
        :param cls: MappedType subclass. When 'inst' is None and only 'cls' is passed, we do not read from storage,
                    but return traited attribute.
        :return: value of type self.wraps
        :raise Exception: when read could not be executed, Or when used GET with incompatible attributes (e.g. chunks).
        """
        if inst is None:
            return self

        if self.trait.bound:
            return self._get_cached_data(inst)
        else:
            return self


    def __set__(self, inst, value):
        """
        This is called when an attribute of type Array is set on another class instance.
        :param inst: It is a MappedType instance
        :param value: expected to be of type self.wraps
        :raise Exception: When incompatible type of value is set
        """
        self._put_value_on_instance(inst, self.array_path)
        if isinstance(value, list):
            value = numpy.array(value)
        elif type(value) in (int, float):
            value = numpy.array([value])

        setattr(inst, '__' + self.trait.name, value)


    def _get_cached_data(self, inst):
        """
        Just read from instance since we don't have storage in library mode.
        """
        return get(inst, '__' + self.trait.name, None)


    def log_debug(self, owner=""):
        """
        Simple access to debugging info on a traited array, usage ::
            obj.trait["array_name"].log_debug(owner="obj")
            
        or ::
            self.trait["array_name"].log_debug(owner=self.__class__.__name__)
        """
        name = ".".join((owner, self.trait.name))
        sts = str(self.__class__)
        if self.trait.value is not None and self.trait.value.size != 0:
            shape = str(self.trait.value.shape)
            dtype = str(self.trait.value.dtype)
            tvb_dtype = str(self.trait.value.dtype)
            has_nan = str(numpy.isnan(self.trait.value).any())
            array_max = str(self.trait.value.max())
            array_min = str(self.trait.value.min())
            self.logger.debug("%s: %s shape: %s" % (sts, name, shape))
            self.logger.debug("%s: %s actual dtype: %s" % (sts, name, dtype))
            self.logger.debug("%s: %s tvb dtype: %s" % (sts, name, tvb_dtype))
            self.logger.debug("%s: %s has NaN: %s" % (sts, name, has_nan))
            self.logger.debug("%s: %s maximum: %s" % (sts, name, array_max))
            self.logger.debug("%s: %s minimum: %s" % (sts, name, array_min))
        else:
            self.logger.debug("%s: %s is Empty" % (sts, name))



class SparseMatrix(Array):
    """
    Map a big matrix.
    Will require storage in File Structure.
    """
    wraps = sparse.csc_matrix
    defaults = (((1, 1), ), {'dtype': numpy.float64})
    logger = get_logger(__module__)


    def log_debug(self, owner=""):
        """
        Simple access to debugging info on a traited sparse matrix, usage ::
            obj.trait["sparse_matrix_name"].log_debug(owner="obj")
            
        or ::
            self.trait["sparse_matrix_name"].log_debug(owner=self.__class__.__name__)
        """
        name = ".".join((owner, self.trait.name))
        sts = str(self.__class__)
        if self.trait.value.size != 0:
            shape = str(self.trait.value.shape)
            sparse_format = str(self.trait.value.format)
            nnz = str(self.trait.value.nnz)
            dtype = str(self.trait.value.dtype)
            array_max = str(self.trait.value.data.max())
            array_min = str(self.trait.value.data.min())
            self.logger.debug("%s: %s shape: %s" % (sts, name, shape))
            self.logger.debug("%s: %s format: %s" % (sts, name, sparse_format))
            self.logger.debug("%s: %s number of non-zeros: %s" % (sts, name, nnz))
            self.logger.debug("%s: %s dtype: %s" % (sts, name, dtype))
            self.logger.debug("%s: %s maximum: %s" % (sts, name, array_max))
            self.logger.debug("%s: %s minimum: %s" % (sts, name, array_min))
        else:
            self.logger.debug("%s: %s is Empty" % (sts, name))

