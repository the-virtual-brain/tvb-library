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
.. [AIMA_3rd_2010] Stuart Jonathan Russell, Peter Norvig, *Artificial 
intelligence: a modern approach*, 3rd Edition, Prentice Hall, 2010

This module was written for use in TVB as a way of determining a colouring 
scheme for the parcelated cortex. This represents a constraint satisfaction 
problem (CSP), see [AIMA_3rd_2010]_, chapter 6. The purpose is to return a 
colouring dictionary that satisfies the constraint of a region's colour not
being the same as any of its neighbours on the surface.

::
    import tvb.simulator.surfaces as surfaces_module
    from tvb.simulator.region_boundaries as RegionBoundaries
    CORTEX = surfaces_module.Cortex()  
    CORTEX_BOUNDARIES = RegionBoundaries(CORTEX)
    region_colours = RegionColours(CORTEX_BOUNDARIES.region_neighbours)
    colouring = region_colours.back_track()


.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy

from tvb.simulator.common import get_logger
LOG = get_logger(__name__)


class RegionColours(object):
    """

    ''neighbours'':
        A dictionary specifying the neigbouring regions of each region.

    ''number_of_colours'':
        For a plane or a surface that is topologically spherical there is a
        theorem stating that only four colours are required to colour a surface
        without any neighbours having the same colour.
        NOTE: If you are considering the additional neighbour constraints
            imposed by the colourbar then it may be necessary to have more than
            four colour possibilities.

    """

    #TODO: Trait me...

    def __init__(self, neighbours, number_of_colours=4):
        """
        """
        self._neighbours = neighbours
        self._number_of_colours = number_of_colours
        self._regions = neighbours.keys()
        self._region_degree = [len(neighbours[r]) for r in self.regions]

        max_degree_index = numpy.array(self.region_degree).argmax()
        self._max_degree_region = self.regions[max_degree_index]

        domains = range(self.number_of_colours)
        self.possible_colours = dict()
        for region in self.neighbours:
            self.possible_colours[region] = list(domains) 

        self._colours = None
        self._region_colours = None


    @property
    def neighbours(self):
        """ A dictionary where specifying the neighbours of each region. """
        return self._neighbours


    @property
    def number_of_colours(self):
        """ The number of colours available for colouring the surface. """
        return self._number_of_colours


    @property
    def regions(self):
        """ A list of the regions comprising the surface. """
        return self._regions


    @property
    def region_degree(self):
        """ A list specifying the degree of each region. """
        return self._region_degree


    @property
    def max_degree_region(self):
        """ Maximum degree, variable selection heuristic. """
        return self._max_degree_region


#    @property
#    def region_colours(self):
#        """ A list specifying the colour of each region. """
#        return self.colours[]#Map region assignment to particular colours... 
#
#    
#    def _get_colours(self):
#        return self._colours
#    def _set_colours(self, colours):
#        if len(colours) == self.number_of_colours:
#            self._colours = colours
#        else:
#            LOG.error("A list of colours of length number_pf_colours must be provided")
#    property(colours, get=_get_colours set=_set_colours)


    def assigned(self, assignment):
        """ A list of the assigned regions """
        return [region for region in self.regions if region in assignment]


    def unassigned(self, assignment):
        """ A list of unassigned regions """
        return [region for region in self.regions if region not in assignment]


    def isconsistent(self, region, colour, assignment):
        """
        Check that using "colour" for "region" doesn't conflict with any of the
        colours already assigned to neighbouring regions.
        """
        for neighbour in self.neighbours[region]:
            if neighbour in self.assigned(assignment):
                if assignment[neighbour] == colour:
                    return False
        return True


    def mrv(self, assignment):
        """
        Minimum reamaining values, variable selection heuristic.
        """
        remaining = [len(self.possible_colours[r]) for r in self.unassigned(assignment)]
        return self.unassigned(assignment)[remaining.index(min(remaining))]

    #TODO: Might be good to add or replace with a least used weighting, for max diversity.
    def lcv(self, region):
        """
        Least constraining colour, value selection heuristic.
        """
        def neighbours_have(colour):
            weighted_count = 0.0
            for neighbour  in self.neighbours[region]:
                if colour in self.possible_colours[neighbour]:
                    weighted_count += 1.0 / len(self.possible_colours[neighbour])
            return weighted_count

        return sorted(self.possible_colours[region], key=neighbours_have)


    def forward_check(self, region, assignment):
        """
        Forward checking, inference step.
        """
        removed = dict()
        resolved = list()
        for neighbour in self.neighbours[region]:
            if ((neighbour not in assignment) and
                (assignment[region] in self.possible_colours[neighbour])):
                self.possible_colours[neighbour].remove(assignment[region])
                removed[neighbour] = assignment[region]
            if len(self.possible_colours[neighbour]) == 0:
                return (False, removed, resolved)
            elif len(self.possible_colours[neighbour]) == 1:
                assignment.update({neighbour: self.possible_colours[neighbour][0]})
                resolved.append(neighbour)
        return (True, removed, resolved)


    def iscomplete(self, assignment):
        """
        Checking for completion of assignment.
        """
        return (sorted(assignment.keys()) == sorted(self.regions))


    def back_track(self, assignment=dict()):
        """
        A backtracking algorithm for constraint satisfaction. The algorithm uses
        the degree heuristic for the initial variable selection, subsequent
        regions are selected via the minimum remaining values (MRV) heuristic.
        Colour selection for regions follows a least constraining value (LCV)
        heuristic. The backtracking search is augmented by a simple forward
        checking inference procedure. See, [AIMA_3rd_2010]_, Sec 6.3, Fig 6.5.

        """
        if self.iscomplete(assignment):
            LOG.debug("Solution found, returning assignment...")
            return assignment
        elif assignment == {}:
            region = self.max_degree_region
        else:
            region = self.mrv(assignment)
        #LOG.debug("For region %s" % (str(region)))
        #LOG.debug("Least constraining colour order is: %s" % (str(self.lcv(region))))
        for colour in self.lcv(region):
            if self.isconsistent(region, colour, assignment):
                #LOG.debug("Adding %s to %s" % (str(colour), str(region)))
                assignment.update({region: colour})
                self.possible_colours[region] = [colour]
                safe, removed, resolved = self.forward_check(region, assignment)
                if safe: #safe
                    result = self.back_track(assignment)
                    if result is not None:
                        return result
                #import pdb; pdb.set_trace()
                for neighbour in removed:
                    self.possible_colours[neighbour].append(removed[neighbour])
                for neighbour in resolved:
                    assignment.pop(neighbour)
        assignment.pop(region)
        #import pdb; pdb.set_trace()
        LOG.error("Failed to find an assignment...")
        return None

