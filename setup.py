"""Setup script for omnisolver project."""
from setuptools import setup, find_namespace_packages

with open("README.md") as readme:
    long_description = readme.read()


setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="omnisolver",
    entry_points={
        "console_scripts": ["omnisolver=omnisolver.cmd:main"],
        "omnisolver": ["random = omnisolver.random"],
    },
    setup_requires=["setuptools_scm"],
    install_requires=["dimod", "numpy>=1.17.0", "pluggy", "typing_extensions", "pyaml", "pandas"],
    tests_require=["pytest"],
    packages=find_namespace_packages(exclude=["tests"]),
    package_data={"omnisolver.random": ["random.yml"]},
)
