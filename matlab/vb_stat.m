function info = vb_stat()
%
% Retrieve information on current simulations.
%

url = 'http://localhost:8042/api/burst/read';

info = loadjson(urlread(url));