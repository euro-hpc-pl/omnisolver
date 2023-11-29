"""Simple implementation of dummy random sampler."""
import random
from functools import partial
from typing import Dict, Hashable, cast

from dimod import BQM, Sampler, SampleSet, vartypes  # type: ignore


class RandomSampler(Sampler):
    """Implementation of simple random-sampler.

    This sampler assigns randomly chosen value to each variable, either from
    the set {0, 1} or the set {-1, 1}, depending on the vartype of BQM
    being solved.
    """

    variable_samplers = {
        vartypes.SPIN: lambda prob: int(random.random() > prob) * 2 - 1,
        vartypes.BINARY: lambda prob: int(random.random() > prob),
    }

    def __init__(self, prob: float) -> None:
        self.prob = prob

    def get_random_sample(self, bqm: BQM) -> Dict[Hashable, int]:
        """Get random assignment of variables in given BQM."""
        get_random_value = partial(self.variable_samplers[bqm.vartype], prob=self.prob)
        return {variable: get_random_value() for variable in bqm.variables}

    def sample(self, bqm: BQM, num_reads=1, **parameters) -> SampleSet:
        samples = [self.get_random_sample(bqm) for _ in range(num_reads)]
        energies = [bqm.energy(sample) for sample in samples]

        return cast(
            SampleSet,
            SampleSet.from_samples(samples, energy=energies, vartype=bqm.vartype),
        )

    @property
    def properties(self):
        return {"prob": self.prob}

    @property
    def parameters(self):
        return {"num_reads": []}
