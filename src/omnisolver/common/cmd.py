"""Command line interface for omnisolver."""
import argparse
import sys
from typing import Optional

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points  # pragma: no cover
else:
    from importlib.metadata import entry_points

from omnisolver.common.plugin import Plugin, filter_namespace_by_iterable
from omnisolver.common.serialization import bqm_from_coo


def get_all_plugins() -> dict[str, Plugin]:
    """Get all plugins defined for Omnisolver.


    Returns:
        A dictionary mapping plugin name to its definition.
    """
    return {
        (plugin := entry_point.load().get_plugin()).name: plugin
        for entry_point in entry_points(group="omnisolver")
    }


def main(argv: Optional[list[str]] = None) -> None:
    """Entrypoint of omnisolver.

    The entrypoint enumerates all plugins, dynamically creates the CLI and then appropriately
    dispatches execution to the plugin selected by the user.
    """
    root_parser = argparse.ArgumentParser()
    common_parser = argparse.ArgumentParser()
    common_parser.add_argument(
        "input",
        help="Path of the input BQM file in COO format. If not specified, stdin is used.",
        type=argparse.FileType("r"),
        default="-",
    )
    common_parser.add_argument(
        "--output",
        help="Path of the output file. If not specified, stdout is used.",
        type=argparse.FileType("w"),
        default="-",
    )
    common_parser.add_argument(
        "--vartype", help="Variable type", choices=["SPIN", "BINARY"], default="BINARY"
    )

    solver_commands = root_parser.add_subparsers(
        title="Solvers", dest="solver", required=True
    )

    all_plugins = get_all_plugins()

    for plugin in all_plugins.values():
        sub_parser = solver_commands.add_parser(
            plugin.name,
            parents=[common_parser],
            add_help=False,
            description=plugin.description,
        )
        plugin.populate_parser(sub_parser)

    args = root_parser.parse_args(argv)

    chosen_plugin = all_plugins[args.solver]
    sampler = chosen_plugin.create_sampler(
        **filter_namespace_by_iterable(args, chosen_plugin.init_args)
    )

    bqm = bqm_from_coo(args.input, vartype=args.vartype)

    result = sampler.sample(
        bqm,
        **filter_namespace_by_iterable(args, chosen_plugin.sample_args),
    )

    result.to_pandas_dataframe().to_csv(args.output, index=False)
