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

Scientific methods for the Spectral datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy
import tvb.basic.traits.util as util
import tvb.datatypes.spectral_data as spectral_data
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class FourierSpectrumScientific(spectral_data.FourierSpectrumData):
    """ This class exists to add scientific methods to FourierSpectrumData. """
    __tablename__ = None
    
    _frequency = None
    _freq_step = None
    _max_freq = None
    
    
    def configure(self):
        """
        Invoke the compute methods for computable attributes that haven't been
        set during initialisation.
        """
        super(FourierSpectrumScientific, self).configure()
        
        if self.trait.use_storage is False and sum(self.get_data_shape('array_data')) != 0:
            if self.amplitude.size == 0:
                self.compute_amplitude()
            
            if self.phase.size == 0:
                self.compute_phase()
            
            if self.power.size == 0:
                self.compute_power()
            
            if self.average_power.size == 0:
                self.compute_average_power()
            
            if self.normalised_average_power.size == 0:
                self.compute_normalised_average_power()
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Spectral type": self.__class__.__name__}
        summary["Source"] = self.source.title
        summary["Segment length"] = self.segment_length
        summary["Windowing function"] = self.windowing_function
        summary["Frequency step"] = self.freq_step
        summary["Maximum frequency"] = self.max_freq
        return summary
    
    
    @property
    def freq_step(self):
        """ Frequency step size of the complex Fourier spectrum."""
        if self._freq_step is None:
            self._freq_step = 1.0 / self.segment_length
            msg = "%s: Frequency step size is %s"
            LOG.debug(msg % (str(self), str(self._freq_step)))
        return self._freq_step
    
    
    @property
    def max_freq(self):
        """ Amplitude of the complex Fourier spectrum."""
        if self._max_freq is None:
            self._max_freq = 0.5 / self.source.sample_period
            msg = "%s: Max frequency is %s"
            LOG.debug(msg % (str(self), str(self._max_freq)))
        return self._max_freq
    
    
    @property
    def frequency(self):
        """ Frequencies represented the complex Fourier spectrum."""
        if self._frequency is None:
            self._frequency = numpy.arange(self.freq_step, 
                                           self.max_freq + self.freq_step,
                                           self.freq_step)
            util.log_debug_array(LOG, self._frequency, "frequency")
        return self._frequency
    
    
    def compute_amplitude(self):
        """ Amplitude of the complex Fourier spectrum."""
        self.amplitude = numpy.abs(self.array_data)
        self.trait["amplitude"].log_debug(owner=self.__class__.__name__)
    
    
    def compute_phase(self):
        """ Phase of the Fourier spectrum."""
        self.phase = numpy.angle(self.array_data)
        self.trait["phase"].log_debug(owner=self.__class__.__name__)
    
    
    def compute_power(self):
        """ Power of the complex Fourier spectrum."""
        self.power = numpy.abs(self.array_data)**2
        self.trait["power"].log_debug(owner=self.__class__.__name__)
    
    
    def compute_average_power(self):
        """ Average-power of the complex Fourier spectrum."""
        self.average_power = numpy.mean(numpy.abs(self.array_data)**2, axis=-1)
        self.trait["average_power"].log_debug(owner=self.__class__.__name__)
    
    
    def compute_normalised_average_power(self):
        """ Normalised-average-power of the complex Fourier spectrum."""
        self.normalised_average_power = (self.average_power / 
                                         numpy.sum(self.average_power, axis=0))
        self.trait["normalised_average_power"].log_debug(owner=self.__class__.__name__)



class WaveletCoefficientsScientific(spectral_data.WaveletCoefficientsData):
    """
    This class exists to add scientific methods to WaveletCoefficientsData.
    """
    __tablename__ = None
    _frequency = None
    _time = None
    
    
    def configure(self):
        """
        Invoke the compute methods for computable attributes that haven't been
        set during initialisation.
        """
        super(WaveletCoefficientsScientific, self).configure()
        
        if self.trait.use_storage is False and sum(self.get_data_shape('array_data')) != 0:
            if self.amplitude.size == 0:
                self.compute_amplitude()
            
            if self.phase.size == 0:
                self.compute_phase()
            
            if self.power.size == 0:
                self.compute_power()
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Spectral type": self.__class__.__name__}
        summary["Source"] = self.source.title
        summary["Wavelet type"] = self.mother
        summary["Normalisation"] = self.normalisation
        summary["Q-ratio"] = self.q_ratio
        summary["Sample period"] = self.sample_period
        summary["Number of scales"] = self.frequencies.shape[0]
        summary["Minimum frequency"] = self.frequencies[0]
        summary["Maximum frequency"] = self.frequencies[-1]
        return summary
    
    
    @property
    def frequency(self):
        """ Frequencies represented by the wavelet spectrogram."""
        if self._frequency is None:
            self._frequency = numpy.arange(self.frequencies.lo, 
                                           self.frequencies.hi, 
                                           self.frequencies.step)
            util.log_debug_array(LOG, self._frequency, "frequency")
        return self._frequency
    
    
    def compute_amplitude(self):
        """ Amplitude of the complex Wavelet coefficients."""
        self.amplitude = numpy.abs(self.array_data)
        self.trait["amplitude"].log_debug(owner=self.__class__.__name__)
    
    
    def compute_phase(self):
        """ Phase of the Wavelet coefficients."""
        self.phase = numpy.angle(self.array_data)
        self.trait["phase"].log_debug(owner=self.__class__.__name__)
    
    
    def compute_power(self):
        """ Power of the complex Wavelet coefficients."""
        self.power = numpy.abs(self.array_data)**2
        self.trait["power"].log_debug(owner=self.__class__.__name__)



class CoherenceSpectrumScientific(spectral_data.CoherenceSpectrumData):
    """ This class exists to add scientific methods to CoherenceSpectrumData. """
    __tablename__ = None
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Spectral type": self.__class__.__name__}
        summary["Source"] = self.source.title
        summary["Number of frequencies"] = self.frequency.shape[0]
        summary["Minimum frequency"] = self.frequency[0]
        summary["Maximum frequency"] = self.frequency[-1]
        summary["FFT length (time-points)"] = self.nfft
        return summary
        
        
class ComplexCoherenceSpectrumScientific(spectral_data.ComplexCoherenceSpectrumData):
    """ This class exists to add scientific methods to ComplexCoherenceSpectrumData. """
    __tablename__ = None
    
    _frequency = None
    _freq_step = None
    _max_freq = None
            
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Spectral type": self.__class__.__name__}
        summary["Source"] = self.source.title
        summary["Frequency step"] = self.freq_step
        summary["Maximum frequency"] = self.max_freq
        #summary["FFT length (time-points)"] = self.fft_points
        #summary["Number of epochs"] = self.number_of_epochs
        return summary
        
    @property
    def freq_step(self):
        """ Frequency step size of the Complex Coherence Spectrum."""
        if self._freq_step is None:
            self._freq_step = 1.0 / self.segment_length
            msg = "%s: Frequency step size is %s"
            LOG.debug(msg % (str(self), str(self._freq_step)))
        return self._freq_step
    
    
    @property
    def max_freq(self):
        """ Maximum frequency represented in the Complex Coherence Spectrum."""
        if self._max_freq is None:
            self._max_freq = 0.5 / self.source.sample_period
            msg = "%s: Max frequency is %s"
            LOG.debug(msg % (str(self), str(self._max_freq)))
        return self._max_freq
    
    
    @property
    def frequency(self):
        """ Frequencies represented in the Complex Coherence Spectrum."""
        if self._frequency is None:
            self._frequency = numpy.arange(self.freq_step, 
                                           self.max_freq + self.freq_step,
                                           self.freq_step)
        util.log_debug_array(LOG, self._frequency, "frequency")
        return self._frequency
            




