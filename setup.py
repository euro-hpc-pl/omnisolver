"""Setup script for omnisolver project."""
from setuptools import setup, find_packages


setup(
    name="omnisolver",
    entry_points={
        "console_scripts": ["omnisolver=omnisolver.cmd:main"],
        "omnisolver": ["random = omnisolver.random"]
    },
    install_requires=["dimod", "pluggy", "typing_extensions", "pyaml", "pandas"],
    tests_require=["pytest"],
    packages=find_packages(exclude=["tests"]),
    package_data={"omnisolver.random": ["random.yml"]},
)
