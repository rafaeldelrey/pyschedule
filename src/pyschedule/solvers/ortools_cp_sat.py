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

import collections
import copy
import sys

def solve(scenario,time_limit=None,copy_scenario=False,msg=False) :
    """ Integration of the ortools scheduling solver """
    try:
        from ortools.constraint_solver import pywrapcp
    except ModuleNotFoundError:
        raise Exception('ERROR: ortools is not installed')

    S = scenario
    if copy_scenario :
        S = copy.deepcopy(scenario)

    # create a Solver instance
    # see documentation at
    # http://google.github.io/or-tools/python/ortools/constraint_solver/pywrapcp.html#pywrapcp.Solver
    ort_solver = pywrapcp.Solver(S.name)

    # tasks
    # Initialize a dictionnary that maps task to FixedDurationIntervalVar
    task_to_interval = collections.OrderedDict()

    # Initialize a directory that maps eahc resource
    # to a list of FixedDurationIntervalVar
    # By default this list is empty, it will be appended later in the algorithm
    resource_to_intervals = {R : [] for R in S.resources()}
    resource_task_to_interval = collections.OrderedDict()

    # Map each Task to a FixedDurationIntervalVar
    # Documentation at
    # http://google.github.io/or-tools/python/ortools/constraint_solver/pywrapcp.html#pywrapcp.Solver.FixedDurationIntervalVar
    for task in S.tasks():
        task_name = task.name
        task_is_optional = False  # it's not part of the Task class, but must be passed to the ort_solver
        task_length = task.length
        lower_interval_bound = 0
        upper_interval_bound = S.horizon - task.length
        interval_from_task = ort_solver.FixedDurationIntervalVar(lower_interval_bound,
                                                                 upper_interval_bound,
                                                                 task_length,
                                                                 task_is_optional,
                                                                 task_name)
        task_to_interval[task] = interval_from_task

    # resource requirements
    for T in S.tasks():  # loop over tasks
        I = task_to_interval[T]  # get the FixedDuration interval for this task
        for RA in T.resources_req:  # loop over the resources required by this task
            # create an empty list which contains TODO comment
            RA_tasks = []
            for R in RA:  # each resource among all assigned resources
                # map the resource to a FixedDuration IntervalVar as well
                # this FixedDurationIntervalVar repesents the fact that the
                # resource is busy during this time interval
                I_ = ort_solver.FixedDurationIntervalVar(0,S.horizon-T.length,T.length,True,T.name+'_'+R.name)
                resource_to_intervals[R].append(I_)

                # stores this time interval into the RA_tasks list
                RA_tasks.append(I_)

                # tells that the resource occupation remains sync'ed with
                # the task schedule
                resource_task_to_interval[(R,T)] = I_
                ort_solver.Add(I.StaysInSync(I_))

                # if resources are fixed
                if T.resources is not None and R in T.resources :
                    ort_solver.Add(I_.PerformedExpr() == 1)

            # one resource needs to get selected
            ort_solver.Add(ort_solver.Sum([I_.PerformedExpr() for I_ in RA_tasks]) == 1)

    ra_to_tasks = S.resources_req_tasks()
    for RA in ra_to_tasks:
        tasks = list(ra_to_tasks[RA])
        T = tasks[0]
        for T_ in tasks[1:]:
            for R in RA:
                I  = resource_task_to_interval[(R,T)]
                I_ = resource_task_to_interval[(R,T_)]
                ort_solver.Add(I.PerformedExpr() == I_.PerformedExpr())

    # resources
    sequences = collections.OrderedDict()
    for R in S.resources():
        # The DisjunctiveConstraint constraint forces all interval vars into an non-overlapping
        # sequence. Intervals with zero duration can be scheduled anywhere.
        # See https://github.com/google/or-tools/blob/v8.0/ortools/constraint_solver/constraint_solver.h#L5271
        disj = ort_solver.DisjunctiveConstraint(resource_to_intervals[R], R.name)
        ort_solver.Add(disj)
        # stores this into the sequence dict
        # documentation at
        # https://developers.google.com/optimization/reference/python/constraint_solver/pywrapcp#sequencevar
        sequences[R] = disj.SequenceVar()

    # objective function
    # TODO: add whether the cost function is makespan or flowtime
    # TODO: bug, variables that are not part of the objective might not be finally defined
    # define the cost
    costs_to_consider = []
    for T in S.tasks():
        if T in task_to_interval and 'delay_cost' in T:
            cost_contribution = task_to_interval[T].EndExpr() * T.delay_cost
            costs_to_consider.append(cost_contribution)
    ort_objective_var = ort_solver.Sum(costs_to_consider)
    ort_objective = ort_solver.Minimize(ort_objective_var, 1)

    # precedences lax
    for P in S.precs_lax():
        ort_solver.Add(task_to_interval[P.task_right].StartsAfterEnd(task_to_interval[P.task_left]))
        # TODO: add offset, but this requires DependecyGraph which is not exposed via swig?
        
    # precedences tight
    for P in S.precs_tight():
        # if no offset
        if P.offset == 0:
            ort_solver.Add(task_to_interval[P.task_right].StartsAtEnd(task_to_interval[P.task_left]))
        else:  # dont' use the same method
            # we could use the same method, maybe check if there is a performance gain
            ort_solver.Add(task_to_interval[P.task_right].StartsAfterEndWithDelay(task_to_interval[P.task_left],
                                                                                  P.offset))

    # bound low
    for P in S.bounds_low():
        ort_solver.Add(task_to_interval[P.task].StartsAfter(P.bound))

    # bound up
    for P in S.bounds_up():
        ort_solver.Add(task_to_interval[P.task].StartsBefore(P.bound))

    # tight bound low
    for P in S.bounds_low_tight():
        ort_solver.Add(task_to_interval[P.task].StartsAt(P.bound))

    # tight bound up
    for P in S.bounds_up_tight():
        ort_solver.Add(task_to_interval[P.task].EndsAt(P.bound))

    # capacity TODO: this doesn't work
    for C in S.capacity():
        for SL in C.slices_sum():
            # ignore sliced capacity constraints
            if SL._start is not None or SL._end is not None:
               continue

            R = SL.resource
            
            coeff = C.SLA[SL]

            cap_tasks = []
            for T in S.tasks():
                w = coeff * SL.weight(T=T, t=0)
                if not w.is_integer():  # might be coeff=w=1.0
                    raise AssertionError("%s is not an integer." % w)
                else:
                    w = int(w)
                cap_tasks.append((resource_task_to_interval[R,T], w))
                ort_solver.Add(ort_solver.Sum([I.PerformedExpr() * w for I, w in cap_tasks]) >= C.bound)

    # creates search phases.
    vars_phase = ort_solver.Phase([ort_objective_var],
                    ort_solver.CHOOSE_FIRST_UNBOUND,
                    ort_solver.ASSIGN_MIN_VALUE)
    sequence_phase = ort_solver.Phase(list(sequences.values()),
                        ort_solver.SEQUENCE_DEFAULT)
    main_phase = ort_solver.Compose([sequence_phase, vars_phase])

    # creates the search log.
    search_log = ort_solver.SearchLog(100, ort_objective_var)

    # collect solution
    solution = ort_solver.Assignment()
    for T in S.tasks() :
        solution.Add(task_to_interval[T])
    for R in S.resources() :
        for I in resource_to_intervals[R] :
            solution.Add(I)
    collector = ort_solver.LastSolutionCollector(solution)

    # set limits (time limit im ms)
    if time_limit :
        ort_time_limit = int(time_limit*1000)
    else :
        ort_time_limit = int(1e8)
    branch_limit = int(1e8)
    failures_limit = int(1e8)
    solutions_limit = int(1e8)
    limits = (ort_solver.Limit(ort_time_limit, branch_limit, failures_limit, solutions_limit, True))

    # add log if msg is requested
    search_params = [limits, collector, ort_objective]
    if msg:
        search_params.append(search_log)

    # solves the problem.
    ort_solver.Solve(main_phase, search_params)

    # check for a solution
    if not collector.SolutionCount():
        if msg:
            print('ERROR: no solution found')
        return False
    solution = collector.Solution(0)

    # read last solution
    for T in S.tasks() :
        T.start_value = int(solution.StartMin(task_to_interval[T]))
        T.resources = [R for RA in T.resources_req for R in RA \
                       if collector.PerformedValue(0,resource_task_to_interval[(R,T)]) == 1]
    return True
