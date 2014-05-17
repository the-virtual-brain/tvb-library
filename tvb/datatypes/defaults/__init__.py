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

Offer support to build datatypes instances by reading data from a demo-data folder

"""

try:
    import tvb_data
except Exception:
    print "No tvb_data python module found! You can not use builders without it!"
    exit(1)

import os
import numpy
import tvb_data.connectivity
import tvb_data.sensors
import tvb_data.surfaceData
import tvb_data.projectionMatrix
import tvb.datatypes.surfaces_data as surfaces_data
import tvb.datatypes.sensors_data as sensors_data
from tvb.datatypes.surfaces import make_surface, RegionMapping, LocalConnectivity, Cortex
from tvb.datatypes.connectivity import Connectivity
from tvb.datatypes.sensors import SensorsEEG, SensorsMEG, SensorsInternal
from tvb.datatypes.defaults.core import ZipReader, H5Reader, FileReader



def DConnectivity(source_file="connectivity_74.zip"):

    result = Connectivity()

    source_full_path = source_file
    if not os.path.isabs(source_file):
        source_full_path = os.path.join(os.path.dirname(tvb_data.connectivity.__file__), source_file)

    if source_file.endswith(".h5"):

        reader = H5Reader(source_full_path)

        result.weights = reader.read_field("weights")
        result.centres = reader.read_field("centres")
        result.region_labels = reader.read_field("region_labels")
        result.orientations = reader.read_field("orientations")
        result.cortical = reader.read_field("cortical")
        result.hemispheres = reader.read_field("hemispheres")
        result.areas = reader.read_field("areas")
        result.tract_lengths = reader.read_field("tract_lengths")

    else:
        reader = ZipReader(source_full_path)

        result.weights = reader.read_array_from_file("weights.txt")
        result.centres = reader.read_array_from_file("centres.txt", use_cols=(1, 2, 3))
        result.region_labels = reader.read_array_from_file("centres.txt", dtype="string", use_cols=(0,))
        result.orientations = reader.read_array_from_file("average_orientations.txt")
        result.cortical = reader.read_array_from_file("cortical.txt", dtype=numpy.bool)
        result.hemispheres = reader.read_array_from_file("hemispheres.txt", dtype=numpy.bool)
        result.areas = reader.read_array_from_file("areas.txt")
        result.tract_lengths = reader.read_array_from_file("tract_lengths.txt")

    return result



def DSensors(sensor_type=sensors_data.EEG_POLYMORPHIC_IDENTITY,
             source_file="EEG_unit_vectors_BrainProducts_62.txt.bz2"):

    if sensors_data.EEG_POLYMORPHIC_IDENTITY == sensor_type:
        result = SensorsEEG()
    elif sensors_data.MEG_POLYMORPHIC_IDENTITY == sensor_type:
        result = SensorsMEG()
    else:
        result = SensorsInternal()

    source_full_path = source_file
    if not os.path.isabs(source_file):
        source_full_path = os.path.join(os.path.dirname(tvb_data.sensors.__file__), source_file)

    reader = FileReader(source_full_path)

    result.labels = reader.read_array(dtype="string", use_cols=(0,))
    result.locations = reader.read_array(use_cols=(1, 2, 3))
    if result.has_orientation:
        result.orientations = reader.read_array(use_cols=(4, 5, 6))

    return result


def DSensorsEEG(source_file="EEG_unit_vectors_BrainProducts_62.txt.bz2"):
    return DSensors(sensors_data.EEG_POLYMORPHIC_IDENTITY, source_file)


def DSensorsMEG(source_file="meg_channels_reg13.txt.bz2"):
    return DSensors(sensors_data.MEG_POLYMORPHIC_IDENTITY, source_file)


def DSensorsInternal(source_file="internal_39.txt.bz2"):
    return DSensors(sensors_data.INTERNAL_POLYMORPHIC_IDENTITY, source_file)



def DSurface(surface_type=surfaces_data.CORTICAL,
             source_file=os.path.join("cortex_reg13", "surface_cortex_reg13.zip")):

    source_full_path = source_file
    if not os.path.isabs(source_file):
        source_full_path = os.path.join(os.path.dirname(tvb_data.surfaceData.__file__), source_file)

    reader = ZipReader(source_full_path)

    result = make_surface(surface_type)

    if result is None:
        result = Cortex()
        result.region_mapping_data = DRegionMapping()
        #result.eeg_projection = DProjectionMatrixArray()
        #result.meg_projection = DProjectionMatrixArray()

    result.vertices = reader.read_array_from_file("vertices.txt")
    result.vertex_normals = reader.read_array_from_file("normals.txt")
    result.triangles = reader.read_array_from_file("triangles.txt", dtype=numpy.int32)

    return result


def DCorticalSurface(source_file=os.path.join("cortex_reg13", "surface_cortex_reg13.zip")):
    return DSurface(surfaces_data.CORTICAL, source_file)


def DSkinAir(source_file="outer_skin_4096.zip"):
    return DSurface(surfaces_data.OUTER_SKIN, source_file)


def DBrainSkull(source_file="inner_skull_4096.zip"):
    return DSurface(surfaces_data.INNER_SKULL, source_file)


def DSkullSkin(source_file="outer_skull_4096.zip"):
    return DSurface(surfaces_data.OUTER_SKULL, source_file)


def DEEGCap(source_file="eeg_skin_surface.zip"):
    return DSurface(surfaces_data.EEG_CAP, source_file)


def DFaceSurface(source_file="face_surface_old.zip"):
    return DSurface(surfaces_data.FACE, source_file)


def DCortex(source_file=os.path.join("cortex_reg13", "surface_cortex_reg13.zip")):
    return DSurface(None, source_file)



def DRegionMapping(source_file=os.path.join("cortex_reg13", "all_regions_cortex_reg13.txt")):

    source_full_path = source_file
    if not os.path.isabs(source_file):
        source_full_path = os.path.join(os.path.dirname(tvb_data.surfaceData.__file__), source_file)

    reader = FileReader(source_full_path)

    result = RegionMapping()
    result.array_data = reader.read_array(dtype=numpy.int32)
    return result



def DLocalConnectivity(source_file=os.path.join("cortex_reg13", "local_connectivity_surface_cortex_reg13.mat")):

    source_full_path = source_file
    if not os.path.isabs(source_file):
        source_full_path = os.path.join(os.path.dirname(tvb_data.surfaceData.__file__), source_file)

    reader = FileReader(source_full_path)

    result = LocalConnectivity()
    result.matrix = reader.read_array(matlab_data_name="LocalCoupling")
    return result



def DProjectionMatrixArray(source_file="region_conn_74_eeg_1020_62.mat", matlab_data_name="ProjectionMatrix"):

    source_full_path = source_file
    if not os.path.isabs(source_file):
        source_full_path = os.path.join(os.path.dirname(tvb_data.projectionMatrix.__file__), source_file)

    reader = FileReader(source_full_path)

    return reader.read_array(matlab_data_name=matlab_data_name)


