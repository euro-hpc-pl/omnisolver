"""Test cases for omnisolver's plugin system."""
import argparse
import copy
import importlib

import pytest

from omnisolver.plugin import (
    filter_namespace_by_iterable,
    add_argument,
    import_object,
    plugin_from_specification,
)

# pylint: disable=C0115,C0116,R0201,C0103


def test_filtering_namespace_by_iterable_extracts_only_attributes_with_names_from_that_iterable():
    namespace = argparse.Namespace(data="some-data", method="BFGS", name="my-solver")
    attribute_filter = ["data", "method"]
    expected_dict = {"data": "some-data", "method": "BFGS"}
    assert filter_namespace_by_iterable(namespace, attribute_filter) == expected_dict


@pytest.mark.parametrize(
    "specification, expected_name, expected_kwargs",
    [
        (
            {
                "name": "prob",
                "help": "probability of choosing 1 (default 0.5)",
                "type": "float",
                "default": 0.5,
            },
            "--prob",
            {"help": "probability of choosing 1 (default 0.5)", "type": float, "default": 0.5},
        ),
        (
            {"name": "num_reads", "help": "number of samples to draw", "type": "int", "default": 1},
            "--num_reads",
            {"help": "number of samples to draw", "type": int, "default": 1},
        ),
        (
            {
                "name": "some_flag",
                "help": "sets some flag",
                "action": "store_true",
            },
            "--some_flag",
            {
                "help": "sets some flag",
                "action": "store_true",
            },
        ),
    ],
)
def test_adding_argument_from_specification_to_parser_populates_all_fields_present_in_spec(
    specification, expected_name, expected_kwargs, mocker
):
    parser = mocker.create_autospec(argparse.ArgumentParser)
    add_argument(parser, specification)

    parser.add_argument.assert_called_once_with(expected_name, **expected_kwargs)


def test_when_importing_object_by_dotted_path_loader_is_called_with_modules_path(mocker):
    loader = mocker.create_autospec(importlib.import_module)

    import_object("omnisolver.pkg.my_sampler.CustomSampler", loader)

    loader.assert_called_once_with("omnisolver.pkg.my_sampler")


def test_when_importing_object_by_dotted_path_the_object_is_retrieved_from_imported_module(mocker):
    loader = mocker.create_autospec(importlib.import_module)
    loader.return_value.CustomSampler = type("CustomSampler", tuple(), {})

    result = import_object("omnisolver.pkg.my_sampler.CustomSampler", loader)

    assert result == loader.return_value.CustomSampler


class TestCreatingPluginFromSchema:

    CORRECT_SPECIFICATION = {
        "schema_version": 1,
        "name": "random",
        "sampler_class": "omnisolver.random.sampler.RandomSampler",
        "description": "A purely random solver",
        "init_args": [
            {
                "name": "prob",
                "help": "probability of choosing 1 (default 0.5)",
                "type": "float",
                "default": 0.5,
            }
        ],
        "sample_args": [
            {"name": "num_reads", "help": "number of samples to draw", "type": "int", "default": 1},
        ],
    }

    def test_raises_if_schema_version_is_different_than_1(self):
        specification = copy.deepcopy(self.CORRECT_SPECIFICATION)
        specification["schema_version"] = 2

        with pytest.raises(ValueError) as error_info:
            plugin_from_specification(specification)

        assert str(error_info.value) == "Unknown schema version: 2"

    def test_gives_plugin_with_solver_factory_equal_to_solver_class_from_specification(
        self, mocker
    ):
        loader = mocker.create_autospec(importlib.import_module)
        plugin = plugin_from_specification(self.CORRECT_SPECIFICATION, loader=loader)

        loader.assert_called_once_with("omnisolver.random.sampler")
        assert plugin.create_sampler == loader.return_value.RandomSampler

    def test_gives_plugin_with_name_taken_from_specification(self, mocker):
        loader = mocker.create_autospec(importlib.import_module)
        plugin = plugin_from_specification(self.CORRECT_SPECIFICATION, loader=loader)

        assert plugin.name == "random"

    def test_gives_plugin_with_populate_parser_that_adds_all_arguments_from_specification(
        self, mocker
    ):
        loader = mocker.create_autospec(importlib.import_module)
        parser = mocker.create_autospec(argparse.ArgumentParser)
        plugin = plugin_from_specification(self.CORRECT_SPECIFICATION, loader=loader)

        plugin.populate_parser(parser)

        parser.add_argument.assert_has_calls(
            [
                mocker.call(
                    "--prob",
                    help="probability of choosing 1 (default 0.5)",
                    type=float,
                    default=0.5,
                ),
                mocker.call("--num_reads", help="number of samples to draw", type=int, default=1),
            ],
            any_order=False,
        )

    def test_gives_plugin_with_init_args_set_to_all_names_present_in_specification_init_args(
        self, mocker
    ):
        loader = mocker.create_autospec(importlib.import_module)
        plugin = plugin_from_specification(self.CORRECT_SPECIFICATION, loader=loader)

        assert plugin.init_args == ["prob"]

    def test_gives_plugin_with_sample_args_set_to_all_names_present_in_specification_sample_args(
            self, mocker
    ):
        loader = mocker.create_autospec(importlib.import_module)
        plugin = plugin_from_specification(self.CORRECT_SPECIFICATION, loader=loader)

        assert plugin.sample_args == ["num_reads"]
