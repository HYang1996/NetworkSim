import numpy as np

from NetworkSim.simulation.simulator.base import BaseSimulator


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def test_control_packet_transmission():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='f',
        receiver_type='t'
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        received_control_packet = simulator.receiver[i].received_control_packet
        for received_time, packet, source_id in received_control_packet:
            expected_transmit_time = received_time - simulator.model.network.get_distance(source_id, i) / \
                simulator.model.constants["speed"] * 1e9
            expected_transmit_time_rounded = np.round(expected_transmit_time, 3)
            # Go to the transmitter side and search for the packet
            expected_control_packet_in_transmitter = [expected_transmit_time_rounded, packet, i]
            assert expected_control_packet_in_transmitter in \
                simulator.transmitter[source_id].transmitted_control_packet


def test_data_packet_transmission_FTTR():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='f',
        receiver_type='t'
    )
    simulator.initialise()
    simulator.run()
    circulation_time = simulator.model.circulation_time
    possible_packet_in_transmitter = []
    for i in range(simulator.model.network.num_nodes):
        received_data_packet = simulator.receiver[i].received_data_packet
        for received_time, packet, source_id in received_data_packet:
            expected_transmit_time = received_time - simulator.model.network.get_distance(source_id, i) / \
                simulator.model.constants["speed"] * 1e9
            expected_transmit_time_rounded = np.round(expected_transmit_time, 3)
            # Go to the transmitter side and search for the packet
            while expected_transmit_time_rounded > 0:
                possible_packet_in_transmitter.append([expected_transmit_time_rounded, packet, i])
                expected_transmit_time_rounded -= circulation_time
            assert intersection(possible_packet_in_transmitter,
                                simulator.transmitter[source_id].transmitted_data_packet)


def test_data_packet_transmission_TTFR():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='t',
        receiver_type='f'
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        received_data_packet = simulator.receiver[i].received_data_packet
        for received_time, packet, source_id in received_data_packet:
            expected_transmit_time = received_time - simulator.model.network.get_distance(source_id, i) / \
                simulator.model.constants["speed"] * 1e9
            expected_transmit_time_rounded = np.round(expected_transmit_time, 3)
            # Go to the transmitter side and search for the packet
            expected_data_packet_in_transmitter = [expected_transmit_time_rounded, packet, i]
            assert expected_data_packet_in_transmitter in simulator.transmitter[source_id].transmitted_data_packet


def test_data_packet_transmission_bidirectional_TTFR():
    simulator = BaseSimulator(
        until=1000,
        transmitter_type='t',
        receiver_type='f',
        bidirectional=True
    )
    simulator.initialise()
    simulator.run()
    for i in range(simulator.model.network.num_nodes):
        received_data_packet = simulator.downstream_receiver[i].received_data_packet
        for received_time, packet, source_id in received_data_packet:
            expected_transmit_time = received_time - simulator.model.network.get_distance(source_id, i) / \
                simulator.model.constants["speed"] * 1e9
            expected_transmit_time_rounded = np.round(expected_transmit_time, 3)
            # Go to the transmitter side and search for the packet
            expected_data_packet_in_transmitter = [expected_transmit_time_rounded, packet, i]
            assert expected_data_packet_in_transmitter in \
                simulator.downstream_transmitter[source_id].transmitted_data_packet
        received_data_packet = simulator.upstream_receiver[i].received_data_packet
        for received_time, packet, source_id in received_data_packet:
            expected_transmit_time = received_time - (simulator.model.network.length -
                                                      simulator.model.network.get_distance(source_id, i)) / \
                simulator.model.constants["speed"] * 1e9
            expected_transmit_time_rounded = np.round(expected_transmit_time, 3)
            # Go to the transmitter side and search for the packet
            expected_data_packet_in_transmitter = [expected_transmit_time_rounded, packet, i]
            assert expected_data_packet_in_transmitter in \
                simulator.upstream_transmitter[source_id].transmitted_data_packet
