"""Tools for serializing and deserializing BQms."""
from os import PathLike
from typing import TextIO, Union

import pandas as pd
from dimod import BQM


def bqm_from_coo(coo: Union[PathLike, TextIO], vartype="BINARY") -> BQM:
    """Read bqm from coordinate format.

    This is intended as a replacement for dimod.serialization.coo.load,
    which sometimes handles integral coefficients poorly.
    """
    data_frame = pd.read_csv(coo, names=["i", "j", "coefficient"], sep=" ")
    quadratic = {}
    linear = {}

    for i, j, coefficient in data_frame.itertuples(index=False):
        if i == j:
            linear[i] = coefficient
        else:
            quadratic[(i, j)] = coefficient
    return BQM(linear, quadratic, vartype=vartype)
