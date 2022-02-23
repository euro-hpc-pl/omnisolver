import dimod
import pytest

from omnisolver.random import get_plugin
from omnisolver.random.sampler import RandomSampler


@pytest.fixture
def bqm():
    return dimod.BQM(
        {0: 0.5, 1: -0.25, 4: 2.0},
        {(0, 1): -1, (2, 3): 1.2, (1, 4): -1.0},
        vartype="BINARY",
    )


@pytest.mark.parametrize("num_reads", [1, 4, 10, 10000])
def test_random_sampler_produces_requested_number_of_samples(bqm, num_reads):
    sampler = RandomSampler(prob=0.5)

    result = sampler.sample(bqm, num_reads=num_reads)

    assert len(result) == num_reads


def test_random_sampler_has_num_reads_in_its_parameters():
    assert RandomSampler(prob=0.5).parameters == {"num_reads": []}


def test_random_sampler_stores_probability_used_for_sampling():
    assert RandomSampler(prob=0.1).properties["prob"] == 0.1


def test_random_sampler_can_be_instantiated_from_plugin():
    plugin = get_plugin()

    sampler = plugin.create_sampler(prob=0.3)

    assert isinstance(sampler, RandomSampler) and sampler.prob == 0.3
