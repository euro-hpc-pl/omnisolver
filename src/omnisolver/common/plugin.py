"""Plugin specifications for omnisolver."""
import copy
import importlib
from argparse import ArgumentParser, Namespace
from typing import Any, Callable, Iterable, NamedTuple, TypeVar

import dimod

T = TypeVar("T")


class Plugin(NamedTuple):
    """Namedtuple storing all information needed from plugin.

    Attributes:
        name: Name of the plugin. This attribute is used internally for plugin identification,
            as well as a name of the solver in CLI.
        description: Description of the plugin, displayed in CLI's help message.
        create_sampler: Callable used to create sampler. It is assumed that the callable
            accepts exactly the arguments listed in ``init_args`. The returned samplers'
            `sample` method should accept the BQM object, as well as additional arguments
            listed in `sample_args`.
        populate_parser: Callable used to populate the argument sampler.
        init_args: Iterable of argument names used for initializing sampler defined
            by this plugin.
        sample_args: Iterable of argument names used for calling `sample` method of
            the sampler defined by this plugin. This iterable cannot contain the
            default `bqm` argument (which should be always present in sample method)
    """

    name: str
    description: str
    create_sampler: Callable[..., dimod.Sampler]
    populate_parser: Callable[[ArgumentParser], None]
    init_args: Iterable[str]
    sample_args: Iterable[str]


def plugin_from_specification(specification, loader=importlib.import_module) -> Plugin:
    """Create Plugin constructed from given specification.

    Args:
        specification: Dictionary specifying properties of the solver.
            For reference, see random.yml in ``omnisolver.random package``.
        loader: Function used for loading modules. Usually no need to override this.

    Returns:
        An instance of Plugin with the following properties:

            - `plugin.name` is taken from "name" in specification.
            - `create_solver` of a class pointed to by `specification["sampler_class"]``.
            - `populate_parser` acts in such a way, that it adds to the target parser all arguments
              present in `specification["args"]`.
    """
    schema_version = specification["schema_version"]
    if schema_version != 1:
        raise ValueError("Unknown schema version: 2")

    def _populate_parser(parser: ArgumentParser) -> None:
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


def filter_namespace_by_iterable(
    namespace: Namespace, attribute_filter: Iterable[str]
) -> dict[str, Any]:
    """Filter namespace, leaving only attribute present in given filter.

    Args:
        namespace: Namespace to be filtered.
        attribute_filter: Iterable of attribute names to be used as a filter.

    Returns:
        Dictionary containing mapping attribute name -> attribute value for every
            attribute of a signature such that its name is in attribute_filter.
    """
    return {
        key: value for key, value in vars(namespace).items() if key in attribute_filter
    }


TYPE_MAP = {"str": str, "int": int, "float": float}


def add_argument(parser: ArgumentParser, specification: dict[str, Any]) -> None:
    """Given specification of the argument, add it to parser.

    Args:
        parser: Parser to be moddified.
        specification: Argument specification. Should at the very least contain
            `"name"` and `"type"` keys, but can also contain any keys accepted
            as kwargs by `parser.add_argument`.
    """
    specification = copy.deepcopy(specification)
    arg_name = f"--{specification.pop('name')}"
    if "type" in specification:
        specification["type"] = TYPE_MAP.get(
            specification["type"], specification["type"]
        )
    parser.add_argument(arg_name, **specification)


def import_object(dotted_path: str, loader=importlib.import_module) -> Any:
    """Imports object specified by its full dotted_path.

    Args:
        dotted_path: Full path of the object, e.g. `"omnisolver.random.sampler.RandomSampler"`.
        loader: Function used to load module from the given path.
            Usually you don't need to specify that, this is here for testability purposes.

    Returns:
        Whatever the `dotted_path` points to.
    """
    module_path, obj_name = dotted_path.rsplit(".", 1)
    module = loader(module_path)
    return getattr(module, obj_name)
