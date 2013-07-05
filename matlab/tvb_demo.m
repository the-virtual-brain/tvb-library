function ys = tvb_demo

% this isn't what I'd expect MATLAB users to write, but
% it demonstrates it can be done

tvb_init

cymex('x', 'from tvb.simulator.lab import *')
cymex('x', 'c = connectivity.Connectivity(speed=3.0)')
cymex('x', 'h = integrators.HeunDeterministic()')
cymex('x', 'model = models.Generic2dOscillator()')
cymex('x', 'mon = monitors.TemporalAverage()')
cymex('x', 's = simulator.Simulator(model=model, connectivity=c, integrator=h, monitors=(mon,))')
cymex('x', 's.configure()')

cymex('x', join(LF, {
'ys = []'
'for ((t, y),) in s(100):'
'    ys.append(y)'
'ys = array(ys)'
}))

% 4-D -> 2-D
cymex('x', 'ys = ys[:, 0, :, 0]')

ys = cymex('r', 'ys');

end


function out = CR()
out = char(13); % # sprintf('\r')
end

function out = LF()
out = char(10); % # sprintf('\n');
end

function out = join(glue, strs)
strs = strs(:)';
strs(2,:) = {glue};
strs = strs(:)';
strs(end) = [];
%out = cat(1, strs{:});
out = [strs{:}];
end

