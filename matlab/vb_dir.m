function info = vb_dir()
%
% info = vb_dir
%
% Get a directory of information of modules & classes available
% on the TVB server
%
% Returns a struct, with one field for each available module, with
% sub-fields for available classes, where the contents is the 
% documentation for that class.
%

url = 'http://localhost:8042/api/burst/dir';

info = loadjson(urlread(url))