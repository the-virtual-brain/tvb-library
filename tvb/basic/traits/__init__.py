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
Traits metadata module
======================

introduction
------------

The problem is that various classes have members whose properties we want to
annotate in a way that does not affect the execution of the class algorithms
but that exposes an API to pull out this info for a user interface and
documentation. It should be readable for the programmers as well. We refer to
an annotated/propertied member as a trait.

Consider the following class:

    >>> class Point(object):
    ...     x = 0.0
    ...     y = 0.0

If you want to present this data to the user, you may want to label each
attribute of the Point with more than just 'x' or 'y', or you want to check
that if the user creates a Point, the values have the right type (here, we
assume the type of 0.0 means floating point), and if you want to store the
instances of Point in a data base, each one needs a unique id. These pieces of
information need to be put somewhere, and the best place to put it is in the
attribute declaration, for example,

    >>> class Point(Type):
    ...     x = Float(0.0, doc='horizontal position')
    ...     y = Float(0.0, doc='vertical position')

Here, the type of each attribute is explicit, and a documentation string
is provided, *all in the same attribute declaration*, and this co-location
of information makes it easier to maintain, and elsewhere in the program,
this information can be accessed programmatically to generate user interfaces,
serialize data, validate data, etc. Additionally, all classes' docstrings
will have Traits information automatically added:

    >>> print Point.__doc__
    Traited class Point
        x: horizontal position, type float
        y: vertical position, type float

The Traits package allows us to write classes like the one above by using a
metaclass to customize the class creation. In brief, when Python reads a class
definition the Trait metaclass has access to all the attribute declarations,
and it will place a dictionary of all the data provided in the declarations on
the class.  When the classes are instantiated and used, the Trait attributes
behave exactly like their values, such that class methods do not need to know
they are accessing Trait attributes. For more details, see `traits.core`.


package modules
---------------

    core            Provides the core of Traits, a metaclass and class that
                    implement the reflection/annotation that Traits allows.

    basic           Provides basic predefined types as well as the Type that
                    should be inherited from when making new Types

    array           Provides a class wrapping the NumPy ndarray

    interface       Provides recursive interfaces classes that are data
                    descriptors, i.e. when placed on classes, they compute
                    the full description of the class and it's Traited
                    attributes.

    util            Utility functions and classes.


refactor notes
--------------

use of keywords
```````````````

TODO changed this, needs updates to describe use of opt_kwds and req_kwds.

Intializing traits with any keywords you like usually involves appending
the keyword name to MetaType.pop_kwds. If you forget, you'll get a nice
message telling you what to do:

    >>> import core
    >>> class Foo(core.Type):
    ...     pass

    >>> Foo(wahwah='hendrix')

    TypeError: couldn't create instance of __main__.Foo with unhandled kwds,
        {'wahwah': 'hendrix'}. To ignore this kwd, append core.MetaType.pop_kwds

    >>> core.MetaType.pop_kwds.append('wahwah')
    >>> f = Foo(wahwah='hendrix')
    >>> f.inits.kwd['wahwah']
    'hendrix'

If you want to do something algorithmic with a keyword value during class
or instance creation, it requires subclassing MetaType or Type,
respectively.

See `traits.sql` for an example.

automatic class documentation
`````````````````````````````

Classes that subclass Type (or subclasses of MetaType) have their docstrings
automatically augmented by the repr() of each attribute which is a Type. This
allows one to find the trait documentation both in Sphinx and at the console.

work list
`````````

X  extend keyword handling
X  better documentation traits itself
O  config reads TVB config / integrated
O  log a count of how many non default values used
O  extensive logging
X  traits auto-added to class doc
/  pylint score 7.37/10 (on core.py)
/  merge into TVB via datatypes, then interfaces, simulator, analyzers
X  merge with minitraits
/  test suite
O  get tests into tvb_test
/  figure out datatypes sql patterns, embed in Trait classes
/  figure out attr acces patterns, embed in Trait data descrip methods
O  protecting keywords and attributes from setting stuff

/  integrate w/ model.DataType: fix entities.mode.DataType.__init__
O  warn/raise bloody hell if trait name conflicts w/ DB attribute
    or just make DB attributes private

It is typically possible for a user to screw up the system in a number of
ways. In other languages, we'd go to great lengths to keep that from happening,
but here, I'd prefer using a combination of logging and sanity flags. The user
can go crazy, but if one or more of the sanity flags are False, the user
should know he/she has done something incorrect and some things may not work.

In particular at class creation, we should make extensive logging notes of
the base(s) attributes and the incoming attributes, and warn about conflicts
if we don't know why.


References
----------

Suggested reading is `Unifying Types and Classes`_ and the
`Python data model`_.

.. _Unifying Types and Classes:
    http://www.python.org/download/releases/2.2.3/descrintro/
.. _Python data model: http://docs.python.org/reference/datamodel.html

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# add interfaces based on config
import core, traited_interface
from tvb.config import TVBSettings as config

setattr(core.Type, core.TRAITS_CONFIGURATION.interface_method_name, 
        traited_interface.TraitedInterfaceGenerator())

def get_mapped_type():
    if config.TRAITS_CONFIGURATION.use_storage:
        import tvb.core.traits.types_mapped as mapped
        return mapped.MappedType
    else:
        from tvb.basic.traits.types_mapped import MappedTypeLight
        return MappedTypeLight

