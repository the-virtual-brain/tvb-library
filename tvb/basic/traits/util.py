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
import tvb.basic.logger.logger as logger
from tvb.config import TVBSettings

LOG = logger.getLogger(__name__)


# old, placed in interface function, this one is deprecated
MAKE_LABEL = lambda label: label[0].upper() + label[1:] + ": "

# returns true if key is, by convention, public
ispublic = lambda key: key[0] is not '_'

# old, consider placing in interface function as well
def str_class_name(thing, short_form = False):
    """
    A helper function that tries to generate an informative name for its
    argument: when passed a class, return its name, when passed an object
    return a string representation of that value.
    """

    # if thing is a class, it has attr __name__
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


# old, prefer filter_attrs
def yield_stuff(obj, cls):
    """
    This function takes an object or class and yields the names and values for
    those attributes that are instances or subclasses of cls, defaulting to Trait.
    """
    ret = []
    if not isinstance(obj, dict):
        obj = dict((k, getattr(obj, k)) for k in dir(obj))
    for key, val in obj.iteritems():
        is_not_private = not (key[0] == '_')
        is_subclass = isinstance(val, type) and issubclass(val, cls)
        is_instance = isinstance(val, cls)
        if (is_subclass or is_instance) and is_not_private:
            ret.append((key, val))
    return ret

# new, replaces yield_stuff
def filter_attrs(obj, cls):
    """
    filter_attrs takes an object or class and returns a dict of names and values of
    those attributes that are instances or subclasses of cls. This is necessary
    when we have a class and want to know what traits it has:

    >>> traits = filter_attrs(Simulator, Trait)

    but the function is generalized so you can be more specific

    >>> pars = filter_attrs(NeuronModel1, Parameter)

    e.g. to get the attributes of NeuronModel1 that are instances of the class
    Parameter.
    """
    # we return a dictionary at the end
    result = {}

    # if the obj is already a dict, ok, else we get a dict of the
    # object's or class's attributes
    obj = obj if isinstance(obj, dict) else obj.__dict__

    for key, val in obj.iteritems():

        # issubclass throws error if val is not a class,
        # ie. isinstance(val, type), so we check that first
        is_subclass = isinstance(val, type) and issubclass(val, cls)

        # check if it's an instance of cls
        is_instance = isinstance(val, cls)

        # combine those checks, and make sure attr is not private
        if (is_subclass or is_instance) and key[0] is not '_':
            result[key] = val

    return result


def supertget(bases, key, default=None):
    """
    Given a class' bases, supertget retrieves the attribute of the first 
    traited base.

    """
    for base in bases:
        if hasattr(base, 'trait'):
            return getattr(base.trait, key)
        else:
            continue
    if default is not None:
        return default
    else:
        msg = "key %r not found in bases' traits"
        raise KeyError(msg % (key, ))



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
        :param avoid_subclasses: When specified, subclasses are not retrieved, only surrent class 
        """

        cls = obj if inspect.isclass(obj) else obj.__class__
        
        if avoid_subclasses:
            return [cls]
        
        if hasattr(cls, '_base_classes'):
            bases = cls._base_classes
        else:
            bases =[]

        sublcasses = [opt for opt in self if (issubclass(opt, cls) or cls in opt.__bases__) 
                                            and not inspect.isabstract(opt) and opt.__name__ not in bases]
        return sublcasses


class HierStruct(dict):
    """
    HierStruct eases access to values in hierarchical dictionaries, and can be
    initialized from a hierarchical dictionary. For keys that are not valid
    Python identifiers, or for any other reaon, dict style access is style
    possible. Where a requested key does not exist, it is automatically given
    the value of a empty dictionary, for convenience.

        >>> hs = HierStruct(a=3, b={'c': 3, 'd': 6})
        >>> hs.a
        3
        >>> hs.b.d
        6
        >>> hs.g.f = 2.3
        >>> hs.g
        {'f': 2.3}
        >>> hs['g']['f']
        2.3
        >>> [key for key in hs.iterkeys()]
        ['a', 'b', 'g']

    Note that fields are automatically created, which can become unwieldy.

        >>> hs.q.w.e.r.t.y = 23
        >>> hs
        {'a': 3, 'b': {'c': 3, 'd': 6},
         'q': {'w': {'e': {'r': {'t': {'y': 42}}}}}}

    """

    def __init__(self, **kwds):
        super(HierStruct, self).__init__(**kwds)
        for key, val in self.iteritems():
            if type(val) is dict:
                self[key] = HierStruct(**val)

    def __getattr__(self, key):
        sup = super(HierStruct, self)
        if key in self:
            return sup.__getitem__(key)
        else:
            sup.__setitem__(key, HierStruct())
            return sup.__getitem__(key)

    def __setattr__(self, key, val):
        sup = super(HierStruct, self)
        if type(val) is dict:
            sup.__setitem__(key, HierStruct(**val))
        else:
            sup.__setitem__(key, val)


GetItem = collections.namedtuple('GetItem', 'obj')

class Reference(object):

    Attr = collections.namedtuple('Attr', 'key')
    Item = collections.namedtuple('Item', 'key')
    Call = collections.namedtuple('Call', 'args kwds')

    class Item(object):

        def __init__(self, key): 
            self.key = key

        def str_slice(self, slice_):
            result = "%s:%s%s"
            result %= (slice_.start if slice_.start else '',
                   slice_.stop  if slice_.stop  else '',
                   ':' + str(slice_.step) if slice_.step  else '')
            return result

        def idxnotation(self):
            return ', '.join(map(self.str_slice, self.key))

    def __init__(self, ref=[]):
        """
        Reference facilitates the attr-referencing in Trait declarations in the
        body of the owner class, and when a SelfRef instance is called on an
        object, it will try to get the referenced attribute from the object,
        and treats attributes of attribtes references, e.g `obj.x.y`
        appropriately.

            >>> class foo:
            ...     class bar:
            ...         baz = rand(10, 10) # 10 x 10 matrix
            ... 
            >>> a = foo.bar.baz[1, 2]
            >>> ref = Reference()
            >>> b = ref.bar.baz[1, 2](foo)
            >>> a == b
            True

        Slices generated by references produce views on Numpy arrays, when
        applicable. Because Ref/Self (the shortcut instances of Reference defined
        below) can be called, they can be used to generate getter properties:

            >>> from tvb.basic.traits.util import Self
            >>> class foo(object):
            ...     x = 5
            ...     y = property(Self.x)
            ...
            >>> foo().y
            5

        TODO: consider overloading ops so we can reference operations.

        - All references must be in principle equivalent to a function of
          a single argument, the object to which the ref applies

        - If the ref is made a data descriptor, then
            - no need for property()
            - eliminate convention for single arg uses application

        """

        self.ref = ref
        self._fast = False

    def __getattr__(self, key):
        return Reference(self.ref + [self.Attr(key)])

    def __getitem__(self, key):
        if type(key) is slice:
            itemref = self.Item((key,))
        else:
            itemref = self.Item(key)

        return Reference(self.ref + [itemref])

#    def __copy__(self):
#        pass
#
#    def __deepcopy__(self, memo):
#        pass
    
    def __call__(self, _obj=None, **kwds):

        # TODO compile ref at each step in the init. this becomes simpler

        # if we receive an _obj, apply reference to _obj
        if _obj is not None and not self._fast:
            if type(self.ref[0]) is self.Item:
                #if self.ref[0].key in _obj:
                    base = _obj[self.ref[0].key]
                #else:
                #    base = None
                    #LOG.warning("Invalid attribute: " + str(self.ref[0].key))
            elif type(self.ref[0]) is self.Attr:
                if hasattr(_obj, self.ref[0].key):
                    base = getattr(_obj, self.ref[0].key)
                else:
                    base = None
                    #LOG.warning("Invalid attribute: " + str(self.ref[0].key))
            elif type(self.ref[0]) is self.Call:
                call = self.ref[0]
                base = _obj(*call.args, **call.kwds)
            else:
                raise TypeError('bad reference element: %r' % (self.ref[0], ))

            if len(self.ref) == 1:
                return base
            else:
                return Reference(self.ref[1:])(base)

        # use compiled version of reference
        elif self._fast:
            return self._fast(_obj)

        # otherwise, add a call reference
        else:
            return Reference(self.ref + [self.Call((), kwds)])

    def __repr__(self):
        return 'Ref(ref=%r)' % (self.ref,)

    def __str__(self):
        #ops = {'__div__':  '/', '__add__':  '+', '__mul__':  '*',
        #       '__rdiv__': '/', '__radd__': '+', '__rmul__': '*'  }
        sref = 'obj'
        for ref in self.ref:
            if type(ref) is self.Item:
                sref += '[' + ref.idxnotation() + ']'
            elif type(ref) is self.Attr:
                sref += '.' + ref.key
            elif type(ref) is self.Call:
                sref += '('
                sref += ', '.join(map(repr, ref.args))
                sref += ', '.join('%s=%r' % (k, v) 
                                  for k, v in ref.kwds.items())
                sref += ')'

        return sref

    def __refmethcall__(self, meth, args=(), kwds={}):
        call = [self.Attr(meth), self.Call(args, kwds)]
        return Reference(self.ref + call)

    def __div__(self, arg):
        return self.__refmethcall__('__div__', (arg,))

    def __rdiv__(self, arg):
        return self.__refmethcall__('__rdiv__', (arg,))

    def __add__(self, arg):
        return self.__refmethcall__('__add__', (arg,))

    def __radd__(self, arg):
        return self.__refmethcall__('__radd__', (arg,))

    def __mul__(self, arg):
        return self.__refmethcall__('__mul__', (arg,))

    def __rmul__(self, arg):
        return self.__refmethcall__('__rmul__', (arg,))

    def __sub__(self, arg):
        return self.__refmethcall__('__sub__', (arg,))

    def __rsub__(self, arg):
        return self.__refmethcall__('__rsub__', (arg,))

    def _done(self):
        """ return a compiled version of reference """
        self._fast = eval('lambda obj: %s' % (self, ))
        return self

    def __get__(self, inst, owner):
        obj = inst if inst else owner
        return self._done()(obj)

    def __set__(self, obj, val):
        raise AttributeError('cannot assign to reference %s' % (self,))

# semantic convenience
Ref = Reference()
Self = Reference()


    
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


