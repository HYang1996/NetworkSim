import numpy as np

from NetworkSim.simulation.simulator.base import BaseSimulator


def test_fixed_transmitter_ram_queue_deque():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='f',
        receiver_type='t'
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        add_to_queue_record = simulator.transmitter[i].ram.add_to_queue_record
        pop_from_queue_record = simulator.transmitter[i].ram.pop_from_queue_record
        # pop_from_queue will always be equal or shorter than add_to_queue, if some data doesnt get transmitted
        for j in range(len(pop_from_queue_record)):
            np.testing.assert_array_equal(
                add_to_queue_record[j],
                pop_from_queue_record[j]
            )


def test_tunable_transmitter_ram_queue_deque():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='t',
        receiver_type='f'
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        add_to_queue_record = simulator.transmitter[i].ram.add_to_queue_record
        pop_from_queue_record = simulator.transmitter[i].ram.pop_from_queue_record
        # pop_from_queue will always be equal or shorter than add_to_queue, if some data doesnt get transmitted
        for j in range(len(pop_from_queue_record)):
            np.testing.assert_array_equal(
                add_to_queue_record[j],
                pop_from_queue_record[j]
            )
