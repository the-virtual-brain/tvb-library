from tvb.basic.profile import TvbProfile
TvbProfile.set_profile(TvbProfile.LIBRARY_PROFILE)

import inspect
import numpy as np
from matplotlib import pyplot

from tvb.simulator.lab import *
from tvb.simulator.simulator_julie import Simulator
from tvb.simulator.models.wong_wang_exc_inh_julie import ReducedWongWangExcInh
import tvb_data


if __name__ == "__main__":

    TVB_DATA_PATH = os.path.dirname(inspect.getabsfile(tvb_data))
    DEFAULT_SUBJECT_PATH = os.path.join(TVB_DATA_PATH, "berlinSubjects", "QL_20120814")
    DEFAULT_CONNECTIVITY_ZIP = os.path.join(DEFAULT_SUBJECT_PATH, "QL_20120814_Connectivity.zip")
    connectivity = connectivity.Connectivity.from_file(DEFAULT_CONNECTIVITY_ZIP)
    connectivity.configure()

    # ----2. Define a TVB simulator (model, integrator, monitors...)--------------

    # Create a TVB simulator and set all desired inputs
    # (connectivity, model, surface, stimuli etc)
    # We choose all defaults in this example
    simulator = Simulator()
    simulator.model = ReducedWongWangExcInh()
    simulator.model.G = np.array(0.1)
    simulator.model.W_BG_e = np.array(0.01)
    simulator.model.W_BG_i = np.array(0.5)

    # Synaptic gating state variables S_e, S_i need to be in the interval [0, 1]
    simulator.connectivity = connectivity
    # TODO: Try to make this part of the __init__ of the Simulator!
    simulator.integrator = integrators.EulerDeterministic(dt=0.1)
    # Some extra monitors for neuroimaging measures:
    mon_raw = monitors.Raw(period=simulator.integrator.dt)
    # mon_bold = Bold(period=2000.)
    # mon_eeg = EEG(period=simulator.integrator.dt)
    simulator.monitors = (mon_raw,)  # mon_bold, mon_eeg

    Nt = 10000
    simulator.source_eeg = np.random.normal(size=(Nt, connectivity.number_of_regions))
    simulator.configure()

    output = simulator.run(simulation_length=Nt*simulator.integrator.dt)
    time = output[0][0]
    data = output[0][1]

    pyplot.plot(time, data[:, 0, :].squeeze())
    pyplot.show()

    print('Success!')
