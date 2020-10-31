"""Hook specifications for omnisolver."""
import argparse
import inspect
from typing import Tuple, NamedTuple, Callable, Dict, Any
import dimod
import pluggy

sampler_spec = pluggy.HookspecMarker("omnisolver")


@sampler_spec
def get_specification_resource() -> Tuple[str, str]:
    """Return package and resource name for solver's specification."""


def filter_namespace_by_signature(
    namespace: argparse.Namespace,
    signature: inspect.Signature
) -> Dict[str, Any]:
    """Filter namespace, leaving only attribute corresponding to parameters of some callable.

    :param namespace: namespace to be filtered.
    :param signature: signature of the function.

    :returns: a dictionary mapping attribute names of namespace to their values such that given key
    exists in this dictionary if and only if there exists parameter in signature of the same name.
    """
    return {key: value for key, value in vars(namespace).items() if key in signature.parameters}


def call_func_with_args_from_namespace(func: Callable, namespace: argparse.Namespace):
    """Call a function, supplying arguments from a namespace.

    Arguments taken from namespace are filtered in such a way that only named parameters
    of the function are passed (even if it is variadic, so it won't receive **kwargs).

    :param func: function to be called.
    :param namespace: namespace from which arguments should be taken.

    :returns: result obtained by calling funct. Equivalent to func(**vars(namespace))
     modulo the filtering described above.
     """
    return func(**filter_namespace_by_signature(namespace, inspect.signature(func)))
