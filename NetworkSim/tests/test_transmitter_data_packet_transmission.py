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


def test_bidirectional_tunable_transmitter_data_transmission():
    simulator = BaseSimulator(
        until=2000,
        transmitter_type='t',
        receiver_type='f',
        bidirectional=True
    )
    simulator.initialise()
    simulator.run()

    def is_upstream(simulator, source_id, destination_id):
        _difference = destination_id - source_id
        if _difference < 0:
            _difference += simulator.model.network.num_nodes
        if _difference <= simulator.model.network.num_nodes / 2:
            return False
        else:
            return True

    for i in range(simulator.model.network.num_nodes):
        upstream_transmitted_packet = simulator.upstream_transmitter[i].transmitted_data_packet
        downstream_transmitted_packet = simulator.downstream_transmitter[i].transmitted_data_packet
        generated_packet = simulator.RAM[i].generated_data_packet
        upstream_counter = 0
        downstream_counter = 0
        for j in range(len(generated_packet)):
            if is_upstream(simulator, i, generated_packet[j][3]) and \
                    upstream_counter < len(upstream_transmitted_packet):
                np.testing.assert_array_equal(
                    upstream_transmitted_packet[upstream_counter][1:],
                    generated_packet[j][2:]
                )
                upstream_counter += 1
            elif not is_upstream(simulator, i, generated_packet[j][3]) and \
                    downstream_counter < len(downstream_transmitted_packet):
                np.testing.assert_array_equal(
                    downstream_transmitted_packet[downstream_counter][1:],
                    generated_packet[j][2:]
                )
                downstream_counter += 1
