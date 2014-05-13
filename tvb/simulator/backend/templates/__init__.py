"Templates & code generation"

import os
import glob
import logging

log = logging.getLogger(__name__)

# expect templates here, eventually elsewhere
here = os.path.dirname(os.path.abspath(__file__))
log.debug('looking in %r for templates', here)

# eventually sep C, CL, etc.
filetypes = ['cu']
log.debug('template filetypes %r', filetypes)

for ft in filetypes:
    patt = os.path.join(here, '*.' + ft)
    log.debug('globbing for %r', patt)
    globals()[ft] = {}
    for f in glob.glob(patt):
        log.debug('reading %r', f)
        with open(f, 'r') as fd:
            globals()[ft][os.path.basename(f)] = fd.read()

