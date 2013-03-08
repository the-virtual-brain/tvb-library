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
Framework methods for the Connectivity datatype.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
"""

import numpy
import tvb.datatypes.connectivity_data as connectivity_data

class ConnectivityFramework(connectivity_data.ConnectivityData):
    """ 
    This class exists to add framework methods and attributes to Connectivity.
    """
    
    __tablename__ = None
    

    def generate_new_connectivity(self, new_weights, interest_areas, storage_path):
        """
        Generate new Connectivity object based on current one, by changing
        weights (e.g. simulate leasion).
        """
        if isinstance(new_weights, str) or isinstance(new_weights, unicode):
            new_weights = eval(new_weights)
            interest_areas = eval(interest_areas)
        
        for i in range(len(new_weights)):
            for j in range(len(new_weights)):
                new_weights[i][j] = numpy.float(new_weights[i][j])
        for i in range(len(interest_areas)):
            interest_areas[i] = int(interest_areas[i]) 
                     
        final_weights = []
        for i in range(len(self.weights)):
            weight_line = []
            for j in range(len(self.weights)):
                if (interest_areas and i in interest_areas and j in interest_areas):
                    weight_line.append(new_weights[i][j])
                else:
                    weight_line.append(0)
            final_weights.append(weight_line)
        final_conn = (self.__class__)()
        final_conn.parent_connectivity = self.gid
        final_conn.storage_path = storage_path
        final_conn.nose_correction = self.nose_correction
        final_conn.weights = final_weights
        final_conn.centres = self.centres
        final_conn.region_labels = self.region_labels
        final_conn.orientations = self.orientations
        final_conn.cortical = self.cortical
        final_conn.hemispheres = self.hemispheres
        final_conn.areas = self.areas
        final_conn.tract_lengths = self.tract_lengths
        final_conn.saved_selection = interest_areas
        final_conn.subject = self.subject
        return final_conn


    @property
    def saved_selection_labels(self):
        """
        Taking the entity field saved_selection, convert indexes in that array
        into labels.
        """
        if self.saved_selection:
            idxs = [int(i) for i in self.saved_selection]
            result = ''
            for i in idxs:
                result += self.region_labels[i] + ','
            return result[:-1]
        else:
            return ''


    @staticmethod  
    def accepted_filters():
        filters = connectivity_data.ConnectivityData.accepted_filters()
        filters.update({'datatype_class._number_of_regions': {'type': 'int', 'display':'No of Regions',
                                                              'operations': ['==', '<', '>']}})
        return filters


