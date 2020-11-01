"""Hook specifications for omnisolver."""
import argparse
import copy
import importlib
import inspect
from typing import NamedTuple, Callable, Dict, Any, TypeVar
import dimod
import pluggy

T = TypeVar("T")

plugin = pluggy.HookspecMarker("omnisolver")


class Plugin(NamedTuple):
    name: str
    create_solver: Callable[..., dimod.Sampler]
    populate_parser: Callable[[argparse.ArgumentParser], None]


@plugin
def get_plugin() -> Plugin:
    """Hook for defining plugin instances."""


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


def call_func_with_args_from_namespace(func: Callable[..., T], namespace: argparse.Namespace) -> T:
    """Call a function, supplying arguments from a namespace.

    Arguments taken from namespace are filtered in such a way that only named parameters
    of the function are passed (even if it is variadic, so it won't receive **kwargs).

    :param func: function to be called.
    :param namespace: namespace from which arguments should be taken.

    :returns: result obtained by calling func. Equivalent to func(**vars(namespace))
     modulo the filtering described above.
     """
    return func(**filter_namespace_by_signature(namespace, inspect.signature(func)))


TYPE_MAP = {"str": str, "int": int, "float": float}

def add_argument(parser: argparse.ArgumentParser, specification: Dict[str, Any]):
    """Given specification of the argument, add it to parser."""
    specification = copy.deepcopy(specification)
    arg_name = f"--{specification.pop('name')}"
    if "type" in specification:
        specification["type"] = TYPE_MAP.get(specification["type"], specification["type"])
    parser.add_argument(arg_name, **specification)


def import_object(dotted_path: str, loader=importlib.import_module):
    """Imports object specified by its full dotted_path.

    :param dotted_path: full path of the object, e.g. omnisolver.random.sampler.RandomSampler.
    :param loader: function used to load module from the given path.
     Usually you don't need to specify that, this is here for testability purposes.
    :returns: whatever dotted path points to.
    """
    module_path, obj_name = dotted_path.rsplit(".", 1)
    module = loader(module_path)
    return getattr(module, obj_name)
