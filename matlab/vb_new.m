function [id, data] = vb_new(sv, sim)
%
% id = vb_new(sv, sim)
% 
% Create new simulation with options specified in struct sim, and return
% the id of the new simulation, on TVB @ sv
%
% Special fields of sim:
%
% sim.wd    working directory, where data files temporarily stored
% sim.tf    simulation length, in milliseconds
% sim.wait  wait for simulation to finish 
%
% [id, data] = vb_new(sv, sim)
%
% As above, but wait for finish, load & return data immediately.
%

% convert ..models.JansenRit style to 'JansenRit'

parts = {'model' 'connectivity' 'coupling' 'integrator'};
for i=1:length(parts)
    part = parts{i};
    lines = strsplit(sim.(part).class);
    if length(lines)>1
        sim.(part).class = lines{1};
    end
end

for i=1:length(sim.monitors)
    lines = strsplit(sim.monitors{i}.class);
    if length(lines)>1
        sim.monitors{i}.class = lines{1};
    end
end

% make sure we've got working directory
if ~isfield(sim, 'wd')
    sim.wd = pwd;
    warning('vb_new: no working directory was specified,\n\tdefaulting to %s', sim.wd);
end

% convert parameters to JSON 
js = savejson('opt', sim);

% submit
url = [sv 'api/simulator/create'];
id = urlread(url, 'GET', {'js' js});
id = str2num(id);

% get & return data if requested
if nargout > 1
    % wait for Python to catch up
    pause(1.0);
    data = vb_load(sv, id, 0);
end
    