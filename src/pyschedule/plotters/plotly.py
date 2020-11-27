# Copyright 2020 Thomas Paviot
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

from datetime import datetime, timedelta

def plot(scenario, hide_tasks=[], hide_resources=[],
         date_init=None, delta_t=None, data_type='Resource'):
    """
    Plot the given solved scenario using matplotlib

    Args:
        scenario:    scenario to plot
        hide_tasks: list of tasks to hide
        hide_resources: list of ressources to hide
        date_init: the initial datetime, by default tomorrow at 8 a.m.
        delta_t: the steptime, by default set to 1 hour
        data_type: 'Task' or 'Resource', whether you want one or the other on the y axis
    """
    try:
        import plotly.express as px
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundError("plotly and pandas are not installed")

    if not data_type in ['Task', 'Resource']:
        raise ValueError('data_type must be either Task or Resource')
    if date_init is None or delta_t is None:
        # by default, the start time is tomorrow at 8 am
        date_init = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(hours=24)
        # and delta_t is one hour
        delta_t = timedelta(hours=1)
    
    hide_tasks_str = [T for T in hide_tasks]
    # get solution tasks
    solution = scenario.solution()
    #tasks of zero length are not plotted
    solution = [(T,R,x,y) for (T,R,x,y) in solution if T not in hide_tasks_str]

    # convert solution list to 
    dd = []
    
    for s in solution:
        if s in hide_tasks_str:
            continue
        task, ress, start, end = s
        dd.append(dict(Task=task.name,
                       Start=date_init + start * delta_t,
                       Finish=date_init + delta_t * end,
                       Resource=ress.name))

    df = pd.DataFrame(dd)

    color_data = 'Task'  # by default
    if data_type == 'Task':
        color_data = 'Resource'

    fig = px.timeline(df, x_start="Start", x_end="Finish", y=data_type, color=color_data)
    fig.update_yaxes(autorange="reversed")
    fig.show()
