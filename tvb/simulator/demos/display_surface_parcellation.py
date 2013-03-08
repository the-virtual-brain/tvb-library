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

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy

import tvb.datatypes.surfaces as surfaces_module
    
from tvb.simulator.region_boundaries import RegionBoundaries
from tvb.simulator.region_colours import RegionColours 

from tvb.simulator.plot.tools import * 

CORTEX = surfaces_module.Cortex()
CORTEX_BOUNDARIES = RegionBoundaries(CORTEX)

region_colours = RegionColours(CORTEX_BOUNDARIES.region_neighbours)
colouring = region_colours.back_track()

#Make the hemispheres symetric #TODO: should prob. et colouring for one hemisphere then just stack two copies...
number_of_regions = len(CORTEX_BOUNDARIES.region_neighbours)
for k in range(int(number_of_regions/2)):
    colouring[k+int(number_of_regions/2)] = colouring[k]


mapping_colours = list("rgbcmyRGBCMY")
colour_rgb = {"r": numpy.array([255,   0,   0], dtype=numpy.uint8),
              "g": numpy.array([  0, 255,   0], dtype=numpy.uint8),
              "b": numpy.array([  0,   0, 255], dtype=numpy.uint8),
              "c": numpy.array([  0, 255, 255], dtype=numpy.uint8),
              "m": numpy.array([255,   0, 255], dtype=numpy.uint8),
              "y": numpy.array([255, 255,   0], dtype=numpy.uint8),
              "R": numpy.array([128,   0,   0], dtype=numpy.uint8),
              "G": numpy.array([  0, 128,   0], dtype=numpy.uint8),
              "B": numpy.array([  0,   0, 128], dtype=numpy.uint8),
              "C": numpy.array([  0, 128, 128], dtype=numpy.uint8),
              "M": numpy.array([128,   0, 128], dtype=numpy.uint8),
              "Y": numpy.array([128, 128,   0], dtype=numpy.uint8)}


(surf_mesh, bpts) = surface_parcellation(CORTEX_BOUNDARIES, colouring, mapping_colours, colour_rgb, white_matter)



##- EoF -##
