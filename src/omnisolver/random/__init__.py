"""Package with purely random reference sampler.

This also serves as a reference implementation of omnisolver plugins.
"""
from importlib import resources

from yaml import safe_load

from omnisolver.common.plugin import Plugin, plugin_from_specification


def get_plugin() -> Plugin:
    """Get package name and resource path."""
    with (resources.files("omnisolver.random") / "random.yml").open("rb") as specs_file:
        specification = safe_load(specs_file)
    return plugin_from_specification(specification)
