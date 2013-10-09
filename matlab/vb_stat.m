function info = vb_stat(sv)
%
% Retrieve information on current simulations on TVB @ sv
%

url = [sv 'api/simulator/read'];

info = loadjson(urlread(url));