from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.tools.distribution import Distribution

import numpy as np


test_model = Model()
test_model.constants = {
    'maximum_bit_rate': 100,  # system burst rate (maximum bit rate), in Gbit/s
    'average_bit_rate': 80,  # system average bit rate, in Gbit/s
}


def test_poisson_minimum_interarrival():
    min_interarrival_expected = np.full(10, 120)
    min_interarrival_calculated = np.full(10, np.inf)
    for i in range(10):
        distribution = Distribution(seed=i, model=test_model)
        interarrival = [distribution.poisson() for i in range(100000)]
        min_interarrival_calculated[i] = np.min(interarrival)
    np.testing.assert_array_less(min_interarrival_expected, min_interarrival_calculated)


def test_pareto_minimum_interarrival():
    min_interarrival_expected = np.full(10, 120)
    min_interarrival_calculated = np.full(10, np.inf)
    for i in range(10):
        distribution = Distribution(seed=i, model=test_model)
        interarrival = [distribution.pareto() for i in range(100000)]
        min_interarrival_calculated[i] = np.min(interarrival)
    np.testing.assert_array_less(min_interarrival_expected, min_interarrival_calculated)


def test_poisson_average_interarrival():
    average_interarrival_expected = np.full(3, 150)
    average_interarrival_calculated = np.zeros(3)
    for i in range(3):
        distribution = Distribution(seed=i, model=test_model)
        interarrival = [distribution.poisson() for i in range(100000)]
        average_interarrival_calculated[i] = np.average(interarrival)
    np.testing.assert_array_almost_equal(average_interarrival_calculated, average_interarrival_expected, decimal=0)


def test_pareto_average_interarrival():
    average_interarrival_expected = np.full(3, 150)
    average_interarrival_calculated = np.zeros(3)
    for i in range(3):
        distribution = Distribution(seed=i, model=test_model)
        interarrival = [distribution.pareto() for i in range(100000)]
        average_interarrival_calculated[i] = np.average(interarrival)
    np.testing.assert_array_almost_equal(average_interarrival_calculated, average_interarrival_expected, decimal=0)
