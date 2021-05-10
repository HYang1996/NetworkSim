import numpy as np

from NetworkSim.simulation.simulator.base import BaseSimulator


def test_FT_TR_reception():
    until = 1000
    multiple = 5
    simulator = BaseSimulator(
        until=until,
        transmitter_type='f',
        receiver_type='t'
    )
    simulator.initialise()
    # Let receiver run for longer simulation time
    for receiver in simulator.receiver:
        receiver.until = multiple * until
    simulator.until = multiple * until
    simulator.run()
    # Check if all rings are empty
    np.testing.assert_equal(simulator.model.control_ring.packet_count, 0)
    for data_ring in simulator.model.data_rings:
        np.testing.assert_equal(data_ring.packet_count, 0)


def test_unidirectional_TT_FR_reception():
    until = 5000
    multiple = 2
    simulator = BaseSimulator(
        until=until,
        transmitter_type='t',
        receiver_type='f'
    )
    simulator.initialise()
    # Let receiver run for longer simulation time
    for receiver in simulator.receiver:
        receiver.until = multiple * until
    simulator.until = multiple * until
    simulator.run()
    # Check if all rings are empty
    np.testing.assert_equal(simulator.model.control_ring.packet_count, 0)
    for data_ring in simulator.model.data_rings:
        np.testing.assert_equal(data_ring.packet_count, 0)


def test_bidirectional_TT_FR_reception():
    until = 5000
    multiple = 2
    simulator = BaseSimulator(
        until=until,
        transmitter_type='t',
        receiver_type='f',
        bidirectional=True
    )
    simulator.initialise()
    # Let receiver run for longer simulation time
    for receiver in simulator.upstream_receiver:
        receiver.until = multiple * until
    for receiver in simulator.downstream_receiver:
        receiver.until = multiple * until
    simulator.until = multiple * until
    simulator.run()
    # Check if all rings are empty
    np.testing.assert_equal(simulator.model.control_ring.packet_count, 0)
    for data_ring in simulator.model.data_rings:
        np.testing.assert_equal(data_ring.packet_count, 0)
