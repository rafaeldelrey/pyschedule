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

try:
    import networkx as nx
    HAVE_NETWORKX = True
except ModuleNotFoundError:
    HAVE_NETWORKX = False

def sort_with_precs(scenario) :
    """
    returns the tasks of the given scenario sorted according to the
    lax precedence constraints and next according to the task length,
    where large tasks have priority
    """
    S = scenario
    G = nx.DiGraph()
    G.add_nodes_from(S.tasks())
    G.add_edges_from([ (P.task_left,P.task_right) for P in S.precs_lax() ])
    task_list = nx.algorithms.topological_sort(G)
    return task_list


#TODO: list as parameter of solving procedure
def solve(scenario,solve_method,task_list=None,batch_size=1,plot_method=None,msg=0) :
    """
    Iteratively adds tasks and uses solve_method to integrate these
    tasks into the schedule.

    Arguments:
        scenario   : the scenario to solve
        task_list  : list of all tasks which defines the order in which all tasks are
                     added to the schedule
        batch_size : the number of tasks to integrate in the schedule at a time
    """
    if not HAVE_NETWORKX:
        raise ModuleNotFoundError("networkx not installed")
    S = scenario

    if task_list is None :
        task_list = sort_with_precs(S)

    constraints = S._constraints # keep references and clear old reference list
    S._constraints = []

    #non_objective_tasks = [ T for T in task_list if not T.objective ]
    for T in task_list :
        S -= T #remove all tasks which are not part of objective

    def batches(tasks, batch_size):
        for i in range(0, len(tasks), batch_size):
            yield tasks[i:i+batch_size]

    for batch in batches(task_list,batch_size) :
        if msg :
            print('INFO: batch for list scheduling '+','.join([ str(T) for T in batch]))
        for T in batch :
            S += T
        S._constraints = [ C for C in constraints if set(C.tasks()).issubset(set(S.tasks())) ]

        solve_method(S)
        if plot_method is not None:
            plot_method(S)

        for T in S.tasks():
            S += T >= T.start_value
    return True
