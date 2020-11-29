#! /usr/bin/env python
import getopt
import sys
sys.path.append('../src')

from pyschedule import Scenario, solvers, plotters

horizon = 10
S = Scenario('Scenario',horizon=horizon)
tasks = S.Tasks('T',num=int(horizon/2),is_group=True,delay_cost=2,state=1)
breaks = S.Tasks('B',num=int(horizon/2),is_group=True,delay_cost=1,state=-1)

R = S.Resource('R')
tasks += R
breaks += R

# ensure that state is always between 0 and 1
for t in range(horizon):
    S += R['state'][:t] <= 1
    S += R['state'][:t] >= 0

if solvers.mip.solve(S, msg=False):
    opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
    if ('--test','') in opts:
        # use a set comprehension assert
        assert list({T.start_value % 2 for T in tasks})[0] == 0
        assert list({T.start_value % 2 for T in breaks})[0] == 1
        print('test passed')
    else:
        plotters.matplotlib.plot(S, fig_size=(10, 5))
else:
    print('no solution found')
