# Tutorial: creating a sampler

In this tutorial, we are going to discuss how to create a new omnisolver
plugin. The sampler provided by the plugin will be a simple one returning
purely random solutions. It is not terribly useful in and of itself, but
we don't want to divert reader's attention from the process of creating
the plugin.

The process involves the following steps:

- Creating a package in which our plugin will live.
- Implementing a dimod-based sampler.
- Defining plugin metadata.


## Prerequisites

Detailed discussion of Python packages is out of the scope of this tutorial,
and hence we assume that the reader is familiar with this concept. If you are
new to creating packages, we recommend taking a look at the [setuptools
Quick start guide](https://setuptools.pypa.io/en/latest/userguide/quickstart.html).

We recommend creating a new virtual environment for experimenting with your plugin.

## Initial layout  package

Our package will be called `dummysolver`. The listing below summarizes its initial
layout.

```text
+-- dummysolver
|   |-- __init__.py
|   +-- solver.py
|-- pyproject.toml
```

We start with three files:

- `pyproject.toml`: a file describing project's metadata, including its dependencies. 
- `dummysolver/__init__.py`: a file marking the `dummysolver` directory as a package. Initially empty, we will later define our plugin there.
- `dummysolver/solver.py`: a Python file in which we are going to place the implementation of our sampler.

## The initial pyproject.toml file

The pyproject.toml file describes the metadata of the project. In our example, the file is pretty minimal and its contents read as follows:

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
version = "0.0.1"
name = "dummysolver"
description = "Simple all random solver"
requires-python = ">=3.8"
dependencies = ["omnisolver ~= 0.0.3"]

[tool.setuptools.packages]
find = {}
```

The metadata are pretty explanatory. We include a single dependency - the core `omnisolver` package. This package, in turn, depend on `dimod`, which hence becomes our transitive dependency. Thanks to it, we can later import classes and mixins needed for implementing our sampler.

Let's leave the `solver.py` file empty for now. We should be able to install our package by executing the following command in the root directory of our project.

```shell
pip install -e .
```

If everything went as expected, we should be able to import it from our interpreter,
like this:

```python
import dummysolver
```

Now that we have an installable package, it is time to populate it. We start by implementing a simple solver.

## Implementing the solver

Put the following content into your `solver.py` file:

```python
import dimod
import random


class DummySolver(dimod.Sampler):
    """A dummy sampler returning random solutions for given BinaryQuadraticModel."""

    @property
    def parameters(self):
        """Parameters accepted by this sampler."""
        return {"num_solutions": []}

    @property
    def properties(self):
        """Properties of this sampler."""
        return {}

    def sample(self, bqm, **parameters):
        """Uniformly sample given BQM."""
        num_samples = parameters.pop("num_solutions", 1)
        assert (
            not parameters
        ), f"Unrecognized parameters: {parameters}"

        possible_values = tuple(bqm.vartype.value)
        solutions = [
            [
                random.choice(possible_values)
                for _ in range(bqm.num_variables)
            ]
            for _ in range(num_samples)
        ]

        return dimod.SampleSet.from_samples_bqm(
            solutions, bqm
        ).aggregate()
```

We imported two modules. The `dimod` module is here to provide a base class for our sampler, the `dimod.Sampler` class. The `random` module is imported to provide us with a pseudorandom number generator.

For our implementation to work we need to provide one of the three possible methods: `sample`, `sample_ising` or `sample_qubo`. We decided to go with `sample` method, in which we implement sampling from an instance of Binary Quadratic Model, which represents either Ising model or the QUBO model. The `sample` method accepts mandatory `bqm` parameter and keyword arguments - but this is purely to conform with the interface defined in `dimod`. In practice, we recognize only one keyword argument, `num_solutions`, which defaults to 1.

The implementation of the `sample` method is pretty easy: we just draw our solutions at random. However, when implementing a real plugin, this is where the actual algorithm solving QUBO or Ising model instance would go.

We can now move to defining the plugin.

## Defining the plugin

To define the plugin, we need to perform the following tasks:

- Creating a function returning the plugin object. This typically involces writing a YAML file with plugin's description.
- Adding the plugin definition to the pyproject.toml file.

### The YAML file

We start with the YAML file, which we place at `dummysolver/dummy.yml`. It should have the following content:

```yaml
schema_version: 1
name: "dummy"
sampler_class: "dummysolver.solver.DummySolver"
description: "Uniformly random dummy sampler"

init_args: []
sample_args:
  - name: "num_solutions"
    help: "number of sampled solutions"
    type: int
    default: 1
```

The first key, `schema_version`, informs that we are using the first version of the Omnisolver plugin definition. Currently, this is the only version, but it might change in the future - including it in your YAML ensures compatibility with future Omnisolver releases. The `name` gives a name to your sampler. This name along with the `description`, will be visible in Omnisolver's CLI.

The `sampler_class` key contains a module path to the sampler we want to expose in the plugin. Finally, the `init_args` and `sample_args` describe arguments that we need to
pass to the sampler. The `init_args` describes parameters passed to the solver's `__init__` method. Since we didn't implement one for our solver, we leave this list empty. The `sampler_args` comprises list of the arguments that can be passed to the `sample` method. We have only one argument, `num_solutions`. We describe its type (`int`), provide the default value (1), and give some helpful description.

The YAML file itself does not provide any new functionallities, and we need to pair
it with a little bit of a boilerplate code that we'll place in packages `__init__.py`
file.

### Plugin definition

To make our YAML useful, we need to inform the package to create a plugin of it. This can be done by adding the following lines to the package's `__init__.py` file.

```python
from omnisolver.plugin import (
    plugin_from_specification,
    plugin_impl,
)
from pkg_resources import resource_stream
from yaml import safe_load


@plugin_impl
def get_plugin():
    """Construct plugin from given yaml file."""
    specification = safe_load(
        resource_stream("dummysolver", "dummy.yml")
    )
    return plugin_from_specification(specification)
```

### Adding definition to pyproject.toml file

The last thing we need to do is to expose the plugin to Omnisolver. This is done by adding the following line in `pyproject.toml`.

```toml
[project.entry-points."omnisolver"]
dummy = "dummysolver"
```

This essentially tells the build system, that we implemented an Omnisolver plugin called "dummy", and it resides in `dummysolver` package.

## Testing things out

Now that our work is done, it's time to test it. Install your package by running

```shell
pip install .
```

If everything went correctly, our new sampler should be visible in Omnisolver's CLI.
We can test it by invoking `omnisolver -h`. Here is what the output should look like,
assuming you didn't install any other plugin:

```text
usage: omnisolver [-h] {dummy,random} ...

options:
  -h, --help      show this help message and exit

Solvers:
  {dummy,random}
```

As you can see, there are two samplers present. The random sampler is built in into the core Omnisolver package, and the dummy solver is provided by our package, so everything seems to work correctly.

Now, try running `omnisolver dummy -h`. The output should look as follows:

```text
usage: omnisolver dummy [-h] [--output OUTPUT] [--vartype {SPIN,BINARY}]
                        [--num_solutions NUM_SOLUTIONS]
                        input

Uniformly random dummy sampler

positional arguments:
  input                 Path of the input BQM file in COO format. If not specified, stdin is
                        used.

options:
  -h, --help            show this help message and exit
  --output OUTPUT       Path of the output file. If not specified, stdout is used.
  --vartype {SPIN,BINARY}
                        Variable type
  --num_solutions NUM_SOLUTIONS
                        number of sampled solutions
```

Nice! We see that our `num_solutions` parameter is there. There are also other CLI parameters added by Omnisolver. Let's try running our sampler now. To do this, first
create an example instance file. For example, let's place the following content in
the file `instance.txt`.

```text
1 2 1.5
0 1 -1
0 2 -3
```

This example file defines the function to be optimized by:
$$
f(x_0, x_1, x_2) = 1.5x_1x_2 - x_0x_1-3x_0x_2
$$
Observe, that the file does not define if we are using the Ising or the QUBO model; instead, this is controlled by the `--vartype` parameter to the Omnisolver CLI.

Now, let's try our sampler out. Run:

```shell
omnisolver dummy --vartype SPIN instance.txt
```

The output might look as follows:
```text
0,1,2,energy,num_occurrences
-1,-1,-1,-2.5,1
```

We see that what we got is a CSV file with columns for each variable, energy and number of occurrences. Here, we only got one solution (remember? It was the default value of `num_solutions`.), corresponding to $x_0=x_1=x_2=-1$.

Now, let's try obtaining more solutions at once. Run:
```shell
omnisolver dummy --vartype SPIN --num_solutions 10 instance.txt
```

This time, the output might look as follows:
```text
0,1,2,energy,num_occurrences
1,1,-1,0.5,3
-1,-1,-1,-2.5,1
1,1,1,-2.5,1
-1,1,-1,-3.5,3
1,-1,1,-3.5,1
1,-1,-1,5.5,1
```
Observe, that the same solutions are grouped together, and the `num_occurrences` column informs how many times given solution occurred.

This concludes our tutorial. At this point we recommend that you try to implement an omnisolver plugin with your favourite optimization algorithm.
