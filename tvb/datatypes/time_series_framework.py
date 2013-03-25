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

Framework methods for the TimeSeries datatypes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import json
import numpy
import tvb.datatypes.time_series_data as time_series_data


class TimeSeriesFramework(time_series_data.TimeSeriesData):
    """ This class exists to add framework methods to TimeSeriesData. """
    __tablename__ = None
    
    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        super(TimeSeriesFramework, self).configure()
        data_shape = self.read_data_shape()
        self.nr_dimensions = len(data_shape)
        self.sample_rate = 1.0 / self.sample_period
        for i in range(min(self.nr_dimensions, 4)): 
            setattr(self, 'length_%dd' % (i+1), int(data_shape[i]))
        
        
    def read_data_shape(self):
        """Expose shape read on field data'"""
        return self.get_data_shape('data')
    
    
    def read_data_slice(self, data_slice):
        """Expose chunked-data access """
        return self.get_data('data', data_slice)


    def read_data_shape1(self, kwd=None):
        """
        This is a hack around the fact that FlowController.read_datatype_attribute
        will not call a method on an entity if there are no kwargs.
        """
        return numpy.array(self.read_data_shape())

    def read_time_shape1(self, kwd=None):
        """
        Obtains and returns the shape of the time array.
        """
        return numpy.array(self.get_data_shape('time'))

    def read_time_slice(self, json_slice=None, slice=None):
        """
        Obtains and returns a particular slice of the time array
        """
        sl = slice or json2slice(json_slice)
        return numpy.array(self.get_data('time', sl))
          
    
    def read_time_page(self, current_page, page_size, max_size=None):
        """Compute time for current page."""
        current_page = int(current_page)
        page_size = int(page_size)
        if max_size is None:
            max_size = page_size
        else:
            max_size = int(max_size)
        page_real_size = page_size * self.sample_period
        start_time = self.start_time + current_page * page_real_size
        end_time = start_time + min(page_real_size, max_size * self.sample_period)  
        return numpy.arange(start_time, end_time, self.sample_period)                    
    
    
    def read_channels_page(self, from_idx, to_idx, step=None, specific_slices=None, channels_list=None):
        """
        Read and return only the data page for the specified channels list.
        
        @param from_idx: the starting time idx from which to read data
        @param to_idx: the end time idx up until to which you read data
        @param step: increments in which to read the data. Optional, default to 1.
        @param specific_slices: optional parameter. If speficied slices the data accordingly.
        @param channels_list: the list of channels for which we want data 
        """
        channels_list = json.loads(channels_list)
        if channels_list:
            channels_list = tuple(channels_list)
        else:
            channels_list = slice(None)
        data_page = self.read_data_page(from_idx, to_idx, step, specific_slices)
        # This is just a 1D array like in the case of Global Average monitor. No need for the channels list
        if len(data_page.shape) == 1:
            return data_page.reshape(data_page.shape[0], 1)
        else:
            return data_page[:, channels_list]
    
    
    def read_data_page(self, from_idx, to_idx, step=None, specific_slices=None):
        """
        Retrieve one page of data (paging done based on time).
        """
        from_idx = int(from_idx)
        to_idx = int(to_idx)
        if isinstance(specific_slices, str) or isinstance(specific_slices, unicode):
            specific_slices = json.loads(specific_slices);
        if step == None:
            step = 1
        else:
            step = int(step)
        slices = []
        overall_shape = self.read_data_shape()
        for i in range(len(overall_shape)):
            if i == 0:  ## Time slice
                slices.append(slice(from_idx, min(to_idx, overall_shape[0]), step) )
                continue
            if i == 2:    ## Read full of the main_dimension (space for the simulator)
                slices.append(slice(overall_shape[i]))
                continue
            if specific_slices is None:
                slices.append(slice(0, 1))
            else:
                slices.append(slice(specific_slices[i], min(specific_slices[i] + 1, overall_shape[i]), 1))
        data = self.read_data_slice(tuple(slices))
        if len(data) == 1:
            ## Do not allow time dimension to get squeezed, a 2D result need to come out of this method.
            data = data.squeeze()
            data = data.reshape((1, len(data)))
        else:
            data = data.squeeze()
        return data
    
    def write_time_slice(self, partial_result, expected_rows=None):
        """Append a new value to the ``time`` attribute"""
        self.store_data_chunk("time", partial_result, grow_dimension=0, expected_rows=expected_rows, close_file=False)
    
    
    def write_data_slice(self, partial_result, expected_rows=None):
        """Append a chunk of time-series data to the ``data`` attribute."""
        self.store_data_chunk("data", partial_result, grow_dimension=0, expected_rows=expected_rows, close_file=False)


    def get_min_max_values(self, page_size = 500, specific_slices=None):
        """
        Compute a good approximation for MIN and MAX values of the current array.
        Will be taken in consideration only the 
        """
        first_page = self.read_data_page(0, page_size, specific_slices)
        return numpy.min(first_page), numpy.max(first_page)
    
    
    @staticmethod  
    def accepted_filters():
        filters = time_series_data.TimeSeriesData.accepted_filters()
        filters.update({'datatype_class._nr_dimensions': {'type': 'int', 'display':'No of Dimensions',
                                                          'operations': ['==', '<', '>']},
                        'datatype_class._sample_period': {'type': 'float', 'display':'Sample Period',
                                                          'operations': ['==', '<', '>']},
                        'datatype_class._sample_rate': {'type': 'float', 'display':'Sample Rate',
                                                        'operations': ['==', '<', '>']},
                        'datatype_class._title': {'type': 'string', 'display':'Title',
                                                  'operations': ['==', '!=', 'like']}})
        return filters


    
    
    
class TimeSeriesEEGFramework(time_series_data.TimeSeriesEEGData,
                             TimeSeriesFramework):
    """ This class exists to add framework methods to TimeSeriesEEGData. """
    pass


class TimeSeriesMEGFramework(time_series_data.TimeSeriesMEGData,
                             TimeSeriesFramework):
    """ This class exists to add framework methods to TimeSeriesMEGData. """
    pass


class TimeSeriesRegionFramework(time_series_data.TimeSeriesRegionData,
                                TimeSeriesFramework):
    """ This class exists to add framework methods to TimeSeriesRegionData. """
    pass


class TimeSeriesSurfaceFramework(time_series_data.TimeSeriesSurfaceData,
                                 TimeSeriesFramework):
    """ This class exists to add framework methods to TimeSeriesSurfaceData. """
    pass


class TimeSeriesVolumeFramework(time_series_data.TimeSeriesVolumeData,
                                TimeSeriesFramework):
    """ This class exists to add framework methods to TimeSeriesVolumeData. """
    pass



