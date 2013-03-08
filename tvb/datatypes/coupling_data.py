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

The Data component of the Coupling datatypes.

.. moduleauthor:: Paula Sanz Leon <paula@tvb.invalid>

"""

import tvb.basic.traits.types_basic as basic
import tvb.datatypes.equations as equations

#TODO: This needs refactoring so that all specific types of Coupling are 
#      instances of a base Coupling class... 
class CouplingData(equations.Equation):
    """
    A base class for the Coupling datatypes
    """
    _ui_name = "Coupling"
    __generate_table__ = True


class LinearCouplingData(equations.Linear):
    """
    The equation for representing a Linear Coupling
    """
    _ui_name = "Linear Coupling"
    
    parameters = basic.Dict( 
        label = "Linear Coupling Parameters a and b",
        doc = """a: rescales connection strengths and maintains ratio and
                 b: shifts the base strength (maintain absolute difference)""",
        default = {"a": 0.00390625, "b": 0.0})
    
    __generate_table__ = True
        
        
class SigmoidalCouplingData(equations.GeneralizedSigmoid):
    """
    The equation for representing a Sigmoidal Coupling.
    """
    _ui_name = "Sigmoidal Coupling"
    __generate_table__ = True
    
    