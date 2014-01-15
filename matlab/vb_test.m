%% determine url
% We communicate with TVB as a server, so need to know where it is
% and use that address for all calls
sv = vb_url('localhost', 8080)

%% set the number of CPUs used for simulations
vb_reset(sv, 2)

%% get info on classes in TVB
vb = vb_dir(sv);

%% try a simulation

sim = [];

% where to put data files
sim.wd = pwd; 

% how long to simulate (ms)
sim.tf = 5e1;

sim.model.class = vb.models.Generic2dOscillator;
%opt.model.a = -2.1;

sim.connectivity.class = 'Connectivity';
sim.connectivity.speed = 4.0;

sim.coupling.class = 'Linear';
sim.coupling.a = 0.002;

sim.integrator.class = 'HeunDeterministic';
sim.integrator.dt = 1e-2;

sim.monitors{1}.class = 'TemporalAverage';

%sim.monitors{2}.class = 'Raw';
%sim.monitors{2}.period = 1.0; % ms

[id, data] = vb_new(sv, sim);

plot(data.mon_0_TemporalAverage.ts, squeeze(data.mon_0_TemporalAverage.ys)')



