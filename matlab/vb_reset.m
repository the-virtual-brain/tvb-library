function nproc = vb_reset(nproc)
%
% vb_reset()
% 
% Reset TVB server, clearing work log and stopping/canceling 
% running simulations.
%
% NOTE This resets id values, so previous vb_stat information 
% is no longer valid
%
% vb_reset(2)
%
% Optionally, reset & specify how many CPUs to use for 
% simulatneous simulations. Default is 2, which is
% safe for most computers.
%
% Returns the number of CPUs used, as confirmed by server.
%

if nargin < 1, nproc = 2; end

url = 'http://localhost:8042/api/burst/reset';
pars = {'nproc' num2str(nproc)};

nproc = urlread(url, 'get', pars);