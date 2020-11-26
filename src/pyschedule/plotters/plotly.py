'''
Copyright 2020 Thomas Paviot

Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''


def plot(scenario,img_filename=None,resource_height=1.0,show_task_labels=True,
         color_prec_groups=False,hide_tasks=[],hide_resources=[],task_colors=dict(),fig_size=(15,5),
		 vertical_text=False) :
	"""
	Plot the given solved scenario using matplotlib

	Args:
		scenario:    scenario to plot
		msg:         0 means no feedback (default) during computation, 1 means feedback
	"""
	import random
	try:
		import plotly.express as px
		import pandas as pd
	except ImportError:
		raise ModuleNotFoundError("plotly and pandas are not installed")

	S = scenario
	
	df = pd.DataFrame([dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Resource="Alex"),
                       dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Resource="Alex"),
                       dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Resource="Max")
	])

	fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
	fig.update_yaxes(autorange="reversed")
	fig.show()
