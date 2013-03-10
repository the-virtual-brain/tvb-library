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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

from tvb.basic.traits.core import TYPE_REGISTER


def get_traited_subclasses(parent_class):
    """
    :param parent_class: SuperClass, to return valid sub-classes of this (e.g. Model).
    :return {class_name: sub_class_instance}
        e.g. {'WilsonCowan': WilsonCowan, ....}
    """
    classes_list = TYPE_REGISTER.subclasses(parent_class)
    result = {}
    for class_instance in classes_list:
        result[class_instance.__name__] = class_instance
    return result


def get_traited_instance_for_name(class_name, parent_class, params_dictionary):  
    """
    :param class_name: Short Traited Class name.
    :param parent_class: Traited basic type expected (e.g. Model)
    :param params_dictionary: dictionary of parameters to be passed to the constructor of the class.
    :return: Class instanciated corresponding to the given name (e.g. FHN() )
    """
    available_subclasses = get_traited_subclasses(parent_class)
    if class_name not in available_subclasses:
        return None
    class_instance = available_subclasses[class_name]
    entity = class_instance(**params_dictionary)
    return entity


    