import numpy as np

from NetworkSim.simulation.simulator.base import BaseSimulator


def test_fixed_transmitter_data_transmission():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='f',
        receiver_type='t'
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        transmitted_packet = simulator.transmitter[i].transmitted_data_packet
        generated_packet = simulator.RAM[i].generated_data_packet
        for j in range(len(transmitted_packet)):
            np.testing.assert_array_equal(
                transmitted_packet[j][1:],
                generated_packet[j][2:]
            )


def test_tunable_transmitter_data_transmission():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='t',
        receiver_type='f'
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        transmitted_packet = simulator.transmitter[i].transmitted_data_packet
        generated_packet = simulator.RAM[i].generated_data_packet
        for j in range(len(transmitted_packet)):
            np.testing.assert_array_equal(
                transmitted_packet[j][1:],
                generated_packet[j][2:]
            )
