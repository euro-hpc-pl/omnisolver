"""Package with purely random reference sampler.

This also serves as a reference implementation of omnisolver plugins.
"""
from typing import Tuple

from omnisolver.plugin import sampler_spec_impl


@sampler_spec_impl
def get_specification_resource() -> Tuple[str, str]:
    """Get package name and resource path."""
    return "omnisolver.random", "random.yml"
