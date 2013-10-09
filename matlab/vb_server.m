function server = vb_server

host = 'localhost';
port = 8042;



% can't touch this
server = sprintf('http://%s:%d/api/burst/', host, port);