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
All problems in computer science can be solved by another layer of
indirection, except for the problem of too many layers of indirection.


Traits overview
---------------

Traits classes are separated into two modules:

core.

    TraitsInfo          metadata container for traits system
    MetaType            base class for traited class creation
    Type                base traited class 

basic.

    MappedType          basic class for traited class mapped to db
    *(Type)             traits mapped to columns
    *(MappedType)       traits mapped to column(foreignkey) -> table 


Traits metadata
---------------

While the traits of a class can be declared nearly arbitrarily, there are
intrinsic pieces of information in the metadata required to make the traits
system work:


Need to implement better info container for this:

    More information based on trait instantiation kwds

        doc         string      long description, possibly multi string
        label       string      short name appearing in UI
        default     object      default value of attribute
        required    bool        determines whether must be set to initialize
        range       Range       helps validate or specify parameter variation
        compute     fn/ref      function computing value
        db          *           False, Col inst; specifies sqlalchemy column
        locked      bool        defaults False, if True, __set__ raise AttrError

    Class attribute that needs to picked up during class creation, and
    inherited via .trait

        uitype      string      specifies what kindof ui selector is used

    trait 'state' information

        state       one of 'nodb', 'dbloaded', 'populated', 'cached'

    .initialize() gets us to the populated state, and then we might use a
    provided compute function to become cached.



TODOs
-----

O   implement behavior for new keywords
O   move _init_* to TraitInfo
O   move Type.update to Type.__call__
O   warn/raise Exc/protect if __type__ or __call__ overridden
O   consider a with-style context manager for manipulating traits info:

        with Sim.trait.unbound as sim:
            sim.x.range *= 2

    or

        with unbound(Sim.model.dt) as dt:
            dt.range = Range(lo=1e-9, hi=0.3)

    which makes sure that it's rebound after the changes. Would want unbound to
    check that we're within a with statement.

O   while traits' values may need to live at first in the trait attr attr
    value, after the trait has an owner, it should always __get__ on the owner
    value. But this will also depend on the db/compute state.


.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: marmaduke <duke@eml.cc>

"""

import re
import abc 
import sqlalchemy
from copy import deepcopy, copy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from tvb.config import TVBSettings as config
from tvb.basic.traits.util import get, Args, TypeRegister, ispublic
import tvb.basic.logger.logger as logger
from tvb.core.traits.sql_mapping import MAPPINGS, get_sql_mapping

LOG = logger.getLogger(__name__)
TRAITS_CONFIGURATION  = config.TRAITS_CONFIGURATION

KWARG_CONSOLE_DEFAULT = 'console_default'
KWARG_SELECT_MULTIPLE = 'select_multiple'
KWARG_ORDER = 'order'                   ## -1 value means hidden from UI
KWARG_AVOID_SUBCLASSES = 'fixed_type'   ## When set on a traited attr, no subclasses will be returned
KWARG_FILE_STORAGE = 'file_storage'
KWARG_REQUIRED = 'required'
KWARG_FILTERS_UI = 'filters_ui'
KWARG_OPTIONS = 'options'
FILE_STORAGE_DEFAULT = 'HDF5'
FILE_STORAGE_EXPAND = 'expandable_HDF5'
FILE_STORAGE_NONE = 'None'


SPECIAL_KWDS = ['bind', 'doc', 'label', 'db', 'default', 'required', KWARG_AVOID_SUBCLASSES,
                'range', 'locked', KWARG_FILTERS_UI, KWARG_CONSOLE_DEFAULT,
                KWARG_SELECT_MULTIPLE, KWARG_FILE_STORAGE, KWARG_ORDER, KWARG_OPTIONS]


# module global used by MetaType
TYPE_REGISTER = TypeRegister()

def compute_table_name(class_name):
    """
    Given a class name compute the name of the corresponding SQL table.
    """
    tablename = 'MAPPED' + re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', '_', class_name).upper()
    if tablename.count('MAPPED_') > 1:
        tablename = tablename.replace('MAPPED_', '', 1)
    return tablename

class TraitsInfo(dict):
    """
    TraitsInfo is a container for information related to the owner
    class and its traited attributes that is used by the traits
    classes. It is needed because many of the attribute names used
    by traits, e.g. data & bound, may mean other things to other
    classes and we can't step on their toes.

    TraitsInfo is a dict of the owner's traited attributes, and its
    other attributes are:

    - name - name of attribute on owner class
    - bound - whether the trait is bound as data descriptor
    - wraps - class this trait wraps
    - inits - a namedtuple of positional and keyword arguments
        given to intialize the trait instance
    - value - instance value of trait, equal to trait if wraps==None
    - defaults - default args to wraps' constructor

    """

    def __init__(self, trait, name='<no name!>', bound=False, wraps=None,
                 inits=Args((), {}), value=None, wraps_defaults=()):
        self.name = name
        self.bound = bound
        self.wraps = wraps
        self.wraps_defaults = wraps_defaults
        self.inits = inits
        self.value = value

    @property
    def file_storage(self):
        if KWARG_FILE_STORAGE not in self.inits.kwd:
            return FILE_STORAGE_DEFAULT
        return self.inits.kwd[KWARG_FILE_STORAGE] 

    @property
    def order_number(self):
        if KWARG_ORDER not in self.inits.kwd:
            return 0
        return self.inits.kwd[KWARG_ORDER]


    @property
    def required(self):
        if KWARG_REQUIRED not in self.inits.kwd:
            return True
        return self.inits.kwd[KWARG_REQUIRED]

    @property
    def use_storage(self):
        if 'use_storage' not in self.inits.kwd:
            return True
        return self.inits.kwd['use_storage']

    @property
    def range_interval(self):
        if 'range' not in self.inits.kwd:
            return None
        return self.inits.kwd['range']

    @property
    def select_multiple(self):
        if KWARG_SELECT_MULTIPLE in self.inits.kwd:
            return self.inits.kwd[KWARG_SELECT_MULTIPLE]
        return False

    def __repr__(self):
        return 'TraitsInfo(%r)' % (super(TraitsInfo, self).__repr__(), )

    def copy(self):
        """
        Create a copy for current Traits.
        """
        new_value = deepcopy(self.value)
        copyed = TraitsInfo(new_value, self.name, self.bound,
                self.wraps, self.inits, wraps_defaults=self.wraps_defaults)
        for key, value in self.iteritems():
            copyed[key] = copy(value)
        return copyed



class Type(object):
    """ Type is redefined below. This is here so MetaType can refer to Type """



class MetaType(abc.ABCMeta):
    """

    The MetaType class augments the class creation and instantiation of all the
    types in the Traits system. See the docstrings of the methods for more
    details:

        __new__  - creates a class 
        __call__ - create a class instance

    While the basic Traits mechanisms are described and implemented in this
    class, see DeclarativeMetaType for implementation and description of 
    database mapping of Traits classes.

    """

    def __new__(mcs, name, bases, dikt):
        """

        MetaType.__new__ creates a new class, but is typically involved
        *implicitly* either by declaring the __metaclass__ attribute

            class Type(object):
                __metaclass__ = MetaType

        or by subclassing Type:

            class Foo(Type):
                pass

        but in both cases, this method is called to produce the new class
        object.

        Rough list of what's done:

            - catch wrapping class and defaults for that class 
            - catch a uitype specification
            - create class via super's __new__ 
            - add new class to list of classes
            - augment docstring of class 
            - catch and setup all trait attributes on class
            - add required information to class 

        To setup a trait attribute, we 

            - check if it's a type, if so, instantiate
            - tell the attr it's name on owner class 
            - setup privatized attr with attr value 
            - augment owner class docstring with trait description 
            - add trait to information on class 

        """

        # if we're wrapping a class, pop that out
        wraps = dikt.pop('wraps', set([]))
        wraps_defaults = dikt.pop('defaults', ())
        uitype = dikt.pop('uitype', '')

        # make new class
        newcls = super(MetaType, mcs).__new__(mcs, name, bases, dikt)

        # add new class to type register
        TYPE_REGISTER.append(newcls)

        # prep class doc string
        doc = get(dikt, '__doc__', 'traited class ' + name)
        doc += "\n    **traits on this class:**\n"

        # build traits info on newcls' attrs
        if hasattr(newcls, 'trait'):
            trait = newcls.trait.copy()
        else:
            trait = TraitsInfo(newcls)

        for key in filter(ispublic, dir(newcls)):
            attr = getattr(newcls, key)
            if isinstance(attr, MetaType) or isinstance(attr, Type):
                if isinstance(attr, MetaType):
                    attr = attr()
                attr.trait.name = key
                setattr(newcls, key, attr)
                #rpr = attr.__repr__()
                #doc += "\n\t``%s``:\n\t\t%s\n" % (key, rpr if rpr else '<bad repr>')
                doc += "\n\t``%s`` (%s)\n" % (key, str(attr.trait.inits.kwd.get('label', "")))
                doc += "\t\t| %s\n" % str(attr.trait.inits.kwd.get('doc', "")).replace("\n", " ")
                doc += "\t\t| ``default``:  %s \n" % str(attr.trait.inits.kwd.get('default', None)).replace("\n", " ")
                specified_range = attr.trait.inits.kwd.get('range', None)
                if specified_range:
                    doc += "\t\t| ``range``: low = %s ; high = %s \n\t\t\n" % (str(specified_range.lo), str(specified_range.hi))
                #TODO: Need a better parsing of range 
                trait[key] = attr

        # add info to new class
        if wraps:
            trait.wraps = wraps
        if wraps_defaults:
            trait.wraps_defaults = wraps_defaults
        newcls.trait = trait

        # bind traits unless told otherwise
        for attr in newcls.trait.itervalues():
            attr.trait.bound = attr.trait.inits.kwd.get('bind', True)

        newcls.__doc__ = doc

        return newcls

    def __call__(ncs, *args, **kwds):
        """

        MetaType.__call__ method wraps ncs.__init__(ncs.__new__(*, **), *, **),
        and is implicitly called when the class __init__()s.

        b.Range(*args, **kwds) -> b.Range.__init__(b.Range.__new__(MetaType.__call__(b.Range, *args, **kwds), *, **), *, **)

        When creating instances of Traits classes, we

            - if wrapping, try to instantiation wrapped class 
            - check keyword arguments, use to initialize trait attributes
            - record all other keyword args for later use 
            - create class instance 
            - return instance updated with information

        """

        inits = Args(args, kwds.copy())

        # build value if we're wrapping
        # TODO: big clean up, use wraps_defaults always
        if 'default' in kwds:
            # TODO: type check
            value = kwds.pop('default')
            if isinstance(value, MetaType):
                value= value()

        elif KWARG_CONSOLE_DEFAULT in kwds and not TRAITS_CONFIGURATION.use_storage:
            value = kwds.pop(KWARG_CONSOLE_DEFAULT)
        elif ncs.trait.wraps:
            wrapped_callable = ncs.trait.wraps[0] if isinstance(ncs.trait.wraps, tuple) else ncs.trait.wraps
            # no args, and we have defaults
            if ncs.trait.wraps_defaults:
                _args, _kwds = ncs.trait.wraps_defaults
                value = wrapped_callable(*_args, **_kwds)
            # else default constructor, no args
            else:
                value = wrapped_callable()
        else:
            value = None

        kwdtraits = {}
        for key in set(kwds.keys()) & set(ncs.trait.keys()):
            kwdtraits[key] = kwds[key]
            del kwds[key]
            
        options = kwds.get(KWARG_OPTIONS, None)

        # discard kwds to be passed for instantiation
        [kwds.pop(key, None) for key in SPECIAL_KWDS]

        # instantiate trait, but catch bad args
        try:
            inst = super(MetaType, ncs).__call__(*args, **kwds)
        except TypeError as exc:
            if not args and not kwds:
                # then it's not because we haven't handled all args & kwds
                raise exc
            else:
                # TODO: we decided against extensible keywords, so this
                # message should be removed.
                msg = "couldn't create instance of %s with unhandled " % (ncs.__module__ + '.' + ncs.__name__, )
                msg += "args, %s, " % (args,) if args else ""
                kwd_advice = " to ignore this kwd, append %s.pop_kwds."
                kwd_advice %= (MetaType.__module__ + '.' +  MetaType.__name__, )
                msg += ("kwds, %s." % (kwds,) + kwd_advice) if kwds else ""
                raise TypeError(msg)

        # make copy of traits info before customizing
        inst.trait = ncs.trait.copy()
        # set all possible options if they were passed in trait instantiation
        inst.trait.options = options
        # set instance's value, inits dict and kwd passed trait values
        inst.trait.value = deepcopy(value) #if (value is not None) else inst
        inst.trait.inits = inits
        # Set Default attributes from traited class definition
        for name, attr in inst.trait.iteritems():
            try:
                setattr(inst, name, deepcopy(attr.trait.value))
            except Exception, exc:
                LOG.exception(exc)
                LOG.error("Could not set attribute '" + name +"' on " + str(inst.__class__.__name__))
                raise exc
        # Overwrite with attributes passed in the constructor
        for name, attr in kwdtraits.iteritems():
            try:
                setattr(inst, name, attr)
            except Exception, exc:
                LOG.exception(exc)
                LOG.error("Could not set kw-given attribute '" + name +"' on " + str(inst.__class__.__name__))
                raise exc

        # the owner class, if any, will set this to true, see metatype.__new__
        inst.trait.bound = False
        return inst



class Type(object):
    """
    Type class provides a base class for datatypes and the attributes on
    datatypes.

    When a Type instance is an attribute of a class and self.bound is True, the
    instance will act as a data descriptor, setting/getting its corresponding
    value on the owner class.

    In the case of sql'ed values, names are coordinated such that the private
    value (```obj._name```) of the public attr (```obj.name```) on the owner
    class used by the Type instance is actually the corresponding sqlalchemy
    data descriptor as generated by the value of 'sql' keyword to the Type
    instance __init__.

    """

    __metaclass__ = MetaType
    _summary_info = None

    def __get__(self, inst, cls):
        """When an attribut of Type is retrieved on another class"""
        if inst is None:
            return self
        if self.trait.bound:
            if hasattr(inst, '_' + self.trait.name):
                # Return simple DB field or cached value
                return getattr(inst, '_' + self.trait.name)
            else:
                return None
        else:
            return self

    def __set__(self, inst, value):
        """
        When an attribute of Type is set on another class
        """
        if self.trait.bound:
            # First validate that the given vaue is compatible with the
            # current attribute definition
            accepted_types = [type(self), type(None)]
            if isinstance(self.trait.wraps, tuple):
                accepted_types.extend(self.trait.wraps)
            else:
                accepted_types.append(self.trait.wraps)

            if (type(value) in accepted_types or isinstance(value, type(self)) 
                or (isinstance(value, (list, tuple)) and self.trait.select_multiple)):
                self._put_value_on_instance(inst, value)
            else:
                msg = 'expected type %s, received type %s' % (type(self), type(value))
                LOG.error(msg)
                raise AttributeError(msg)


    def _put_value_on_instance(self, inst, value):
        """
        Is the ultimate method called by __set__ implementations.
        We write it separately here, because subclasses might need to call this separately, 
        without the __set__ default value validation.
        """
        setattr(inst, '_' + self.trait.name, value)
        inst.trait[self.trait.name].value = value


    def __repr__(self):
        """
        Type.repr builds a useful representation of itself, which can be 
        configured with values in config:

        """
        trait = self.trait
        rep  = self.__class__.__name__ + "("
        objstr = object.__repr__(self)
        value = objstr if self is trait.value else trait.value

        reprinfo = {}
        reprinfo['value'] = repr(value)
        reprinfo['bound'] = repr(trait.bound)
        if trait.wraps:
            reprinfo['wraps'] = repr(trait.wraps)
        if trait.bound:
            reprinfo['name'] = repr(trait.name)

        reprstr = ['%s=%s' % (k, v) for k, v in reprinfo.items()]
        return rep + ', '.join(reprstr) + ')'


    def configure(self):
        """
        Call this method to process linked attributes on datatype.
        it will be called before storing in DB.
        """
        pass


    @property
    def summary_info(self):
        """
        For a particular DataType, return a dictionary of label: value, 
        to describe the entity from scientific point of view.
        """
        if self._summary_info is None and hasattr(self, "_find_summary_info"):
            self._summary_info = self._find_summary_info()
        return self._summary_info


    def _find_summary_info(self):
        """
        To be implemented in every subclass.
        """
        return None


class DeclarativeMetaType(DeclarativeMeta, MetaType):
    """
    The DeclarativeMetaType class helps with class creation by automating
    some of the sqlalchemy code generation. We code for three possibilities:

    - the sql or db keywords are False, no sqlalch used
    - sql or db keywords are True or unset, default sqlalche used
    - sql or db keywords are set with sqlalchemy.Column instances, and
        that is used

    If it is desired that no sql/db is used, import traits.core and set
    traits.core.TRAITS_CONFIGURATION.use_storage = False. This will have the (hopefully
    desired) effect that all sql and db keyword args are ignored.

    """

    def __new__(*args):
        mcs, name, bases, dikt = args
        if dikt.get('__generate_table__', False):
            tablename = compute_table_name(name)
            if '__tablename__' not in dikt:
                dikt['__tablename__'] = tablename
        newcls = super(DeclarativeMetaType, mcs).__new__(*args)

        if newcls.__name__ in ('DataType', 'MappedType'):
            return newcls

        mro_names = map(lambda cls: cls.__name__, newcls.mro())
        if Type in newcls.mro() and 'DataType' in mro_names:
            LOG.debug('new mapped, typed class %r', newcls)
        else:
            LOG.debug('new mapped, non-typed class %r', newcls)
            return newcls

        # Compute id foreignkey to parent
        all_parents = []
        for b in bases:
            all_parents.extend(b.mro())
        mapped_parent = filter(lambda cls: issubclass(cls, Type) and hasattr(cls, '__tablename__') 
                                            and getattr(cls, '__tablename__') is not None, all_parents)
        # Identify DATA_TYPE class, to be used for specific references
        datatype_class = filter(lambda cls: hasattr(cls, '__tablename__') and cls.__tablename__ == 'DATA_TYPES', 
                                all_parents)[0]

        ###### Map Trait attributes to SQL Columns as necessary
        all_class_traits = getattr(newcls, 'trait', {})
        super_traits = dict()
        for parent_class in filter(lambda cls: issubclass(cls, Type), all_parents):
            super_traits.update(getattr(parent_class, 'trait', {}))
        newclass_only_traits = dict([(key, all_class_traits[key]) for key in all_class_traits if key not in super_traits])

        LOG.debug('mapped, typed class has traits %r', newclass_only_traits)
        for key, attr in newclass_only_traits.iteritems():
            kwd = attr.trait.inits.kwd
            ##### Either True or a Column instance
            sql = kwd.get('db', True)

            if isinstance(sql, sqlalchemy.Column):
                setattr(newcls, '_' + key, sql)

            elif get_sql_mapping(attr.__class__):
                defsql = get_sql_mapping(attr.__class__)
                sqltype, args, kwds = defsql[0], (), {}
                for arg in defsql[1:]:
                    if type(arg) is tuple:
                        args = arg
                    elif type(arg) is dict:
                        kwds = arg
                setattr(newcls, '_' + key, sqlalchemy.Column('_'+key, sqltype, *args, **kwds))

            elif Type in attr.__class__.mro() and hasattr(attr.__class__, 'gid'):
                #### Is MappedType
                fk = sqlalchemy.ForeignKey('DATA_TYPES.gid', ondelete="SET NULL")
                setattr(newcls, '_' + key, sqlalchemy.Column('_' + key, sqlalchemy.String, fk))
                if newcls.__tablename__:
                    #### Add relationship for specific class, to have the original entity loaded
                    rel = relationship(attr.__class__, lazy='joined', cascade="none",
                    ####In case of 'save-update' we would need to SET the exact instance type as defined in atrr description
                                       primaryjoin=(eval('newcls._'+key)==attr.__class__.gid),
                                       enable_typechecks = False)
                    setattr(newcls, '__' + key, rel)

            else: #### no default, nothing given
                LOG.warning('no sql column generated for attr %s, %r', key, attr)
        DeclarativeMetaType.__add_class_mapping_attributes(newcls, mapped_parent)
        return newcls


    @staticmethod
    def __add_class_mapping_attributes(newcls, mapped_parent):
        """
        Add Column ID and update __mapper_args__
        """
        #### Determine best FOREIGN KEY  
        if mapped_parent is None or len(mapped_parent) < 1:
            mapped_parent = datatype_class
            fkparentid = 'DATA_TYPES.id'
        else:
            mapped_parent = mapped_parent[0]
            fkparentid = mapped_parent.__tablename__ + '.id' 
        ### Update __mapper_args__ SQL_ALCHEMY attribute.    
        if newcls.__tablename__:
            LOG.debug('cls %r has dtparent %r', newcls, mapped_parent)
            LOG.debug('%r using %r as id foreignkey', newcls, fkparentid)
            column_id = sqlalchemy.Column('id', sqlalchemy.Integer,
                                          sqlalchemy.ForeignKey(fkparentid, ondelete="CASCADE"), primary_key=True)
            setattr(newcls, 'id', column_id)
            ### We can not use such a backref for cascading deletes, as we will have a cyclic dependency (DataType > Mapped DT > Operation).
#            rel = relationship(mapped_parent, primaryjoin=(eval('newcls.id')==mapped_parent.id),
#                               backref = backref('__' +newcls.__name__, cascade="delete"))
#            setattr(newcls, '__id_' + mapped_parent.__name__, rel)
            mapper_arg = {}
            kwd = newcls.trait.inits.kwd
            if hasattr(newcls, '__mapper_args__'):
                mapper_arg = getattr(newcls, '__mapper_args__')

            if 'polymorphic_on' in mapper_arg and isinstance(mapper_arg['polymorphic_on'], (str, unicode)):
                discriminator_name = mapper_arg['polymorphic_on']
                LOG.debug("Polymorphic_on %s - %s "% (newcls.__name__, discriminator_name))
                mapper_arg['polymorphic_on'] = getattr(newcls, '_' + discriminator_name)
            mapper_arg['inherit_condition'] = (newcls.id == mapped_parent.id)
            if 'exclude_properties' in mapper_arg:
                del mapper_arg['exclude_properties']
                del mapper_arg['inherits']
            setattr(newcls, '__mapper_args__', mapper_arg)


if TRAITS_CONFIGURATION.use_storage:
    TypeBase = declarative_base(cls=Type, name='TypeBase', metaclass=DeclarativeMetaType)
else:
    TypeBase = Type


