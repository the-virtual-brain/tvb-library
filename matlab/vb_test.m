%% needed packages
addpath jsonlab

%% set the number of procs in the pool
vb_reset(2)

%% get info on classes in TVB
vb = vb_dir;

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

[id, data] = vb_new(sim);

plot(data.mon_0_TemporalAverage.ts, squeeze(data.mon_0_TemporalAverage.ys)')



