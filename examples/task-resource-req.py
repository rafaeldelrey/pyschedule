# test artefact for the case that pyschedule is
# read from folder
import getopt

import sys
sys.path.append('../src')

from pyschedule import Scenario, solvers, plotters, alt

opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])

horizon=10
S = Scenario('shift_bounds',horizon=horizon)

# define two employees
R = S.Resources('Employees_',num=2)

T0 = S.Task('Task0',delay_cost=3)
T0 += alt(R)

T1 = S.Task('Task1',delay_cost=1)
T1 += alt(R)

T1 += T0*R[0]
T0 += T1*R[0]

if solvers.mip.solve(S, msg=0):
    if ('--test','') in opts:
        assert T0.start_value == 0
        assert T1.start_value == 1
        print('test passed')
    else:
        plotters.matplotlib.plot(S, fig_size=(10, 5), vertical_text=False)
else:
    print('no solution found')
