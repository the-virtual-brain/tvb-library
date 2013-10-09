
addpath urlread2 jsonlab

urlread('http://localhost:8042/api/burst/reset', 'get', {'nproc' '6'})

opt.wd = pwd;
opt.model.class = 'Generic2d';
opt.model.a = 2.49024;
opt.model.b = 0:5;
opt.connectivity.weights = eye(3);
js = savejson('opt', opt);
[param, header] = http_paramsToString({'js' js}, 1);
[output, ~] = urlread2('http://localhost:8042/api/burst/create', 'GET', param, header)


% need to specfiy current working directly for results h5 file

urlread('http://localhost:8042/api/burst/read')

urlread('http://localhost:8042/api/version')

info = loadjson(urlread('http://localhost:8042/api/burst/dir'))

