---
hide:
  - navigation
---

<p align="center">
    <a href="https://github.com/euro-hpc-pl/omnisolver"><img src="assets/logo-large.png" alt="Omnisolver"></a>
</p>

---

<h1></h1>

<p align="center">
    <a href="https://github.com/euro-hpc-pl/omnisolver/actions/workflows/quality_checks.yml">
    <img src="https://github.com/euro-hpc-pl/omnisolver/actions/workflows/quality_checks.yml/badge.svg" alt="Tests"/>
    </a>
<a href="https://euro-hpc-pl.github.io/omnisolver">
<img alt="Docs" src="https://img.shields.io/github/actions/workflow/status/euro-hpc-pl/omnisolver/quality_checks.yml?label=Docs">
</a>
</p>

**Documentation:** https://euro-hpc-pl.github.io/omnisolver 

**Source code:** https://github.com/euro-hpc-pl/omnisolver

---

Omnisolver is a collection of Binary Quadratic Model solvers and a framework for implementing them.



## Why Omnisolver?

### Benefits for the end-users

Omnisolver contains a selection of standard and more sophisticated algorithms for solving BQMs. All solvers are available through intuitive CLI or from Python scripts as dimod based Samplers.

### Benefits for solver creators

Omnisolver allows developer to focus on algorithms instead of common tasks like handling input/output or creating CLI.

## Quickstart

<!-- termynal -->

```
# Install base omnisolver package
$ pip install omnisolver
---> 100%
Successfuly installed omnisolver
# Install chosen plugins (e.g. parallel-tempering solver)
$ pip install omnisolver-pt
---> 100%
Successfuly installed omnisolver-pt
# Create an instance file in COOrdinate format
$ echo "0 1 1.0
> 1 2 1.0
> 2 0 1.0" > instance.txt
# Run solver
$ omnisolver pt --vartype SPIN instance.txt
0,1,2,energy,num_occurrences
1,-1,-1,-1.0,1
```

## What's next?

Here are some resources to get you started:

- Start with user guide to learn about the installation methods and general usage patterns.
- Discover available solvers in our plugin list.
- If you are interested in developing your own solver, or are interested in in-depth details of how the Omnisolver
  works, check our solver creator guide and reference manual.

## Citing

If you used Omnisolver in your research, consider citing it in your paper.
You can use the following BibTeX entry:

```text
@article{omnisolver2023,
    title = {Omnisolver: An extensible interface to Ising spin–glass and QUBO solvers},
    journal = {SoftwareX},
    volume = {24},
    pages = {101559},
    year = {2023},
    doi = {https://doi.org/10.1016/j.softx.2023.101559},
    url = {https://www.softxjournal.com/article/S2352-7110(23)00255-8/},
    author = {Konrad Jałowiecki and {\L}ukasz Pawela},
}
```
