"""Hook specifications for omnisolver."""
from typing import Tuple
import pluggy

hook_spec = pluggy.HookspecMarker("omnisolver-simple")]

@hook_spec
def get_specification_resource() -> Tuple[str, str]:
    """Return package and resource name for solver's specification."""
