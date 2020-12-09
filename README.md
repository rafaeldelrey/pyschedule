[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8817f1dea5d443b9a7a6046f00c1ce29)](https://app.codacy.com/gh/tpaviot/pyschedule?utm_source=github.com&utm_medium=referral&utm_content=tpaviot/pyschedule&utm_campaign=Badge_Grade)
[![Azure Build Status](https://dev.azure.com/tpaviot/pyschedule/_apis/build/status/tpaviot.pyschedule?branchName=dev)](https://dev.azure.com/tpaviot/pyschedule/_build?definitionId=8)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/tpaviot/pyschedule/HEAD?filepath=example-notebooks)

# pyschedule (fork of the original project)

## About/Features
pyschedule is python package to compute resource-constrained task schedules. Some features are: 

-   **precedence relations:** e.g. task A should be done before task B
-   **resource requirements:** e.g. task A can be done by resource X or Y
-   **resource capacities:** e.g. resource X can only process a few tasks

pyschedule depends on mandatory python libraries:

- [Pulp](https://github.com/coin-or/pulp): python linear programming

as well os the optional (but strongly recommended) libraries:

- Matplotlib and/or Plotly for Gantt charts rendering

- the Jupyter suite

## Install on Unix/OSX/Windows

Install latest relase using pip:

```bash
pip install pyschedule
```

or conda

```bash
conda install -c conda-forge pyschedule
```

Run the development release:

Fist create a local copy of this repository:
```bash
git clone https://github.com/tpaviot/pyschedule
```
then install the development version:

```bash
cd pyschedule
pip install -r requirements-min.txt
```

## Getting started

Read the [Getting started](https://github.com/tpaviot/pyschedule/blob/dev/doc/getting-started.md) page.
