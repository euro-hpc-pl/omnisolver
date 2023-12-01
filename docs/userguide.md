# User guide

This guide focuses on using Omnisolver from the perspective of the end-user wanting
to leverage pre-existing solvers in their work. If you are rather interested in 
creating your own solvers, see Solver creator guide.

This guide covers the following topics:

- Overview of Omnisolver functionalities.
- Prerequisites
- Installation.
- Key concepts:
  - Binary Quadratic Models.
  - Input nad output file formats.
- Solving BQMs using Omnisolver's command line interface (CLI).
- Advanced usage: using Omnisolver from Python scripts.

## Overview

Omnisolver allows you to use to leverage several different solvers using a unified CLI interface.
The Omnisolver takes case of reading input files, and serializing the outputs, ensuring full
interoparability between implemented solvers. 

Additionally, since Omnisolver is based on the dimod framework, all solvers can also be used
from Python scripts. This is useful if you are planning to use Omnisolver in more complex 
scenarios, e.g. if instantiating the solvers takes significant amount of time.

## Prerequisites

Omnisolver requires relatively modern version of Python (at least 3.9). It was tested on
GNU/Linux systems, but it should also work on other platforms. Please note that specific plugins
might have their own requirements.

Naturally, Omnisolver uses several third-party packages. However, you don't need to install them
manually, as they will be automatically installed when installing Omnisolver using any of the
suported methods.

## Installation

!!! tip
    We encourage you to use fresh virtual environments when starting a new project. It reduces
    the risk of running into dependency conflicts as well as the risk of messing up your existing
    environment.

Omnisolver's architecture is based on plugins. The core package provides only the
plugin framework and the random solver (serving as a plugin example) which is not particularly
useful. Therefore, to actually use Omnisolver, you will also need to install the plugin
including the solver(s) that you want to use. In this guide, we will use Parallel Tempering
solver, included in the `omnisolver-pt` plugin.

### From PyPI

Omnisolver and its plugins build in Euro HPC project are available from Python Package Index (PyPI). 
To install the latest version of the base `omnisolver` package and `omnisolver-pt` plugin run
```bash
pip install omnisolver omnisolver-pt
```

### From source

The core Omnisolver package can also be installed from source. This is especially useful if you
plancontributing to Omnisolver.

To install from source, clone the Omnisolver's repository using your preferred method:

=== "SSH"

    ```bash
    git clone git@github.com:euro-hpc-pl/omnisolver.git
    ```

=== "HTTPS"
    ```bash
    git clone https://github.com/euro-hpc-pl/omnisolver.git
    ```
    
=== "GitHub CLI"
    ```bash
    gh repo clone euro-hpc-pl/omnisolver
    ``` 

Then, change directory into the `omnisolver` directory and install the package:

```bash
cd omnisolver && poetry install
```

## Key concepts

### Binary Quadratic Models

### Input and output file formats

## Solving BQMs using Omnisolver's CLI

## Advanced usage: using Omnisolver from Python scripts
