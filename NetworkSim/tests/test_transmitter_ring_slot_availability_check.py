import numpy as np

from NetworkSim.simulation.simulator.base import BaseSimulator


def test_fixed_single_transmitter_without_reception():
    simulator = BaseSimulator(
        until=5000,
        transmitter_type='f',
        receiver_type='t'
    )
    simulator._initialise_ram(node_id=0)
    simulator._initialise_transmitter(node_id=0)
    simulator.run()
    num_control_packet_transmitted = len(simulator.transmitter[0].transmitted_control_packet)
    num_data_packet_transmitted = len(simulator.transmitter[0].transmitted_data_packet)
    np.testing.assert_equal(num_control_packet_transmitted, 4)
    np.testing.assert_equal(num_data_packet_transmitted, 4)
