"""Hook specifications for omnisolver."""
import argparse
import copy
import importlib
from typing import Any, Callable, Dict, Iterable, NamedTuple, TypeVar

import dimod
import pluggy

T = TypeVar("T")

plugin_spec = pluggy.HookspecMarker("omnisolver")
plugin_impl = pluggy.HookimplMarker("omnisolver")


class Plugin(NamedTuple):
    """Namedtuple storing all information needed from plugin."""

    name: str
    description: str
    create_sampler: Callable[..., dimod.Sampler]
    populate_parser: Callable[[argparse.ArgumentParser], None]
    init_args: Iterable[str]
    sample_args: Iterable[str]


def plugin_from_specification(specification, loader=importlib.import_module) -> Plugin:
    """Create Plugin constructed from given specification.

    :param specification: dictionary specifying properties of the solver.
     For reference, see random.yml in omnisolver.random package.
    :param loader: function used for loading modules. Usually no need to override this.

    :returns: a instance of Plugin with the following properties:
     - plugin.name is taken from "name" in specification
     - create_solver of a class pointed to by specification["sampler_class"]
     - populate_parser acts in such a way, that it adds to the target parser all arguments
       present in specification["args"]
    """
    schema_version = specification["schema_version"]
    if schema_version != 1:
        raise ValueError("Unknown schema version: 2")

    def _populate_parser(parser: argparse.ArgumentParser) -> None:
        for arg in specification["init_args"]:
            add_argument(parser, arg)

        for arg in specification["sample_args"]:
            add_argument(parser, arg)

    return Plugin(
        name=specification["name"],
        description=specification["description"],
        create_sampler=import_object(specification["sampler_class"], loader),
        populate_parser=_populate_parser,
        init_args=[arg["name"] for arg in specification["init_args"]],
        sample_args=[arg["name"] for arg in specification["sample_args"]],
    )


@plugin_spec
def get_plugin() -> Plugin:
    """Hook for defining plugin instances."""


def filter_namespace_by_iterable(
    namespace: argparse.Namespace, attribute_filter: Iterable[str]
) -> Dict[str, Any]:
    """Filter namespace, leaving only attribute present in given filter.

    :param namespace: namespace to be filtered.
    :param attribute_filter: iterable of attribute names to be used as a filter.

    return dictionary containing mapping attribute name -> attribute value for every
     attribute of a signature such that its name is in attribute_filter.
    """
    return {key: value for key, value in vars(namespace).items() if key in attribute_filter}


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
