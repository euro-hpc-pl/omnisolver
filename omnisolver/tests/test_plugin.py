"""Test cases for omnisolver's plugin system."""
import argparse
import copy
import importlib
import inspect

import pytest

from omnisolver.plugin import (
    call_func_with_args_from_namespace,
    filter_namespace_by_signature,
    add_argument,
    import_object,
    plugin_from_specification,
)


def test_filtering_namespace_gives_intersection_of_signature_args_and_namespace_attributes():
    def function(data, method, precision):
        return data, method, precision

    signature = inspect.signature(function)
    namespace = argparse.Namespace(data="some-data", method="BFGS", name="my-solver")

    expected_dict = {"data": "some-data", "method": "BFGS"}
    assert filter_namespace_by_signature(namespace, signature) == expected_dict


class TestCallingFunctionWithArgsFromNamespace:
    def test_passes_all_arguments_defined_in_namespace(self, mocker):
        def _func(x, y, z=0.0):
            return x, y, z

        func = mocker.create_autospec(_func)

        call_func_with_args_from_namespace(func, argparse.Namespace(x=5.0, y=20))

        func.assert_called_once_with(x=5.0, y=20)

    def test_passes_through_return_value_of_called_function(self, mocker):
        def _solve(instance, n_args, beta):
            return instance, n_args, beta

        solve = mocker.create_autospec(_solve)

        return_value = call_func_with_args_from_namespace(
            solve, argparse.Namespace(instance=[(0, 1, 5.0), (2, 3, -1.5)], n_args=100, beta=1.0)
        )

        assert return_value == solve.return_value

    def test_succeeds_even_if_additional_arguments_are_present_in_namespace(self):
        def _func(x, y):
            return x, y

        call_func_with_args_from_namespace(_func, argparse.Namespace(x=1, y=2, z=3))


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
        "args": [
            {
                "name": "prob",
                "help": "probability of choosing 1 (default 0.5)",
                "type": "float",
                "default": 0.5,
            },
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
        assert plugin.create_solver == loader.return_value.RandomSampler

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
