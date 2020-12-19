#Copyright 2015 Tim Nonner
#
#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

__doc__ = """Z3 SMT solver"""

import collections
import copy
import sys

try:
    from z3 import Solver, Int, unsat, unknown
except ModuleNotFoundError:
    raise Exception('z3 is not installed')

#
# Doc at http://www.cs.toronto.edu/~victorn/tutorials/z3/SMT.html
#

def makeIntVar(sol, name, min_val, max_val):
    """ Create an Integer variable with name,
    minimal_value and maximal_value
    """
    v = Int(name)
    sol.add(v >= min_val, v <= max_val)
    return v

def solve(scenario,time_limit=None,copy_scenario=False,msg=False) :
    """ Integration of the ortools scheduling solver """
    S = scenario
    if copy_scenario :
        S = copy.deepcopy(scenario)

    # create a Solver instance
    smt_solver = Solver()

    # task to int dictionnary. Store all
    # tasks start time in a dictionnary
    task_IntVar = {}
    for task in S.tasks():
        task_name = task.name
        task_is_optional = False  # it's not part of the Task class, but must be passed to the ort_solver
        task_length = task.length
        lower_interval_bound = 0
        upper_interval_bound = S.horizon - task.length
        # create a variable for the task start
        task_start = makeIntVar(smt_solver, task_name + "_lower_bound", lower_interval_bound, upper_interval_bound)
        # store the variable in the dictionary
        task_IntVar[task] = task_start

    # precedences lax
    for P in S.precs_lax():
        print("Processing lax precedences")
        lv = task_IntVar[P.task_left]  # start_time for left task
        rv = task_IntVar[P.task_right]  # start_time for right task
        length = P.task_left.length  # duration for task left
        offset = P.offset
        length_plus_offset = length + offset
        # add the constraint lv + length + offset < rv
        smt_solver.add(lv + length_plus_offset <= rv)
    
    # precedences tight. Same code that above, change the "<="" to "==""
    for P in S.precs_tight():
        print("Processing tight precedences")
        lv = task_IntVar[P.task_left]  # start_time for left task
        rv = task_IntVar[P.task_right]  # start_time for right task
        length = P.task_left.length  # duration for task left
        offset = P.offset
        length_plus_offset = length + offset
        # add the constraint lv + length + offset < rv
        smt_solver.add(lv + length_plus_offset == rv)


    # bound low
    for P in S.bounds_low():
        print("Processing bounds low")
        task_start_time = task_IntVar[P.task]
        smt_solver.add(task_start_time >= P.bound)

    # bound up
    for P in S.bounds_up():
        print("Processing bounds low")
        task_start_time = task_IntVar[P.task]
        task_length = P.task.length
        smt_solver.add(task_start_time + task_length <= P.bound)

    # tight bound low
    for P in S.bounds_low_tight():
        print("Processing bounds low tight")
        task_start_time = task_IntVar[P.task]
        smt_solver.add(task_start_time == P.bound)

    # tight bound up
    for P in S.bounds_up_tight():
        print("Processing bounds up tight")
        task_start_time = task_IntVar[P.task]
        task_length = P.task.length
        smt_solver.add(task_start_time + task_length == P.bound)

    # check satisfiability
    sat_result  = smt_solver.check()

    if sat_result == unsat:
        print("No solution exists.")
        return False
    elif sat_result == unknown:
        print("No solution can be found.")
        return False

    # solve
    solution = smt_solver.model()

    if msg:
        print("Constraints:")
        for c in smt_solver.assertions():
            print("\t", c)
        print("Solver satistics:")
        for k, v in smt_solver.statistics():
            print("\t%s : %s" % (k, v))
        print("Solution:")
        for d in solution.decls():
                    print("\t%s = %s" % (d.name(), solution[d]))
    # read last solution
    #for T in S.tasks() :
    #    T.start_value = int(solution.StartMin(task_to_interval[T]))
    #    T.resources = [R for RA in T.resources_req for R in RA \
    #                   if collector.PerformedValue(0,resource_task_to_interval[(R,T)]) == 1]
    return True
