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
Surface relates DataTypes. This brings together the scientific and framework 
methods that are associated with the surfaces data.

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.surfaces_scientific as surfaces_scientific
import tvb.datatypes.surfaces_framework as surfaces_framework
import tvb.datatypes.surfaces_data as surfaces_data
import tvb.basic.traits.exceptions as exceptions
from tvb.basic.config.settings import TVBSettings as cfg
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)

CORTICAL = surfaces_data.CORTICAL
OUTER_SKIN = surfaces_data.OUTER_SKIN
INNER_SKULL = surfaces_data.INNER_SKULL
OUTER_SKULL = surfaces_data.OUTER_SKULL
EEG_CAP = surfaces_data.EEG_CAP
FACE = surfaces_data.FACE



class Surface(surfaces_scientific.SurfaceScientific, surfaces_framework.SurfaceFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Surface DataType.
    
    ::
        
                            SurfaceData
                                 |
                                / \\
                SurfaceFramework   SurfaceScientific
                                \ /
                                 |
                              Surface
        
    
    """


    def configure(self):
        """
        Make sure both Scientific and Framework configure methods are called.
        """
        surfaces_scientific.SurfaceScientific.configure(self)
        surfaces_framework.SurfaceFramework.configure(self)


    def validate(self):
        """
        This method checks if the data stored into this entity is valid, and ready to be stored in DB.
        Method automatically called just before saving entity in DB.
        In case data is not valid an Exception should be thrown.
        We implement this method here, because the "check" method is in scientific class.
        """
        super(Surface, self).validate()

        # First check if the surface has a valid number of vertices
        if self.number_of_vertices > cfg.MAX_SURFACE_VERTICES_NUMBER:
            msg = "This surface has too many vertices (max allowed: %d)." % cfg.MAX_SURFACE_VERTICES_NUMBER
            msg += " Please upload a new surface or change max number in application settings."
            raise exceptions.ValidationException(msg)

            # Now check if the surface is closed
        is_closed, _, _, _, _ = self.check()
        if not is_closed:
            msg = "Could not import surface because it's not closed.Please correct the problem and upload again."
            raise exceptions.ValidationException(msg)



class CorticalSurface(surfaces_scientific.CorticalSurfaceScientific,
                      surfaces_framework.CorticalSurfaceFramework, Surface):
    """
    This class brings together the scientific and framework methods that are
    associated with the CorticalSurface DataType.
    
    ::
        
                        CorticalSurfaceData
                                 |
                                / \\
        CorticalSurfaceFramework   CorticalSurfaceScientific
                                \ /
                                 |
                          CorticalSurface
        
    
    """
    __mapper_args__ = {'polymorphic_identity': CORTICAL}



class SkinAir(surfaces_scientific.SkinAirScientific, surfaces_framework.SkinAirFramework, Surface):
    """
    This class brings together the scientific and framework methods that are
    associated with the SkinAir DataType.
    
    ::
        
                            SkinAirData
                                 |
                                / \\
                SkinAirFramework   SkinAirScientific
                                \ /
                                 |
                              SkinAir
        
    
    """
    __mapper_args__ = {'polymorphic_identity': OUTER_SKIN}



class BrainSkull(surfaces_scientific.BrainSkullScientific, surfaces_framework.BrainSkullFramework, Surface):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the BrainSkull dataType.
    
    ::
        
                           BrainSkullData
                                 |
                                / \\
             BrainSkullFramework   BrainSkullScientific
                                \ /
                                 |
                             BrainSkull
        
    
    """
    __mapper_args__ = {'polymorphic_identity': INNER_SKULL}



class SkullSkin(surfaces_scientific.SkullSkinScientific, surfaces_framework.SkullSkinFramework, Surface):
    """
    This class brings together the scientific and framework methods that are
    associated with the SkullSkin dataType.
    
    ::
        
                           SkullSkinData
                                 |
                                / \\
              SkullSkinFramework   SkullSkinScientific
                                \ /
                                 |
                             SkullSkin
        
    
    """
    __mapper_args__ = {'polymorphic_identity': OUTER_SKULL}


##--------------------- CLOSE SURFACES End Here---------------------------------------##


##--------------------- OPEN SURFACES Start Here---------------------------------------##


class OpenSurface(surfaces_scientific.OpenSurfaceScientific, surfaces_framework.OpenSurfaceFramework, Surface):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the OpenSurface dataType.
    
    ::
        
                           OpenSurfaceData
                                 |
                                / \\
             OpenSurfaceFramework   OpenSurfaceScientific
                                \ /
                                 |
                             OpenSurface
        
    
    """
    pass



class EEGCap(surfaces_scientific.EEGCapScientific, surfaces_framework.EEGCapFramework, OpenSurface):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the EEGCap dataType.
    
    ::
        
                           EEGCapData
                                 |
                                / \\
             EEGCapFramework   EEGCapScientific
                                \ /
                                 |
                             EEGCap
        
    
    """
    __mapper_args__ = {'polymorphic_identity': EEG_CAP}



class FaceSurface(surfaces_scientific.FaceSurfaceScientific, surfaces_framework.FaceSurfaceFramework, OpenSurface):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the FaceSurface dataType.
    
    ::
        
                           FaceSurfaceData
                                 |
                                / \\
             FaceSurfaceFramework   FaceSurfaceScientific
                                \ /
                                 |
                             FaceSurface
        
    
    """
    __mapper_args__ = {'polymorphic_identity': FACE}

##--------------------- OPEN SURFACES End Here---------------------------------------##


##--------------------- SURFACES ADJIACENT classes start Here---------------------------------------##


class RegionMapping(surfaces_framework.RegionMappingFramework, surfaces_scientific.RegionMappingScientific):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the RegionMapping dataType.
    
    ::
        
                        RegionMappingData
                                 |
                                / \\
          RegionMappingFramework   RegionMappingScientific
                                \ /
                                 |
                          RegionMapping
        
    
    """
    pass



class LocalConnectivity(surfaces_scientific.LocalConnectivityScientific, surfaces_framework.LocalConnectivityFramework):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the LocalConnectivity dataType.
    
    ::
        
                       LocalConnectivityData
                                 |
                                / \\
      LocalConnectivityFramework   LocalConnectivityScientific
                                \ /
                                 |
                         LocalConnectivity
        
    
    """
    pass



class Cortex(surfaces_scientific.CortexScientific, surfaces_framework.CortexFramework, CorticalSurface):
    """ 
    This class brings together the scientific and framework methods that are
    associated with the Cortex dataType.
    
    ::
        
                             CortexData
                                 |
                                / \\
                 CortexFramework   CortexScientific
                                \ /
                                 |
                               Cortex
        
    
    """
    pass

