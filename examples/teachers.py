# test artefact for the case that pyschedule is
# read from folder
import sys
sys.path.append('../src')

import getopt
from pyschedule import Scenario, solvers, plotters

opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])

horizon = 20
S = Scenario('parallel_courses',horizon=horizon)

#size 2 means teacher can do two things in parallel
Teacher = S.Resource('Teachers',size=2)

Courses_English = S.Tasks('CE',num=10,delay_cost=1,plot_color='red',english=1)
Courses_Math = S.Tasks('CM',num=10,delay_cost=1,plot_color='green',math=1)

Courses_English += Teacher
Courses_Math += Teacher

S += Teacher['english'][0:horizon:1].max + Teacher['math'][0:horizon:1].max <= 1

if solvers.mip.solve(S,time_limit=600,msg=0):
    if ('--test','') in opts:
        assert len(set( T.start_value for T in Courses_English ) & set( T.start_value for T in Courses_Math )) == 0
        print('test passed')
    else:
        plotters.matplotlib.plot(S,show_task_labels=True)
else:
    print('no solution found')
