"""Setup script for omnisolver project."""
from setuptools import setup, find_packages


setup(
    name="omnisolver",
    entry_points={"console_scripts": ["omnisolver=omnisolver.cmd:main"]},
    install_requires=["dimod", "typing_extensions", "pyaml", "pandas"],
    tests_require=["pytest"],
    packages=find_packages(exclude=["tests"]),
    package_data={"omnisolver": ["specifications/*.yml"]},
)
