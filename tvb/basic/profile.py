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
ENUM used for choosing current TVB Profile.

Contains functionality which allows a user to set a certain profile for TVB.
"""

class TvbProfile():
    
    SUBPARAM_PROFILE = "-profile"
    
    # Existing profiles:
    LIBRARY_PROFILE = "LIBRARY_PROFILE"
    DEVELOPMENT_PROFILE = "DEVELOPMENT_PROFILE"
    TEST_POSTGRES_PROFILE = "TEST_POSTGRES_PROFILE"
    TEST_SQLITE_PROFILE = "TEST_SQLITE_PROFILE"
    DEPLOYMENT_PROFILE = "DEPLOYMENT_PROFILE"
    CONSOLE_PROFILE = "CONSOLE_PROFILE"

    # Used for setting the current TVB profile
    CURRENT_SELECTED_PROFILE = None


    @staticmethod
    def get_profile(script_argv):
        """
        Returns the user given profile or None if the user didn't specify a profile.

        script_argv - represents a list of string arguments. If the script_argv contains the element
        '-profile' than the tvb profile will be set to the next element.

        E.g.: if script_argv=['$param1', ..., '-profile', 'TEST_SQLITE_PROFILE', ...] than the tvb profile
        will be set to 'TEST_SQLITE_PROFILE'
        """
        if TvbProfile.SUBPARAM_PROFILE in script_argv:
            index = script_argv.index(TvbProfile.SUBPARAM_PROFILE)
            if len(script_argv) > index + 1:
                return script_argv[index + 1]
        return None


    @staticmethod
    def set_profile(script_argv):
        """
        Sets the specified profile.

        script_argv - represents a list of string arguments. If the script_argv contains the element
        '-profile' than the tvb profile will be set to the next element.
        E.g.: if script_argv=['$param1', ..., '-profile', 'TEST_SQLITE_PROFILE', ...] than the tvb profile
        will be set to 'TEST_SQLITE_PROFILE'
        """
        selected_profile = TvbProfile.get_profile(script_argv)
        if selected_profile is not None:
            TvbProfile.CURRENT_SELECTED_PROFILE = selected_profile
            
            