"""Test cases for omnisolver's plugin system."""
import argparse
import inspect
from omnisolver.plugin import call_func_with_args_from_namespace, filter_namespace_by_signature


def test_filtering_namespace_gives_intersection_of_signature_args_and_namespace_attributes():
    def function(data, method, precision):
        pass

    signature = inspect.signature(function)
    namespace = argparse.Namespace(data="some-data", method="BFGS", name="my-solver")

    expected_dict = {"data": "some-data", "method": "BFGS"}
    assert filter_namespace_by_signature(namespace, signature) == expected_dict


class TestCallingFunctionWithArgsFromNamespace:

    def test_passes_all_arguments_defined_in_namespace(self, mocker):

        def _func(x, y, z=0.0):
            pass

        func = mocker.create_autospec(_func)

        call_func_with_args_from_namespace(func, argparse.Namespace(x=5.0, y=20))

        func.assert_called_once_with(x=5.0, y=20)

    def test_passes_through_return_value_of_called_function(self, mocker):
        def _solve(instance, n_args, beta):
            pass

        solve = mocker.create_autospec(_solve)

        return_value = call_func_with_args_from_namespace(
            solve,
            argparse.Namespace(
                instance=[(0, 1, 5.0), (2, 3, -1.5)],
                n_args=100,
                beta=1.0
            )
        )

        assert return_value == solve.return_value

    def test_succeeds_even_if_additional_arguments_are_present_in_namespace(self):

        def _func(x, y):
            pass

        call_func_with_args_from_namespace(_func, argparse.Namespace(x=1, y=2, z=3))
