"""
This module implements neotraits.
It is private only to shield public usage of the imports and logger.
"""
import numpy
import logging
from six import add_metaclass
from ._attr import Attr
from ._declarative_base import _Property, MetaType
from .info import trait_object_str, trait_object_repr_html, narray_summary_info
from .ex import TraitAttributeError, TraitTypeError, TraitValueError, TraitError
import sys

if sys.version_info[0] == 3:
    import typing

# a logger for the whole traits system
log = logging.getLogger('tvb.traits')

# once in python > 3.6 simplify the name book keeping with __set_name__



class CachedTraitProperty(_Property):
    # This is a *non-data* descriptor
    # Once a field with the same name exists on the instance it will
    # take precedence before this non-data descriptor
    # This means that after the first __get__ which sets a same-name instance attribute
    # this will not be called again. Thus this is a cache.
    # To refresh the cache one could delete the instance attr.

    def __get__(self, instance, owner):
        # type: (typing.Optional['HasTraits'], 'MetaType') -> typing.Any
        if instance is None:
            return self
        ret = self.fget(instance)
        # mhtodo the error messages generated by this will be confusing
        # noinspection PyProtectedMember
        ret = self.attr._validate_set(instance, ret)
        # set the instance same-named attribute which becomes the cache
        setattr(instance, self.attr.field_name, ret)
        return ret



class TraitProperty(_Property):

    def __get__(self, instance, owner):
        # type: (typing.Optional['HasTraits'], 'MetaType') -> typing.Any
        if instance is None:
            return self
        ret = self.fget(instance)
        # mhtodo the error messages generated by this will be confusing
        # noinspection PyProtectedMember
        ret = self.attr._validate_set(instance, ret)
        return ret

    def setter(self, fset):
        # return a copy of self that has fset. It will overwrite the current one in the
        # owning class as the attributes have the same name and the setter comes after the getter
        return type(self)(self.fget, self.attr, fset)

    def __set__(self, instance, value):
        # type: ('HasTraits', typing.Any) -> None
        if self.fset is None:
            raise TraitAttributeError("Can't set attribute. Property is read only. In " + str(self))
        # mhtodo the error messages generated by this will be confusing
        # noinspection PyProtectedMember
        value = self.attr._validate_set(instance, value)
        self.fset(instance, value)

    def __delete__(self, instance):
        raise TraitAttributeError("can't delete a traitproperty")

    def __str__(self):
        return 'TraitProperty(attr={}, fget={}'.format(self.attr, self.fget)



def trait_property(attr):
    # type: (Attr) -> typing.Callable[[typing.Callable], TraitProperty]
    """
    A read only property that has a declarative attribute associated with.
    :param attr: the declarative attribute that describes this property
    """
    if not isinstance(attr, Attr):
        raise TypeError('@trait_property(attr) attribute argument required.')

    def deco(func):
        return TraitProperty(func, attr)
    return deco


def cached_trait_property(attr):
    # type: (Attr) -> typing.Callable[[typing.Callable], CachedTraitProperty]
    """
    A lazy evaluated attribute.
    Transforms the decorated method into a cached property.
    The method will be called once to compute a value.
    The value will be stored in an instance attribute with
    the same name as the decorated function.
    :param attr: the declarative attribute that describes this property
    """
    if not isinstance(attr, Attr):
        raise TypeError('@cached_trait_property(attr) attribute argument required.')

    def deco(func):
        return CachedTraitProperty(func, attr)
    return deco


@add_metaclass(MetaType)
class HasTraits(object):
    def __init__(self, **kwargs):
        """
        The default init accepts kwargs for all declarative attrs
        and sets them to the given values
        """
        # cls just to emphasise that the metadata is on the class not on instances
        cls = type(self)

        # defined before the kwargs loop, so that a title Attr can overwrite this defaults

        self.title = '{}'.format(self.__class__.__name__)
        """ a generic name that the user can set to easily recognize the instance """

        for k, v in list(kwargs.items()):
            if k not in cls.declarative_attrs:
                raise TraitTypeError(
                    'Valid kwargs for type {!r} are: {}. You have given: {!r}'.format(
                        cls, repr(cls.declarative_attrs), k
                    )
                )
            setattr(self, k, v)

        self.tags = {}
        """
        a generic collections of tags. The trait system is not using them
        nor should any other code. They should not alter behaviour
        They should describe the instance for the user
        """


    def __str__(self):
        return trait_object_str(self)


    def _repr_html_(self):
        return trait_object_repr_html(self)

    def tag(self, tag_name, tag_value=None):
        # type: (str, str) -> None
        """
        Add a tag to this trait instance.
        The tags are for user to recognize and categorize the instances
        They should never influence the behaviour of the program
        :param tag_name: an arbitrary tag
        :param tag_value: an optional tag value
        """
        self.tags[str(tag_name)] = str(tag_value)


    def validate(self):
        """
        Check that the internal invariants of this class are satisfied.
        Not meant to ensure that that is the case.
        Use configure for that.
        The default configure calls this before it returns.
        It complains about missing required attrs
        Can be overridden in subclasses
        """
        cls = type(self)

        for k in cls.declarative_attrs:
            # read all declarative attributes. This will trigger errors if they are
            # in an invalid state, like beeing required but not set
            getattr(self, k)


    def configure(self, *args, **kwargs):
        """
        Ensures that invariant of the class are satisfied.
        Override to compute uninitialized state of the class.
        """
        self.validate()


    def summary_info(self):
        # type: () -> typing.Dict[str, str]
        """
        A more structured __str__
        A 2 column table represented as a dict of str->str
        The default __str__ and html representations of this object are derived from
        this table.
        Override this method and return such a table filled with instance information
        that informs the user about your instance
        """
        cls = type(self)
        ret = {'Type': cls.__name__}
        if self.title:
            ret['title'] = str(self.title)

        for aname in cls.declarative_attrs:
            try:
                attr_field = getattr(self, aname)
                if isinstance(attr_field, numpy.ndarray):
                    ret.update(narray_summary_info(attr_field, ar_name=aname))
                elif isinstance(attr_field, HasTraits):
                    ret[aname] = attr_field.title
                else:
                    ret[aname] = repr(attr_field)
            except TraitError:
                ret[aname] = 'unavailable'
        return ret
