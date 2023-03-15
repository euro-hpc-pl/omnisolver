
![Logo](https://raw.githubusercontent.com/euro-hpc-pl/omnisolver/master/logo.png)
*Omnisolver is a collection of Binary Quadratic Model solvers and a framework for implementing them.*

[![Build Status](https://travis-ci.org/omnisolver/omnisolver.svg?branch=master)](https://travis-ci.org/omnisolver/omnisolver)
[![Documentation Status](https://readthedocs.org/projects/omnisolver/badge/?version=latest)](https://omnisolver.readthedocs.io/en/latest/?badge=latest)



## Installation and getting started

Installing this package alone won't give you much benefit, unless of course you want to develop new omnisolver plugins. In that case, you can install `omnisolver` from pip:

```shell
pip install omnisolver
```

Algorithms for solving QUBO and Ising models are implemented in Omnisolver *plugins*. For instance, to use parallel tempering algorithm you need to install the `omnisolver-pt` package:

```shell
pip install omnisolver-pt
```

You can run the `omnisolver pt -h` command to see the command line usage.

## Citing

If you used the package or one of its plugins, please cite:

```text
@misc{https://doi.org/10.48550/arxiv.2112.11131,
  doi = {10.48550/ARXIV.2112.11131},
  
  url = {https://arxiv.org/abs/2112.11131},
  
  author = {Jałowiecki, Konrad and Pawela, Łukasz},
  
  keywords = {Software Engineering (cs.SE), Quantum Physics (quant-ph), FOS: Computer and information sciences, FOS: Computer and information sciences, FOS: Physical sciences, FOS: Physical sciences},
  
  title = {Omnisolver: an extensible interface to Ising spin glass solvers},
  
  publisher = {arXiv},
  
  year = {2021},
  
  copyright = {arXiv.org perpetual, non-exclusive license}
}
```
