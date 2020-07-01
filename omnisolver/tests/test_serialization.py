"""Test cases for omnisolver.serialization."""
from textwrap import dedent
from typing import Any, Dict
from dimod import vartypes
import pytest
from io import StringIO
from omnisolver.serialization import bqm_from_coo


def make_coo(string):
    return StringIO(dedent(string).strip("\n"))


def sorted_quadratic(quadratic: Dict[Any, float]):
    return {tuple(sorted(k)): v for k, v in quadratic.items()}


@pytest.mark.parametrize("vartype", ["SPIN", "BINARY"])
def test_sets_correct_vartype(vartype):
    """BQM loaded from coo should have correct vartype."""
    coo = make_coo(
        """0 1 2.5
        1 1 -3
        2 0 4
        4 3 -1.2
        0 3 0.1123456
        """
    )
    bqm = bqm_from_coo(coo, vartype=vartype)
    assert bqm.vartype == vartypes.as_vartype(vartype)


@pytest.mark.parametrize("vartype", ["SPIN", "BINARY"])
def test_sets_correct_coefficients(vartype):
    """BQM loaded from coo should have correct coefficients"""
    coo = make_coo(
        """
        0 1 2.5
        1 1 -3
        0 2 4
        3 4 -1.2
        3 3 0.03125
        """
    )
    bqm = bqm_from_coo(coo, vartype=vartype)
    assert bqm.linear == {1: -3, 3: 0.03125, 0: 0, 2: 0, 4: 0}
    assert sorted_quadratic(bqm.quadratic) == {(0, 2): 4, (3, 4): -1.2, (0, 1): 2.5}
