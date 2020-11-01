"""Command line interface for omnisolver."""
import argparse
from typing import Dict
import pluggy
import omnisolver.plugin
from omnisolver.serialization import bqm_from_coo


def get_plugin_manager() -> pluggy.PluginManager:
    """Construct plugin manager aware of all defined plugins for omnisolver."""
    pm = pluggy.PluginManager("omnisolver")
    pm.add_hookspecs(omnisolver.plugin)
    pm.load_setuptools_entrypoints("omnisolver")
    return pm


def get_all_plugins(plugin_manager: pluggy.PluginManager) -> Dict[str, omnisolver.plugin.Plugin]:
    """Get all plugins defined for omnisolver."""
    return {plugin.name: plugin for plugin in plugin_manager.hook.get_plugin()}


def main():
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

    solver_commands = root_parser.add_subparsers(title="Solvers", dest="solver")

    all_plugins = get_all_plugins(get_plugin_manager())

    for plugin in all_plugins.values():
        sub_parser = solver_commands.add_parser(plugin.name, parents=[common_parser], add_help=False)
        plugin.populate_parser(sub_parser)

    args = root_parser.parse_args()

    chosen_plugin = all_plugins[args.solver]
    sampler = omnisolver.plugin.call_func_with_args_from_namespace(
        chosen_plugin.create_solver, args
    )

    args.bqm = bqm_from_coo(args.input, vartype=args.vartype)

    result = omnisolver.plugin.call_func_with_args_from_namespace(sampler.sample, args)
    result.to_pandas_dataframe().to_csv(args.output)


if __name__ == "__main__":
    main()
