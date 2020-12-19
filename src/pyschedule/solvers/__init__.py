#! /usr/bin/env python
'''
Copyright 2015 Tim Nonner

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

__doc__ = """
This module contains solvers that accept the pyschedule scenario format
as input. Each solver should correspond to a class which offers the
method "solve" that takes a scenario as minimal input. If a solution
exists, then a True should be returned, otherwise a False. The optimal solution
should be directly written to the passed scenario
"""

from . import mip
from . import mip_bigm
from . import ortools_cp_sat
from . import listsched
from . import z3_smt
