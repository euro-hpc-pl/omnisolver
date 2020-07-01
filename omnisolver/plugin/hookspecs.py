"""Hook specifications for omnisolver."""
from typing import Tuple
import pluggy

simple_sampler = pluggy.HookspecMarker("omnisolver-simple")]

@simple_sampler
def get_specification_resource() -> Tuple[str, str]:
    """Return package and resource name for solver's specification."""
