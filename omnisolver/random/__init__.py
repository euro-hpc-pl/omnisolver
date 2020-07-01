"""Package with purely random reference sampler.

This also serves as a reference implementation of omnisolver plugins.
"""
from typing import Tuple

from omnisolver.plugin.hookspecs import simple_sampler


@simple_sampler
def get_specification_resource() -> Tuple[str, str]:
    """Get package name and resource path."""
    return "omnisolver.random", "random.yml"
