function nproc = vb_reset(sv, nproc)
%
% vb_reset(sv)
% 
% Reset TVB server sv, clearing work log and stopping/canceling 
% running simulations.
%
% NOTE This resets id values, so previous vb_stat information 
% is no longer valid
%
% vb_reset(sv, 2)
%
% Optionally, reset & specify how many CPUs to use for 
% simulatneous simulations. Default is 2, which is
% safe for most computers.
%
% Returns the number of CPUs used, as confirmed by server.
%

if nargin < 2, nproc = 2; end

url = [sv 'api/simulator/reset'];
pars = {'nproc' num2str(nproc)};

nproc = urlread(url, 'get', pars);