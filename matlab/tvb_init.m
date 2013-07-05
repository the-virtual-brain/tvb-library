function tvb_init
% take care of initializing tvb interface

if ~exist('cymex')
	disp('MEX bridge to Python not found! Nothing will work!');
end

cymex x 
cymex('x', ['insert_path("' tvb_pkg_path '")']);
