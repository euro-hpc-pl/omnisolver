"""Command line interface for omnisolver."""
import argparse
import sys
from typing import Dict

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

import omnisolver.common.plugin
from omnisolver.common.serialization import bqm_from_coo


def get_all_plugins() -> Dict[str, omnisolver.common.plugin.Plugin]:
    """Get all plugins defined for omnisolver."""
    return {
        (plugin := entry_point.load().get_plugin()).name: plugin
        for entry_point in entry_points(group="omnisolver")
    }


def main(argv=None):
    """Entrypoint of omnisolver."""
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

    solver_commands = root_parser.add_subparsers(title="Solvers", dest="solver", required=True)

    all_plugins = get_all_plugins()

    for plugin in all_plugins.values():
        sub_parser = solver_commands.add_parser(
            plugin.name, parents=[common_parser], add_help=False, description=plugin.description
        )
        plugin.populate_parser(sub_parser)

    args = root_parser.parse_args(argv)

    chosen_plugin = all_plugins[args.solver]
    sampler = chosen_plugin.create_sampler(
        **omnisolver.common.plugin.filter_namespace_by_iterable(args, chosen_plugin.init_args)
    )

    bqm = bqm_from_coo(args.input, vartype=args.vartype)

    result = sampler.sample(
        bqm,
        **omnisolver.common.plugin.filter_namespace_by_iterable(args, chosen_plugin.sample_args),
    )

    result.to_pandas_dataframe().to_csv(args.output, index=False)
