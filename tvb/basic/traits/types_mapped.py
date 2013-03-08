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
Mapped super-classes are defined here.

Important:

- Type - traited, possible mapped to db *col*
- MappedType - traited, mapped to db *table*
- MappedStorage - entity saved in file storage also


.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: marmaduke <mw@eml.cc>

"""

import numpy
from scipy import sparse
from tvb.basic.logger.logger import getLogger
from tvb.basic.traits.util import get
from tvb.basic.traits.core import Type, FILE_STORAGE_NONE
from tvb.basic.traits.core import FILE_STORAGE_DEFAULT
from tvb.basic.traits.core import TRAITS_CONFIGURATION
from tvb.basic.traits.types_basic import DType
from tvb.core.entities.file.exceptions import FileStorageException
from tvb.core.entities.file.exceptions import MissingDataSetException


class MappedTypeLight(Type):
    """
    Light base class for all entities which are about to be mapped in storage.
    Current light implementation is to be used with the library stand-alone mode.
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
        summary = dict()
        if TRAITS_CONFIGURATION.use_storage and self.trait.use_storage:
            if included_info is None:
                included_info = self.trait[array_name]._stored_metadata
            summary = self.__read_storage_array_metadata(array_name, included_info)
            if self.METADATA_ARRAY_SHAPE in included_info:
                summary[self.METADATA_ARRAY_SHAPE] = self.get_data_shape(array_name)
        else:
            array_attr = getattr(self, array_name)
            if isinstance(array_attr, numpy.ndarray):
                for key in included_info:
                    if key in self.ALL_METADATA_ARRAY:
                        summary[key] = eval("array_attr." + self.ALL_METADATA_ARRAY[key] + "()")
                    else:
                        self.logger.warning("Not supported meta-data will be ignored "+ str(key))  
        ### Before return, prepare names for UI display.                
        result = dict()
        for key, value in summary.iteritems():
            result[array_name.capitalize().replace("_", " ") + " - " + key] = value
        return result
    
    
    def __read_storage_array_metadata(self, array_name, included_info=None):
        """
        Retrieve from HDF5 specific meta-data about an array.
        """
        summary_hdf5 = self.get_metadata(array_name)
        result = dict()
        if included_info is None:
            if array_name in self.trait:
                included_info = self.trait[array_name]._stored_metadata
            else:
                included_info = []
        for key, value in summary_hdf5.iteritems():
            if key in included_info:
                result[key] = value
        return result
    
# Type - unmapped classes
    
LOG = getLogger(__name__)

class Array(Type):
    """
    Traits type that wraps a NumPy NDArray.

    Initialization requires at least shape, and when not given, will be set to (), an empty, 0-dimension array.
    """

    wraps = numpy.ndarray
    dtype = DType()
    defaults = ( (0, ), {})
    _stored_metadata = MappedTypeLight.ALL_METADATA_ARRAY.keys()
      
      
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
        :param cls: MappedType subclass. When 'inst' is None and only 'cls' is passed, we do not read from storage, but return traited attribute.
        :return value of type self.wraps
        @raise Exception: when read could not be executed, Or when used GET with incompatible attributes (e.g. chunks).
        """
        if inst is None:
            return self
        
        if self.trait.bound:
        
            cached_data = get(inst, '__'+ self.trait.name, None)
            
            if ((cached_data is None or cached_data.size == 0) and self.trait.file_storage != FILE_STORAGE_NONE
                and TRAITS_CONFIGURATION.use_storage and inst.trait.use_storage and isinstance(inst, MappedTypeLight)):
                
                ### Data not already loaded, and storage usage
                cached_data = self._read_from_storage(inst)
                setattr(inst, '__' + self.trait.name, cached_data)
                
            ## Data already loaded, or no storage is used
            return cached_data
        
        else:
            return self
        
        
    def __set__(self, inst, value):
        """
        This is called when an attribute of type Array is set on another class instance.
        :param inst: It is a MappedType instance
        :param value: expected to be of type self.wraps
        @raise Exception: When incompatible type of value is set
        """
        self._put_value_on_instance(inst, self.array_path)
        if isinstance(value, list):
            value = numpy.array(value)
        elif type(value) in (int, float):
            value = numpy.array([value])
            
        setattr(inst, '__' + self.trait.name, value)
        
        if (TRAITS_CONFIGURATION.use_storage and inst.trait.use_storage and value is not None and value.size > 0 
            and (inst is not None and isinstance(inst, MappedTypeLight) 
                 and self.trait.file_storage != FILE_STORAGE_NONE)):
            
            if not isinstance(value, self.trait.wraps):
                raise Exception("Invalid DataType!! It expects %s, but is %s"% str(self.trait.wraps), str(type(value)))
            
            self._write_in_storage(inst, value)
       
       
    def _read_from_storage(self, inst):
        """
        Call correct storage methods, and validation
        :param inst: Will give us the storage_path, it is a MappedType instance
        :return: entity of self.wraps type
        @raise: Exception when used with chunks
        """
        if self.trait.file_storage == FILE_STORAGE_NONE:
            return None
        elif self.trait.file_storage == FILE_STORAGE_DEFAULT:
            try:
                return inst.get_data(self.trait.name, ignore_errors=True)
            except MissingDataSetException, exc:
                LOG.debug("Missing dataSet " + self.trait.name)
                LOG.debug(exc)
                return numpy.ndarray(0)
        else:
            raise FileStorageException("Use get_data(_, slice) not full GET on attributes-stored-in-files!")
        
        
    def _write_in_storage(self, inst, value):
        """
        Store value on disk (in h5 file).
        :param inst: Will give us the storage_path, it is a MappedType instance
        :param value: expected to be of type self.wraps
        @raise Exception : when passed value is incompatible (e.g. used with chunks)  
        """
        if self.trait.file_storage == FILE_STORAGE_NONE:
            pass
        elif self.trait.file_storage == FILE_STORAGE_DEFAULT:
            inst.store_data(self.trait.name, value)
        else:
            raise FileStorageException("You should not use SET on attributes-to-be-stored-in-files!")
           

    def log_debug(self, owner = ""):
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
            LOG.debug("%s: %s shape: %s" % (sts, name, shape))
            LOG.debug("%s: %s actual dtype: %s" % (sts, name, dtype))
            LOG.debug("%s: %s tvb dtype: %s" % (sts, name, tvb_dtype))
            LOG.debug("%s: %s has NaN: %s" % (sts, name, has_nan))
            LOG.debug("%s: %s maximum: %s" % (sts, name, array_max))
            LOG.debug("%s: %s minimum: %s" % (sts, name, array_min))
        else:
            LOG.debug("%s: %s is Empty" % (sts, name))
            
            

class SparseMatrix(Array):
    """
    Map a big matrix.
    Will require storage in File Structure.
    """
    wraps = sparse.csc_matrix 
    defaults = (((1, 1), ), {'dtype': numpy.float64})


    def log_debug(self, owner = ""):
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
            LOG.debug("%s: %s shape: %s" % (sts, name, shape))
            LOG.debug("%s: %s format: %s" % (sts, name, sparse_format))
            LOG.debug("%s: %s number of non-zeros: %s" % (sts, name, nnz))
            LOG.debug("%s: %s dtype: %s" % (sts, name, dtype))
            LOG.debug("%s: %s maximum: %s" % (sts, name, array_max))
            LOG.debug("%s: %s minimum: %s" % (sts, name, array_min))
        else:
            LOG.debug("%s: %s is Empty" % (sts, name))

    
    
    def _read_from_storage(self, inst):
        """
        Overwrite method from superclass, and call Sparse_Matrix specific reader.
        """
        try:
            return self._read_sparse_matrix(inst, self.trait.name)
        except MissingDataSetException, exc:
            LOG.debug("Missing dataSet " + self.trait.name)
            LOG.debug(exc)
            return None
        
    
    def _write_in_storage(self, inst, value):
        """
        Overwrite method from superclass, and call specific Sparse_Matrix writer.
        """
        self._store_sparse_matrix(inst, value, self.trait.name)
    
    
    # ------------------------- STORE and READ sparse matrix to / from HDF5 format 
    ROOT_PATH = "/"
   
    FORMAT_META = "format" 
    DTYPE_META = "dtype" 
    SHAPE_META = "shape" 
    DATA_DS = "data" 
    INDPTR_DS = "indptr" 
    INDICES_DS = "indices" 
    ROWS_DS = "rows" 
    COLS_DS = "cols" 
     
     
    @staticmethod   
    def _store_sparse_matrix(inst, mtx, data_name): 
        """    
        This method stores sparse matrix into H5 file.
        ::param inst: instance on for which to store sparse matrix
        ::param mtx: sparse matrix to store
        ::param data_name: name of data group which will contain sparse matrix details     
        """
        info_dict = {}
        info_dict[SparseMatrix.DTYPE_META] = mtx.dtype.str 
        info_dict[SparseMatrix.SHAPE_META] = str(mtx.shape) 
        info_dict[SparseMatrix.FORMAT_META] = mtx.format 
    
        data_group_path = SparseMatrix.ROOT_PATH + data_name
        
        # Store data and additional info
        inst.store_data(SparseMatrix.DATA_DS, mtx.data, data_group_path) 
        inst.store_data(SparseMatrix.INDPTR_DS, mtx.indptr, data_group_path) 
        inst.store_data(SparseMatrix.INDICES_DS, mtx.indices, data_group_path)
        
        # Store additional info on the group dedicated to sparse matrix
        inst.set_metadata(info_dict, '', True, data_group_path) 
     
    
    @staticmethod
    def _read_sparse_matrix(inst, data_name):
        """
        Reads SparseMatrix from H5 file and returns an instance of such matrix
        ::param inst: instance on for which to read sparse matrix
        ::param data_name: name of data group which contains sparse matrix details
        ::return in instance of sparse matrix with data loaded from H5 file
        """ 
        constructors = {'csr':sparse.csr_matrix, 'csc':sparse.csc_matrix} 
    
        data_group_path = SparseMatrix.ROOT_PATH + data_name
        
        info_dict = inst.get_metadata('', data_group_path)
        
        mtx_format = info_dict[SparseMatrix.FORMAT_META] 
        if not isinstance(mtx_format, str): 
            mtx_format = mtx_format[0] 
    
        dtype = info_dict[SparseMatrix.DTYPE_META] 
        if not isinstance(dtype, str): 
            dtype = dtype[0] 
    
        constructor = constructors[mtx_format] 
    
        if mtx_format in ['csc', 'csr']:
            data =  inst.get_data(SparseMatrix.DATA_DS, where=data_group_path)
            indices = inst.get_data(SparseMatrix.INDICES_DS, where=data_group_path)
            indptr = inst.get_data(SparseMatrix.INDPTR_DS, where=data_group_path)
            shape = eval(info_dict[SparseMatrix.SHAPE_META])
            
            mtx = constructor((data, indices, indptr), shape = shape, dtype = dtype)
            mtx.sort_indices() 
        elif mtx_format == 'coo': 
            data =  inst.get_data(SparseMatrix.DATA_DS, where=data_group_path)
            shape = eval(info_dict[SparseMatrix.SHAPE_META])
            rows =  inst.get_data(SparseMatrix.ROWS_DS, where=data_group_path)
            cols =  inst.get_data(SparseMatrix.COLS_DS, where=data_group_path)
            
            mtx = constructor((data, sparse.c_[rows, cols].T), shape = shape, dtype = dtype ) 
        else: 
            raise Exception("Unsupported format: %s"%mtx_format) 
    
        return mtx 
    
