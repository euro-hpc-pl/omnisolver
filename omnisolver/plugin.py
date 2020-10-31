"""Hook specifications for omnisolver."""
from typing import Tuple
import pluggy

sampler_spec = pluggy.HookspecMarker("omnisolver")


@sampler_spec
def get_specification_resource() -> Tuple[str, str]:
    """Return package and resource name for solver's specification."""
