# Welcome to Omnisolver's documentation!


## Introduction
Omnisolver is a collection of Binary Quadratic Model solvers and a framework for implementing them.

### Benefits for the end-users
Omnisolver contains a selection of standard and more sophisticated algorithms for solving BQMs.
All solvers are available through intuitive CLI or from Python scripts as `dimod` based Samplers.

### Benefits For solver creators
Omnisolver allows developer to focus on algorithms instead of common tasks like handling 
input/output or creating CLI.

## Quick start

````{only} latex
```console
# install omnisolver and parallel tempering plugin
$ pip install omnisolver omnisolver-pt
# create an example input file (three frustrated spins)
$ echo "0 1 1.0    
> 1 2 1.0 
> 2 0 1.0" > instance.txt
# run solver, assume we use Ising model
$ omnisolver pt --vartype SPIN instance.txt
0,1,2,energy,num_occurrences
1,-1,-1,-1.0,1
```

````

````{only} html

```{termynal} termynal:my-id
:typeDelay: 10
:lineDelay: 500

- "# install omnisolver and parallel tempering plugin"
- value: pip install omnisolver omnisolver-pt
  type: input
- type: progress
- "# create an example input file (three frustrated spins)"
- value: echo "0 1 1.0    
  type: input
- value: 1 2 1.0
  type: input
  prompt: ">"
- value: 2 0 1.0" > instance.txt
  type: input
  prompt: ">"
- "# run solver, assume we use Ising model"
- value:  omnisolver pt --vartype SPIN instance.txt
  type: input
- 0,1,2,energy,num_occurrences
- 1,-1,-1,-1.0,1
```
````


````{only} latexpdf
## Documentation
```{toctree}
:maxdepth: 1
```
````
