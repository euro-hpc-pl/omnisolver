"""Tools for serializing and deserializing BQms."""
from typing import Union, TextIO
from os import PathLike
from dimod import BQM
import pandas as pd


def bqm_from_coo(coo: Union[PathLike, TextIO], vartype="BINARY") -> BQM:
    """Read bqm from coordinate format.

    This is intended as a replacement for dimod.serialization.coo.load,
    which sometimes handles integral coefficients poorly.
    """
    df = pd.read_csv(coo, names=["i", "j", "coefficient"], sep=" ")
    quadratic = {}
    linear = {}
    print(df.values.tolist())
    for i, j, coefficient in df.itertuples(index=False):
        if i == j:
            linear[i] = coefficient
        else:
            quadratic[(i, j)] = coefficient
    return BQM(linear, quadratic, vartype=vartype)
