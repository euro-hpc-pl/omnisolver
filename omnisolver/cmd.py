"""Command line interface for omnisolver."""
import argparse
from typing import Dict

import pluggy

import omnisolver.plugin
from omnisolver.serialization import bqm_from_coo


def get_plugin_manager() -> pluggy.PluginManager:
    """Construct plugin manager aware of all defined plugins for omnisolver."""
    manager = pluggy.PluginManager("omnisolver")
    manager.add_hookspecs(omnisolver.plugin)
    manager.load_setuptools_entrypoints("omnisolver")
    return manager


def get_all_plugins(plugin_manager: pluggy.PluginManager) -> Dict[str, omnisolver.plugin.Plugin]:
    """Get all plugins defined for omnisolver."""
    return {plugin.name: plugin for plugin in plugin_manager.hook.get_plugin()}


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

    all_plugins = get_all_plugins(get_plugin_manager())

    for plugin in all_plugins.values():
        sub_parser = solver_commands.add_parser(
            plugin.name, parents=[common_parser], add_help=False, description=plugin.description
        )
        plugin.populate_parser(sub_parser)

    args = root_parser.parse_args(argv)

    chosen_plugin = all_plugins[args.solver]
    sampler = chosen_plugin.create_sampler(
        **omnisolver.plugin.filter_namespace_by_iterable(args, chosen_plugin.init_args)
    )

    bqm = bqm_from_coo(args.input, vartype=args.vartype)

    result = sampler.sample(
        bqm, **omnisolver.plugin.filter_namespace_by_iterable(args, chosen_plugin.sample_args)
    )

    result.to_pandas_dataframe().to_csv(args.output, index=False)
