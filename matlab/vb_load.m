function data = vb_load(sv, id, keep, dsets)
%
% data = vb_load(id)
%
% Load data from simulation with index id
%
% Returns struct with one field per monitor, and two subfields for 
% time and monitor values, e.g. 
%
% data.mon_0_TemporalAverage.ts % time
% data.mon_0_TemporalAverage.ys % values
%
% data = vb_load(id, keep)
%
% keep == 0  deletes the HDF5 used to store simulation
% output, if keep==1 (default), it is left alone.
%
% data = vb_load(id, nodelete, dsets)
%
% Retrieves specific datasets per monitor, by default, {'ts' 'ys'} as
% currently these are the only two implemented, but in the future, 
% sensor data/details may be provided as well
%
% ys will have 4 dimensions, [mode, node, state variable, time] while ts
% is a column vector. 
%
% Note, the order of dimensions for ys is reversed from Python, because
% the underlying storage format, HDF5 stores in C-order, while MATLAB
% employs Fortran-ordered arrays. permute() as needed... 


if nargin < 3; keep = 1; end
if nargin < 4, dsets = {'ts' 'ys'}; end

vb_wait(sv, id);

info = vb_stat(sv);

rfnm = info{id}.result;
rinf = h5info(rfnm);

for i=1:length(rinf.Groups)
    g = rinf.Groups(i).Name(2:end);
    for j=1:length(dsets)
        dset = dsets{j};
        data.(g).(dset) = h5read(rfnm, ['/' g '/' dset]);
    end
end

if ~keep
    delete(rfnm);
end
