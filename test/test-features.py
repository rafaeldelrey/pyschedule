#Copyright 2020 Thomas Paviot (tpaviot@gmail.com)
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

import unittest
import warnings

from pyschedule import Scenario, Task, Resource, solvers

class TestFeatures(unittest.TestCase):
    def test_create_scenario(self) -> None:
        """ Scenario creation
        """
        scenario = Scenario('Scenario_1', horizon=10)
        self.assertIsInstance(scenario, Scenario)

    def test_create_single_task(self) -> None:
        scenario= Scenario('Scenario_2')
        task = scenario.Task('T')
        self.assertEqual(task.name, 'T')
        self.assertIsNone(task.start_value)
        # default lenght should be 1
        self.assertEqual(task.length, 1)
        # the creation of another task with the same name
        # should raise an exception
        with self.assertRaises(NameError):
            task_2 = scenario.Task('T')
        # the creation of a task with a non integer length
        # should raise an exception
        with self.assertRaises(ValueError):
            task_2 = scenario.Task('T2', length=4.2)
        # check the task is part of the scenario
        self.assertEqual(len(scenario.tasks()), 1)

    def test_create_multiple_tasks(self) -> None:
        scenario= Scenario('Scenario_2')
        tasks = scenario.Tasks(name='T', num=5, length=2)
        self.assertEqual(len(tasks), 5)
        # check task names. Tasks names should be T0, T1, T2, T3 and T4
        for idx, task in enumerate(tasks):
            self.assertEqual(task.name, 'T%i' % idx)
            self.assertEqual(task.length, 2)
        self.assertEqual(len(scenario.tasks()), 5)

    def test_create_single_resource(self) -> None:
        scenario= Scenario('Scenario_3')
        self.assertEqual(len(scenario.resources()), 0)
        res = scenario.Resource('R')
        self.assertIsInstance(res, Resource)
        self.assertIsNone(res.periods)
        self.assertEqual(res.name, 'R')
        self.assertEqual(res.size, 1)
        # check that this resource is part of the scenario
        self.assertEqual(len(scenario.resources()), 1)

    def test_create_multiple_resources(self) -> None:
        scenario= Scenario('Scenario_2')
        resources = scenario.Resources(name='R', num=5, size=2)
        self.assertEqual(len(resources), 5)
        # check task names. Tasks names should be T0, T1, T2, T3 and T4
        for idx, resource in enumerate(resources):
            self.assertEqual(resource.name, 'R%i' % idx)
            self.assertEqual(resource.size, 2)
        self.assertEqual(len(scenario.resources()), 5)

if __name__ == "__main__":
    unittest.main()
