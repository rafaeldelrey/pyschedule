#! /usr/bin/env python
import sys
sys.path += ['../src','src']
from pyschedule import Scenario, Task, Resource, solvers, plotters
import copy, collections, traceback

# planning horizon for the planning which need it
horizon = 10

# solver feedback
msg = True

def solve_cbc(scenario):
    return solvers.mip.solve(scenario,kind='CBC',msg=msg)

def solve_glpk(scenario):
    return solvers.mip.solve(scenario,kind='GLPK',msg=msg)

def solve_cbc_bigm(scenario):
    return solvers.mip_bigm.solve(scenario,kind='CBC',msg=msg)

def solve_scip(scenario):
    return solvers.mip.solve(scenario,kind='SCIP',msg=msg)

def solve_scip_bigm(scenario):
    return solvers.mip_bigm.solve(scenario,kind='SCIP',msg=msg)

def solve_gurobi(scenario):
    return solvers.mip.solve(scenario,kind='GUROBI',msg=msg)

def solve_ortools(scenario):
    return solvers.ortools.solve(scenario, msg=msg)


solve_methods = [
solve_cbc,
solve_glpk,
solve_cbc_bigm,
solve_ortools
#solve_gurobi,
#solve_scip,
#solve_scip_bigm,
]

def two_task_scenario() :
    S = Scenario('Scenario_1',horizon=horizon)
    T1 = S.Task('T1')
    T2 = S.Task('T2')
    R1 = S.Resource('R1')
    R2 = S.Resource('R2')
    S += T1*2 + T2 #T1 has priority to break ties
    return S

def ZERO() :
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S['T1'].length = 0
    sols = ['[(T1, R1, 0, 0), (T2, R1, 0, 1)]']
    return S,sols

def NONUNIT():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S['T1'].length = 5
    sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 6)]']
    return S,sols

def BOUND() : # only test lower bound, upper bound is similar
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['T1'] > 3
    sols = ['[(T2, R1, 0, 1), (T1, R1, 3, 4)]']
    return S,sols

def BOUNDTIGHT() : # only test tight upper bound, lower bound is similar
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['T1'] <= 3
    sols = ['[(T2, R1, 0, 1), (T1, R1, 2, 3)]']
    return S,sols

def LAX() :
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['T2'] < S['T1']
    sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 2)]']
    return S,sols

def LAXPLUS() :
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['T2'] + 1 < S['T1']
    sols = ['[(T2, R1, 0, 1), (T1, R1, 2, 3)]']
    return S,sols

def TIGHT() :
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['T2'] <= S['T1']
    sols = ['[(T2, R1, 0, 1), (T1, R1, 1, 2)]']
    return S,sols

def TIGHTPLUS() :
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['T2'] + 1 <= S['T1']
    sols = ['[(T2, R1, 0, 1), (T1, R1, 2, 3)]']
    return S,sols

def LAXRES() :
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    P = S['T1'] + 2 < S['T2']*S['R2']
    S += P
    sols = ['[(T1, R1, 0, 1), (T2, R1, 3, 4)]']
    return S,sols

def ALT() :
    S = two_task_scenario()
    S['T1'] += S['R1']|S['R2']
    S['T2'] += S['R1']|S['R2']
    sols = ['[(T1, R1, 0, 1), (T2, R2, 0, 1)]','[(T1, R2, 0, 1), (T2, R1, 0, 1)]']
    return S,sols

def MULT() :
    S = two_task_scenario()
    S['T1'] += (S['R1'],S['R2'])
    S['T2'] += (S['R1'],S['R2'])
    sols = ['[(T1, R1, 0, 1), (T1, R2, 0, 1), (T2, R1, 1, 2), (T2, R2, 1, 2)]']
    return S,sols

def TASKSREQ() :
    S = two_task_scenario()
    RA = S['R1']|S['R2']
    S['T1'] += RA
    S['T2'] += RA
    S['T2'] += S['T1']*[S['R1'],S['R2']]
    sols = ['[(T1, R1, 0, 1), (T2, R1, 1, 2)]','[(T1, R2, 0, 1), (T2, R2, 1, 2)]']
    return S,sols

def CUMUL() :
    S = two_task_scenario()
    S['R1'].size = 3
    S['T1'] += S['R1']*2
    S['T2'] += S['R1']
    sols = ['[(T1, R1, 0, 1), (T2, R1, 0, 1)]']
    return S,sols

def CAP():
    S = two_task_scenario()
    S['T1'] += S['R1']|S['R2']
    S['T2'] += S['R1']|S['R2']
    S += S['R2']['length'] <= 0
    sols = ['[(T1, R1, 0, 1), (T2, R1, 1, 2)]']
    return S,sols

def CAPSLICE():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S += S['R1']['length'][:3] <= 1
    sols = ['[(T1, R1, 0, 1), (T2, R1, 3, 4)]']
    return S,sols

def CAPDIFF():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S.clear_objective()
    S += S['T1'] - S['T2']*2
    S += S['R1']['length'].diff <= 1
    sols = ['[(T1, R1, 8, 9), (T2, R1, 9, 10)]']
    return S,sols

def CAPDIFFSLICE():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S.clear_objective()
    S += S['T1'] - S['T2']*2
    S += S['R1']['length'][5:].diff <= 0
    S += S['R1']['length'][:5].diff <= 1
    sols = ['[(T1, R1, 3, 4), (T2, R1, 4, 5)]']
    return S,sols

def CAPMAX():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R2']
    S.clear_objective()
    S += S['T1']*2 + S['T2']
    S += S['R1']['length'][:1].max + S['R2']['length'][:1].max <= 1
    sols = ['[(T1, R1, 0, 1), (T2, R2, 1, 2)]']
    return S,sols

def SCHEDULECOST():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S['T1'].schedule_cost = -2
    S['T2'].schedule_cost = -1
    S += S['R1']['length'] <= 1
    sols = ['[(T1, R1, 0, 1)]']
    return S,sols

def PERIODS():
    S = two_task_scenario()
    S['T1'] += S['R1']
    S['T2'] += S['R1']
    S['T1'].delay_cost = 1
    S['T2'].delay_cost = 2
    S['R1'].periods = [1,3,4]
    S['T2'].periods = [3]
    sols = ['[(T1, R1, 1, 2), (T2, R1, 3, 4)]']
    return S,sols

def COSTPERPERIOD():
    S = two_task_scenario()
    S['T1'] += S['R1']|S['R2']
    S['T2'] += S['R1']|S['R2']
    S['T1'].delay_cost = 2
    S['T2'].delay_cost = 1
    S['R1'].cost_per_period = 10
    sols = ['[(T1, R2, 0, 1), (T2, R2, 1, 2)]']
    return S,sols


scenario_methods = [
ZERO,
NONUNIT,
BOUND,
BOUNDTIGHT,
LAX,
LAXPLUS,
TIGHT,
TIGHTPLUS,
LAXRES,
ALT,
MULT,
TASKSREQ,
CUMUL,
CAP,
CAPSLICE,
CAPDIFF,
CAPDIFFSLICE,
CAPMAX,
SCHEDULECOST,
PERIODS
]

#scenario_methods = [TIGHT]

solve_method_names = collections.OrderedDict([ ('%s.%s' % (solve_method.__module__,solve_method.__name__),solve_method)
                                             for solve_method in solve_methods ])
table = [[''] + list(solve_method_names.keys()) ]

for scenario_method in scenario_methods :
    scenario_name = scenario_method.__name__
    S,sols = scenario_method()
    print(S)
    row = [scenario_name]
    for solve_method_name in solve_method_names :
        print('###############################################')
        print('%s / %s' % (solve_method_name,scenario_name))
        solve_method = solve_method_names[solve_method_name]
        S_ = copy.deepcopy(S)
        try :
            solve_method(S_)
            sol = str(S_.solution())
            valid = ( sol in sols )
            row.append(valid)
            print(sol)
        except Exception as err:
            print(err)
            row.append('Error')
            traceback.print_exc()
    table.append(row)

# write output to file
s = ''
for row in table :
    s +=  ','.join([ str(x) for x in row ]) + '\n'
with open('solvers.csv','w') as f :
    f.write(s)
    f.close()

# plot table to screen
print('################ Results #########################')
try :
    import pandas as pd
    df = pd.DataFrame(table[1:])
    # take last two elements in method name
    df.columns = ['scenario'] + [ '.'.join(x.split('.')[-2:]) for x in table[0][1:] ]
    df = df.set_index('scenario')
    df = df.replace(True,'X').replace(False,'')
    print(df)
    with open('tmp.html','w') as f:
        f.write(df.to_html())
        f.close()
except :
    print('INFO: install pandas to get nicer table plot')
    print(table)
print('##################################################')
