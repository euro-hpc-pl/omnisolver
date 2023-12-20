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

### Input file format

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
   ```

!!! warning 
    If you specify the same quadratic term for the second time with reversed order of variables, both of the terms will be taken into account. Therefore, the following file is also equivalent to all the previous ones:
    ```text
    2 2 1.2   
    3 2 2
    1 1 -1
    3 1 -1.5
    1 3 -1
    ```


You might observe that the type of the problem (QUBO or Ising) is not specified in the input file. Moreover, it clearly cannot be inferred from the contents of the input file. The Omnisolver handles this via a command line switch, as we will see later in this guide.
## Solving BQMs using Omnisolver's CLI

Once you determined which solver you want to use, it is time to solve a problem. As already mentioned, in this guide
we will use `omnisolver-pt` plugin. If you followed the guide and installed everything, running `omnisolver -h` should
give the following output:

```text
usage: omnisolver [-h] {pt,random} ...

options:
  -h, --help   show this help message and exit

Solvers:
  {pt,random}

```

The output tells us that we can run `omnisolver pt <arguments>`. Let's inspect what the arguments should
look like by running `omnisolver pt -h`:

```text
usage: omnisolver pt [-h] [--output OUTPUT] [--vartype {SPIN,BINARY}] [--num_replicas NUM_REPLICAS] [--num_pt_steps NUM_PT_STEPS] [--num_sweeps NUM_SWEEPS] [--beta_min BETA_MIN] [--beta_max BETA_MAX] [--num_states NUM_STATES] input

Parallel tempering sampler

positional arguments:
  input                 Path of the input BQM file in COO format. If not specified, stdin is used.

options:
  -h, --help            show this help message and exit
  --output OUTPUT       Path of the output file. If not specified, stdout is used.
  --vartype {SPIN,BINARY}
                        Variable type
  --num_replicas NUM_REPLICAS
                        number of replicas to simulate (default 10)
  --num_pt_steps NUM_PT_STEPS
                        number of parallel tempering steps
  --num_sweeps NUM_SWEEPS
                        number of Monte Carlo sweeps per parallel tempering step
  --beta_min BETA_MIN   inverse temperature of the hottest replica
  --beta_max BETA_MAX   inverse temperature of the coldest replica
  --num_states NUM_STATES
                        number of lowest energy states to keep track of.
```

Let's break it down:

- The sampler expects a single positional argument `input` which should be a path to the input file
  in the format we discussed in the previous section.
- Variable type is controlled by specifiying either `--vartype SPIN` (for Ising) or `--vartype BINARY` (for QUBO)
- The output will be printed to stdout or, if `--output OUTPUT` is specified, stored in a given location.

All the bullet points above are also true for other samplers - they constitute the part of the common interface.
The other parameters are optional and algorithm-specific. By tuning them, you can improve performance, quality
of solution or, as is the case here, number of states returned. Most samplers define sane defaults for optional
parameters, so in principle all of them should be invokeable simply as:

```shell
omnisolver <solver name> <input file> --vartype <desired vartype>
```

Let us run our sampler on a simple problem defined in the previous section. To simplify, we will use zero-based
indexing (so all the indices are decreased by 1). Here's our input file, which we will save as `"instance.txt"`:

```text
0 0 -1
1 1 1.2
1 2 2
0 2 -2.5
```

Let us use the default arguments first. We can run:
```shell
omnisolver pt instance.txt --vartype SPIN
```
which should produce output roughly similar to the following one:
```text
0,1,2,energy,num_occurrences
1,-1,1,-6.7,1
```

The actual output might be different, because the parallel-tempering sampler is randomized. In our case, we obtained a single sample $s_0=1, s_1=-1, s_2=1$ with the corresponding energy of $-6.7$. The last column, `num_occurrences` signifies that this particular sample ocured once. This will always be the case for the PT sampler. However, other samplers might report a given sample multiple times.

Lastly, let's add some optional arguments. For instance, let's request 5 states instead of just one:

```text
0,1,2,energy,num_occurrences
-1,1,-1,-2.3,1
-1,-1,-1,-0.7,1
1,-1,1,-6.7,1
-1,-1,1,0.2999999999999998,1
1,1,1,-0.2999999999999998,1
```

As expected we obtained multiple samples. Be aware that the samples are not sorted by energy!

## Advanced usage: using Omnisolver from Python scripts

All samplers in Omnisolver can be also used in Python scripts. The steps are roughly as follows:

- From the sampler's documentation, determine the class which is used for sampling.
- Import this class and instantiate it.
- Create an instance of `BQM`.
- Run `sampler.sample` method.

In case of the parallel-tempering, the sampler is implemented by class `omnisolver.pt.sampler.PTSampler`.

We can import it as follows:

```python
from omnisolver.pt.sampler import PTSampler
```

The `PTSampler` can be instantiated without arguments, so instantiating it is really simple:

```python
sampler = PTSampler()
```

We can now define the Binary Quadratic Model. For simplicity, we will use the same coefficients as previously:
```python
from dimod import BQM

bqm = BQM({0: -1, 1: 1.2}, {(1, 2): 2, (0, 2): -2.5}, vartype="SPIN")
```

Finally, we are able to solve our problem and print the solution:

```python
result = sampler.sample(bqm)
print(result.first.energy)
```

In our case, we obtained the same solution as previously:
```python
Sample(sample={0: 1, 1: -1, 2: 1}, energy=-6.7, num_occurrences=1)
```
