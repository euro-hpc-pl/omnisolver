"""Simple implementation of dummy random sampler."""
import random
from functools import partial

import dimod


class RandomSampler(dimod.Sampler):
    """Implementatoin of simple random-sampler."""

    variable_samplers = {
        dimod.vartypes.SPIN: lambda prob: int(random.random() > prob) * 2 - 1,
        dimod.vartypes.BINARY: lambda prob: int(random.random() > prob),
    }

    def __init__(self, prob):
        self.prob = prob

    def get_random_sample(self, bqm):
        """Get random assignment of variables in given BQM."""
        get_random_value = partial(self.variable_samplers[bqm.vartype], prob=self.prob)
        return {variable: get_random_value() for variable in bqm.variables}

    def sample(self, bqm, num_reads=1):
        samples = [self.get_random_sample(bqm) for _ in range(num_reads)]
        energies = [bqm.energy(sample) for sample in samples]

        return dimod.SampleSet.from_samples(samples, energy=energies, vartype=bqm.vartype)

    @property
    def properties(self):
        return dict()

    @property
    def parameters(self):
        return {"num_reads": []}
