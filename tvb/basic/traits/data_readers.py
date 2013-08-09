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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import os
import numpy
import inspect
try:
    H5PY_SUPPORT = True
    import h5py as hdf5
except Exception:
    H5PY_SUPPORT = False
    
import tvb.simulator
from scipy import io as scipy_io
from tvb.basic.logger.builder import get_logger
from tvb.basic.traits.util import read_list_data
from tvb.basic.config.settings import TVBSettings


### As current reader will be used in library-mode, all paths are relative to simulator.
ROOT_PATH = os.path.join(os.path.dirname(tvb.simulator.__file__), 'files')



class File(object):
    """
    Will be used for reading default values, when library-profile is selected.
    """

    KEY_PARAMETERS = "parameters"
    KEY_METHOD = "method_name"


    def __init__(self, folder_path, file_name=None):
        self.folder_path = os.path.join(ROOT_PATH, folder_path)
        self.file_name = file_name
        ### Map of references to be used for further reload of default from a different file.
        self.references = {}
        self.logger = get_logger(self.__class__.__module__)


    def read_data(self, file_name=None, matlab_data_name=None, dtype=numpy.float64,
                  skiprows=0, usecols=None, field=None, lazy_load=False):
        """
        Read from given file and sub-file.
        """
        if TVBSettings.TRAITS_CONFIGURATION.use_storage:
            # We want to avoid reading files when no library-mode is used.
            return None

        if field is not None:
            self.references[field] = {self.KEY_PARAMETERS: {'file_name': file_name,
                                                            'matlab_data_name': matlab_data_name,
                                                            'dtype': dtype,
                                                            'skiprows': skiprows,
                                                            'usecols': usecols,
                                                            'field' : field},
                                      self.KEY_METHOD: 'read_data'}
        if lazy_load:
            ## Do not read now, just keep the reference. It will be used on "reload" later.
            return None
        
        # If we are reloading from a h5py we will need to skip check for file_name
        # since a 'non' h5py read will always pass a filename, which will overwrite
        # self.file_name (which is the h5py file in this reload case)
        if self.file_name is not None and self.file_name.endswith('.h5'):
            if H5PY_SUPPORT:
                full_path = os.path.join(self.folder_path, self.file_name)
                return self._read_h5py(full_path, field)
            else:
                self.logger.warning("You need h5py properly installed in order to load from a HDF5 file.")

        if file_name is None:
            file_name = self.file_name
        full_path = os.path.join(self.folder_path, file_name)
        self.logger.debug("Starting to read from: " + str(full_path))

        # Try to read NumPy
        if full_path.endswith('.txt') or full_path.endswith('.txt.bz2'):
            return read_list_data(full_path, dtype=dtype, skiprows=skiprows, usecols=usecols)
        if full_path.endswith('.npz'):
            return numpy.load(full_path)

        # Try to read Matlab format
        return self._read_matlab(full_path, matlab_data_name)

    
    def _read_h5py(self, path, field):
        hfd5_file = hdf5.File(path, 'r', libver='latest')
        return hfd5_file['/' + field][()]
    

    def _read_matlab(self, path, matlab_data_name=None):
        """
        Read array from Matlab file. 
        """
        if path.endswith(".mtx"):
            return scipy_io.mmread(path)

        if path.endswith(".mat"):
            try:
                matlab_data = scipy_io.matlab.loadmat(path)
            except NotImplementedError, exc:
                self.logger.error("Could not read Matlab content from: " + path)
                self.logger.error("Matlab files must be saved in a format <= -V7...")
                raise exc
            return matlab_data[matlab_data_name]


    def __copy__(self):
        return self


    def __deepcopy__(self, memo):
        return self


    def reload(self, target_instance, folder_path, file_name=None):
        """
        Re-read a file, and populate attributes on target_instance, 
        according with previously stored map or references.
        """
        current_class = self.__class__
        new_default = current_class(folder_path, file_name)
        new_default.references = self.references

        for field_name in self.references:
            if not hasattr(target_instance, field_name):
                ## Skip attribute references which might come from subclasses.
                self.logger.debug("Skipped attribute reference: " + field_name + " on instance of "
                                  + target_instance.__class__.__name__)
                continue

            try:
                previous_parameters = self.references[field_name][self.KEY_PARAMETERS]
                method_name = self.references[field_name][self.KEY_METHOD]
                method_call = getattr(new_default, method_name)
                new_value = method_call(**previous_parameters)
                setattr(target_instance, field_name, new_value)

                if inspect.isclass(target_instance):
                    target_instance.trait[field_name].trait.value = new_value
            except Exception, excep:
                self.logger.warning("Could not read data for field " + field_name + " on instance of class "
                                    + target_instance.__class__.__name__ + "\n" + str(excep))

        target_instance.default = new_default



class Table(File):
    """
    A lookup table reload capable map of references.
    """


    def __init__(self, folder_path, file_name=None):
        super(Table, self).__init__(folder_path, file_name)
        self.loaded_table = None
        if file_name is not None:
            self.loaded_table = self.read_data(file_name)


    def read_dimension(self, dimension_1, dimension_2=None, field=None):
        """
        This method will more or less replace in end-usage the method from superclass 'read_data'.
        On a table, this is the method calls we want to persist in references.
        """
        if TVBSettings.TRAITS_CONFIGURATION.use_storage:
            # We want to avoid reading files when no library-mode is used.
            return None

        if field is not None:
            self.references[field] = {self.KEY_PARAMETERS: {'dimension_1': dimension_1,
                                                            'dimension_2': dimension_2},
                                      self.KEY_METHOD: 'read_dimension'}

        if self.loaded_table is None:
            return numpy.array([])

        if dimension_2 is not None:
            return numpy.array(self.loaded_table[dimension_1][dimension_2])

        return numpy.array(self.loaded_table[dimension_1])
    
        
