"""Package with purely random reference sampler.

This also serves as a reference implementation of omnisolver plugins.
"""
from pkg_resources import resource_stream
from yaml import safe_load

from omnisolver.plugin import Plugin, plugin_from_specification, plugin_impl


@plugin_impl
def get_plugin() -> Plugin:
    """Get package name and resource path."""
    specification = safe_load(resource_stream("omnisolver.random", "random.yml"))
    return plugin_from_specification(specification)
