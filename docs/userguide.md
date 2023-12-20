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

If you are familiar with Ising model and QUBO, you can skip this section entirely,
as Binary Quadratic Models are just an umbrella term for those two optimization problems.

If, on the other hand, you are new to this topic, all you need to know is that Binary Quadratic Models are optimization problems in which one attempts to minimize the following function:

$$
F(x_1, x_2, \ldots, x_N) = \sum_{i=1}^N a_i x_i + \sum_{i, j} b_{ij} x_i x_j. + \text{const.}
$$

Here all $a_i$ and $b_{ij}$ are some fixed real numbers called the problem coefficients.

Importantly, in BQMs the variables are dichotomous, which means that $x_i$ can assume only one of two possible values. There are essentially two choices for the domain of $x_i$:

- $x_i \in \{0, 1\}$: in this case, the problem is called Quadratic Unconstrained Binary Optimization (QUBO). When using QUBO model, it is customary to denote the cost function by $Q$ and the variables by $q_i$:

$$
  Q(q_1, q_2, \ldots, q_N) = \sum_{i=1}^N a_i q_i + \sum_{i, j} b_{ij} q_i q_j. + \text{const.}
$$

- $x_i \in \{-1, 1\}$: in this case we call the objective function an Ising model Hamiltonian. The Ising model is deeply rooted in physics, where it is used to model ferromagnetism. It is customary to denote the Ising Hamiltonian by $H$, the decision variables by $s_i$, and the coefficients by $h_i$ and $J_{ij}$:

$$
  H(s_1, s_2, \ldots, s_N) = \sum_{i=1}^N h_i s_i + \sum_{i, j} J_{ij} s_i s_j. + \text{const.}
$$

The second sum in all the equations above runs over all pairs $(i,j)$ with $i\ne j$. However, when specifying the cost function, we typically ommit the coefficients that are equal to zero. As an example, here is a possible Ising Hamiltonian:

$$
H(s_1, s_2, s_3) = -s_1 + 2s_2 + 2s_2 s_3 - 2s_1s_3
$$

For such a Hamiltonian we have $h_1 = -1, h_2 = 2, J_{23}=2, J_{13}=-2$. The omitted coefficients $h_3$ and $J_{13}$, as well as the constant offset are implicitly equal to zero.

### Input and output file formats

#### Input files
The Omnisolver understands input COOrdinate format (COO). COO files are plain text files with comprising rows of the form `i j Q_ij` where:

- `i` and `j` are indices of variables,
- `Q_ij` is either a quadratic coefficient corresponding to `i`-th and `j`-th variable if `i`$\ne$ `j`, or a linear coefficient corresponding to `i`-th variable if `i=j`.

Let's take an example Ising Hamiltonian:

$$
H(s_1, s_2, s_3) = -s_1 + 1.2s_2 + 2s_2 s_3 - 2.5s_1s_3,
$$

the corresponding COO file would look like this:

```text
1 1 -1
2 2 1.2
2 3 2
1 3 -2.5
```

There are several things to note here:

- the order of rows is unimportant. For instance, the following file is equivalent to the previous one:
   ```text   
   2 2 1.2
   1 3 -2.5
   2 3 2
   1 1 -1
   ```
- The order of the variables in quadratic terms is unimportant (but see caveat below). Therefore, the following file is equivalent to the first one:
    ```text
    2 2 1.2
    3 1 -2.5
    3 2 2
    1 1 -1 

!!! warning 
    If you specify the same quadratic term for the second time with reversed order of variables, both of the terms will be taken into account. Therefore, the following file is also equivalent to all the previous ones:
    ```text
    2 2 1.2   
    3 2 2
    1 1 -1
    3 1 -1.5
    1 3 -1
    ```

## Solving BQMs using Omnisolver's CLI

## Advanced usage: using Omnisolver from Python scripts
