function vb_wait(sv, id)
%
% Wait for one or more simulations, specified by id,
% to finish running. If no id given, wait for all jobs.
%
% This blocks MATLAB, but is the only way to know as
% soon as a simulation is done.
%
% The time between polling for information, polltime, 
% defaults to 2.0 (s).
%

while 1
    info = vb_stat(sv);
    
    if id > length(info)
        warning('vb_wait() ignoring out of bounds id=%d > length(info)=%d', id, length(info))
        break
    end
    
    if strcmp(info{id}.status, 'waiting')
        pause(1.0);
    else
        break
    end
end
