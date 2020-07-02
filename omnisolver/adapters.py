"""Definition of adapter protocols and other things common to all adapters."""
import argparse
import importlib
import dimod
from typing_extensions import Protocol

from omnisolver.serialization import bqm_from_coo


class Adapter(Protocol):
    def __init__(self) -> None:
        pass

    def is_available(self) -> bool:
        pass

    def create_sampler(self, cmd_args) -> dimod.Sampler:
        pass

    def sample(self, sampler: dimod.Sampler, cmd_args) -> dimod.SampleSet:
        pass

    def add_argparse_subparser(
        self, root_group: argparse._SubParsersAction, parent: argparse.ArgumentParser
    ):
        pass


class SimpleAdapter(Adapter):

    type_mapping = {"bool": bool, "int": int, "float": float, "str": str}

    def __init__(self, specification) -> None:
        super().__init__()
        if specification["schema_version"] != 1:
            raise ValueError("Unknown version of specification file.")
        self.sample_args_spec = specification["sample_args"]
        self.init_args_spec = specification["init_args"]
        self.module_path, self.class_name = specification["sampler_class"].rsplit(".", 1)
        self.parser_name = specification["parser_name"]
        self.description = specification["description"]

    def load_sampler_module(self):
        return importlib.import_module(self.module_path)

    def is_available(self) -> bool:
        try:
            self.load_sampler_module()
            return True
        except ImportError as e:
            print("{} is not available because: {}".format(self.parser_name, e))
            return False

    def create_sampler(self, cmd_args) -> dimod.Sampler:
        module = self.load_sampler_module()
        kwargs = {
            arg_spec["name"]: getattr(cmd_args, arg_spec["name"])
            for arg_spec in self.init_args_spec
        }
        return getattr(module, self.class_name)(**kwargs)

    def add_argparse_subparser(
        self, root_group: argparse._SubParsersAction, parent: argparse.ArgumentParser
    ):
        parser = root_group.add_parser(self.parser_name, parents=[parent], add_help=False)

        for arg_spec in self.sample_args_spec:
            self._add_argument(parser, arg_spec)

        for arg_spec in self.init_args_spec:
            self._add_argument(parser, arg_spec)

        parser.set_defaults(sample=self.sample)

    def _add_argument(self, parser, arg_spec):
        if "action" in arg_spec:
            parser.add_argument(
                f"--{arg_spec['name']}", help=arg_spec["help"], action=arg_spec["action"]
            )
        elif "default" in arg_spec:
            parser.add_argument(
                f"--{arg_spec['name']}",
                help=arg_spec["help"],
                type=self.type_mapping[arg_spec["type"]],
                default=arg_spec["default"],
            )
        else:
            raise NotImplemented("Argument spec must contain one of 'default' or 'action'")

    def sample(self, cmd_args) -> dimod.SampleSet:
        sampler = self.create_sampler(cmd_args)
        kwargs = {
            arg_spec["name"]: getattr(cmd_args, arg_spec["name"])
            for arg_spec in self.sample_args_spec
        }

        bqm = bqm_from_coo(cmd_args.input, vartype=cmd_args.vartype)
        return sampler.sample(bqm, **kwargs)
