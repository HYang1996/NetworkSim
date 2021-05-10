from NetworkSim.architecture.base.network import Network
from NetworkSim.architecture.setup.model import Model
from NetworkSim.architecture.base.ring import Ring
from NetworkSim.architecture.signal.control import ControlSignal
from NetworkSim.architecture.signal.data import DataSignal


# Set up test network, signals and model
network = Network(length=100,
                  num_nodes=100,
                  direction=1)
control_signal = ControlSignal(id_length=7,
                               control_length=2)
data_signal = DataSignal(size=1)
test_model = Model(network=network,
                   control_signal=control_signal,
                   data_signal=data_signal)
test_model.constants = {
    'speed': 1
}


def test_control_packet_location_on_ring():
    control_ring = Ring(model=test_model, time_unit='s')
    # Add control packets to ring at different timings
    test_nodes = [0, 50, 99]
    test_packets = ['000000000', '000000001', '000000011']
    test_time = [0, 5, 10]
    for i in range(3):
        control_ring.add_packet(node_id=test_nodes[i],
                                destination_id=-1,
                                packet=test_packets[i],
                                generation_timestamp=test_time[i],
                                transmission_timestamp=test_time[i])
    presence_expected = [True, True, True, True, True, True]
    packet_expected = [
        ['000000000', 0, 0, 0, 0, -1],
        ['000000001', 5, 5, 50, 50, -1],
        ['000000011', 10, 10, 99, 99, -1],
        ['000000000', 0, 0, 0, 0, -1],
        ['000000001', 5, 5, 50, 50, -1],
        ['000000011', 10, 10, 99, 99, -1]
    ]
    presence_test = [None] * 6
    packet_test = [None] * 6
    # Check packet
    check_time = [0, 5, 10, 50, 55, 60]
    check_nodes = [0, 50, 99, 50, 0, 49]
    for i in range(6):
        presence_test[i], packet_test[i] = \
            control_ring.check_packet(current_time=check_time[i],
                                      node_id=check_nodes[i])

    assert presence_test == presence_expected
    assert packet_test == packet_expected


def test_data_packet_location_on_ring():
    data_ring = Ring(model=test_model, time_unit='s')
    # Add control packets to ring at different timings
    test_nodes = [0, 50, 99]
    test_packets = ['00000000', '00001111', '11111111']
    test_time = [0, 20, 40]
    for i in range(3):
        data_ring.add_packet(node_id=test_nodes[i],
                             destination_id=-1,
                             packet=test_packets[i],
                             generation_timestamp=test_time[i],
                             transmission_timestamp=test_time[i])
    presence_expected = [True, True, True, True, True, True]
    packet_expected = [
        ['00000000', 0, 0, 0, 0, -1],
        ['00001111', 20, 20, 50, 50, -1],
        ['11111111', 40, 40, 99, 99, -1],
        ['00000000', 0, 0, 0, 0, -1],
        ['00001111', 20, 20, 50, 50, -1],
        ['11111111', 40, 40, 99, 99, -1]
    ]
    presence_test = [None] * 6
    packet_test = [None] * 6
    # Check packet
    check_time = [0, 20, 40, 100000, 200030, 3490]
    check_nodes = [0, 50, 99, 0, 60, 49]
    for i in range(6):
        presence_test[i], packet_test[i] = \
            data_ring.check_packet(current_time=check_time[i],
                                   node_id=check_nodes[i])

    assert presence_test == presence_expected
    assert packet_test == packet_expected


def test_data_packet_location_on_reversed_ring():
    num_test = 15
    data_ring = Ring(model=test_model, time_unit='s', reversed=True)
    # Add control packets to ring at different timings
    test_nodes = [0, 50, 99]
    test_packets = ['00000000', '00001111', '11111111']
    test_time = [0, 20, 40]
    for i in range(3):
        data_ring.add_packet(node_id=test_nodes[i],
                             destination_id=-1,
                             packet=test_packets[i],
                             generation_timestamp=test_time[i],
                             transmission_timestamp=test_time[i])
    presence_expected = [True] * num_test
    packet_expected = []
    for i in range(int(num_test / 3)):
        packet_expected.append(['00000000', 0, 0, 0, 0, -1])
        packet_expected.append(['00001111', 20, 20, 50, 50, -1])
        packet_expected.append(['11111111', 40, 40, 99, 99, -1])
    presence_test = [None] * num_test
    packet_test = [None] * num_test
    # Check packet
    check_time = [0, 20, 40, 1000, 1020, 1040, 101, 121, 141, 99, 119, 139, 100000, 200030, 3490]
    check_nodes = [0, 50, 99, 0, 50, 99, 99, 49, 98, 1, 51, 0, 0, 40, 49]
    for i in range(num_test):
        presence_test[i], packet_test[i] = \
            data_ring.check_packet(current_time=check_time[i],
                                   node_id=check_nodes[i])

    assert presence_test == presence_expected
    assert packet_test == packet_expected
