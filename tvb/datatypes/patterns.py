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

The Pattern datatypes. This brings together the scientific and framework
methods that are associated with the pattern datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.datatypes.patterns_scientific as patterns_scientific
import tvb.datatypes.patterns_framework as patterns_framework


class SpatialPattern(patterns_scientific.SpatialPatternScientific,
                     patterns_framework.SpatialPatternFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the SpatialPattern datatype.
    
    ::
        
                         SpatialPatternData
                                 |
                                / \\
         SpatialPatternFramework   SpatialPatternScientific
                                \ /
                                 |
                          SpatialPattern
        
    
    """
    pass


class SpatioTemporalPattern(patterns_scientific.SpatioTemporalPatternScientific,
                            patterns_framework.SpatioTemporalPatternFramework, SpatialPattern):
    """
    This class brings together the scientific and framework methods that are
    associated with the SpatioTemporalPattern datatype.
    
    ::
        
                           SpatioTemporalPatternData
                                       |
                                      / \\
        SpatioTemporalPatternFramework   SpatioTemporalPatternScientific
                                      \ /
                                       |
                             SpatioTemporalPattern
        
    
    """


class StimuliRegion(patterns_scientific.StimuliRegionScientific,
                    patterns_framework.StimuliRegionFramework, SpatioTemporalPattern):
    """
    This class brings together the scientific and framework methods that are
    associated with the StimuliRegion datatype.
    
    ::
        
                          StimuliRegionData
                                 |
                                / \\
          StimuliRegionFramework   StimuliRegionScientific
                                \ /
                                 |
                           StimuliRegion
        
    
    """


class StimuliSurface(patterns_scientific.StimuliSurfaceScientific,
                     patterns_framework.StimuliSurfaceFramework, SpatioTemporalPattern):
    """
    This class brings together the scientific and framework methods that are
    associated with the StimuliSurface datatype.
    
    ::
        
                         StimuliSurfaceData
                                 |
                                / \\
         StimuliSurfaceFramework   StimuliSurfaceScientific
                                \ /
                                 |
                          StimuliSurface
        
    
    """


class SpatialPatternVolume(patterns_scientific.SpatialPatternVolumeScientific,
                           patterns_framework.SpatialPatternVolumeFramework, SpatialPattern):
    """
    This class brings together the scientific and framework methods that are
    associated with the SpatialPatternVolume datatype.
    
    ::
        
                            SpatialPatternVolumeData
                                       |
                                      / \\
         SpatialPatternVolumeFramework   SpatialPatternVolumeScientific
                                      \ /
                                       |
                              SpatialPatternVolume
        
    
    """


if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Pattern datatypes initialize without error.
    SPATIAL_PATTERN = SpatialPattern()
    SPATIOTEMPORAL_PATTERN = SpatioTemporalPattern()
    SPATIAL_PATTERN_VOLUME = SpatialPatternVolume()
    STIMULI_REGION = StimuliRegion()
    STIMULI_SURFACE = StimuliSurface()

    LOG.info("Default Pattern datatypes initialized without error...")
