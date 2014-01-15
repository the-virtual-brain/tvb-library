function url = vb_url(host, port)
%
% url = vb_url(host, port)
%
% For given host and port, compute the correct url for TVB server
%
% url = vb_url
%
% Use defaults, 'localhost', 8080
%

if nargin < 1, host = 'localhost'; end
if nargin < 2, port = 8080; end

url = sprintf('http://%s:%d/', host, port);
