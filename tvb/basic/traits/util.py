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
All the little functions that make life nicer in the Traits package.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: marmaduke <duke@eml.cc>
"""
import numpy
import collections, inspect  
from tvb.config import TVBSettings



# returns true if key is, by convention, public
ispublic = lambda key: key[0] is not '_'


def str_class_name(thing, short_form = False):
    """
    A helper function that tries to generate an informative name for its
    argument: when passed a class, return its name, when passed an object
    return a string representation of that value.
    """
    # if thing is a class, it has attribute __name__
    if hasattr(thing, '__name__'):
        cls = thing
        if short_form:
            return cls.__name__
        return cls.__module__ + '.' + cls.__name__
    else:
        # otherwise, it's an object and we return its __str__
        return str(thing)


def get(obj, key, default = None):
    """
    get() is a general function allowing us to ignore whether we are
    getting from a dictionary or object. If obj is a dictionary, we
    return the value corresponding to key, otherwise we return the
    attribute on obj corresponding to key. In both cases, if key
    does not exist, default is returned.
    """
    if type(obj) is dict:
        return obj.get(key, default)
    else:
        return getattr(obj, key) if hasattr(obj, key) else default

   
def log_debug_array(log, array, array_name, owner=""):
    """
    Simple access to debugging info on an array.
    """
    if TVBSettings.TRAITS_CONFIGURATION.use_storage:
        return
        # Hide this logs in web-mode, with storage, because we have multiple storage exceptions
        
    if owner != "":
        name = ".".join((owner, array_name))
    else:
        name = array_name
    
    if array is not None and hasattr(array, 'shape'):
        shape = str(array.shape)
        dtype = str(array.dtype)
        has_nan = str(numpy.isnan(array).any())
        array_max = str(array.max())
        array_min = str(array.min())
        log.debug("%s shape: %s" % (name, shape))
        log.debug("%s dtype: %s" % (name, dtype))
        log.debug("%s has NaN: %s" % (name, has_nan))
        log.debug("%s maximum: %s" % (name, array_max))
        log.debug("%s minimum: %s" % (name, array_min))
    else:
        log.debug("%s is None or not Array" % (name))



Args = collections.namedtuple('Args', 'pos kwd')


class TypeRegister(list):
    """
    TypeRegister is a smart list that can be queried to obtain selections of the
    classes inheriting from Traits classes.
    """

    def subclasses(self, obj, avoid_subclasses = False):
        """
        The subclasses method takes a class (or given instance object, will use
        the class of the instance), and returns a list of all options known to
        this TypeRegister that are direct subclasses of the class or have the
        class in their base class list.
        :param obj: Class or instance
        :param avoid_subclasses: When specified, subclasses are not retrieved, only current class.
        """

        cls = obj if inspect.isclass(obj) else obj.__class__
        
        if avoid_subclasses:
            return [cls]
        
        if hasattr(cls, '_base_classes'):
            bases = cls._base_classes
        else:
            bases = []

        sublcasses = [opt for opt in self if (issubclass(opt, cls) or cls in opt.__bases__) 
                                    and not inspect.isabstract(opt) and opt.__name__ not in bases]
        return sublcasses



 
