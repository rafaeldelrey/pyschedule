import getopt
import sys
sys.path.append('../src')
from pyschedule import Scenario, solvers, plotters

n_night_shifts = 5
n_day_shifts = 5
n_tasks = n_night_shifts+n_day_shifts
horizon = n_tasks

S = Scenario('Shift_bounds',horizon=horizon)

R = S.Resource('P')

for i in range(n_night_shifts):
    # added some delay cost, so without any
    # constraint, there would be first 5 night shifts
    # and then 5 day shifts
    T = S.Task('N%i'%i,delay_cost=2)
    # the shift type of night shifts is -1
    T.shift_type = -1
    T += R

for i in range(n_day_shifts):
    T = S.Task('D%i'%i,delay_cost=1)
    # the shift type of day shifts is -1
    T.shift_type = 1
    T += R

for i in range(horizon):
    # for every set of periods 1..i, make sure that
    # there is always at most one more night shift than
    # day shifts and vice versa. Each capacity constraint
    # limits the sum of 'shift_types' in the range
    S += R[:i]['shift_type'] <= 1
    S += R[:i]['shift_type'] >= -1

if solvers.mip.solve(S,msg=0,kind='CBC'):
    opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
    if ('--test','') in opts:
        assert {T.start_value % 2 for T in S.tasks() if T.name.startswith('N')} == {0}
        assert {T.start_value % 2 for T in S.tasks() if T.name.startswith('D')} == {1}
        print('test passed')
    else:
        plotters.matplotlib.plot(S)
else:
    print('no solution found')
