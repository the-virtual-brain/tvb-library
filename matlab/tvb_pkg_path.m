function folder = tvb_pkg_path
% tvb_pkg_path 
%
%   returns the folder containing the Python TVB package
%

[folder, name, ext] = fileparts(mfilename('fullpathext'));

% python pkg will be bla/bloo/matlab/../tvb
% so knock of the final '/matlab'
folder = folder(1:end-7);

