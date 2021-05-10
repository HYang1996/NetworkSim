__author__ = ['Hongyi Yang']
__all__ = [
    'generate_testvector'
]

import os


def generate_testvector(
    simulator,
    receiver_id=1,
    id_width=7,
    address_width=8,
    data_width=128,
    output_dir=None
):
    """
    Generate testvector files for receiver module.

    The underlying clock cycle is 1 ns and testvectors are generated for every clock cycle. \
        The end time is the `until` value of the simulator.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used for the simulation.
    receiver_id : int, optional
        The ID of the receiver of interest, by default 1.
    address_width : int, optional
        The bit width of the receiver RAM address, by default 8.
    data_width : int, optional
        The bit width of data signal, by default 128.
    output_dir : str, optional
        Output directory for the testvectors, by default None \
            (the `testvectors` directory under Digital-Design).

    Returns
    -------
    data_in, ram_assert : list
        Two lists containing input data signal and RAM content to be checked against.
    """
    # Mapping SystemVerilog ID to NetworkSim ID
    mapped_receiver_id = receiver_id - 1
    file_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(file_dir, '../../../Digital-Design/SystemVerilog-Project/testvectors')
    data_in_filename = os.path.join(output_dir, 'receiver_data_in.tv')
    ram_assert_filename = os.path.join(output_dir, 'receiver_ram_assert.tv')
    time_counter = 0
    ram_address = 0
    first_packet = True
    data_in = []
    ram_assert = []
    data = str(bin(0)[2:].zfill(data_width))
    last_packet_time = simulator.receiver[mapped_receiver_id].received_data_packet[-1][0]
    # Generate test vector content
    for data_packet in simulator.receiver[mapped_receiver_id].received_data_packet:
        # Time period with no data
        while time_counter < data_packet[0]:
            data_in.append([time_counter, str(bin(0)[2:].zfill(data_width))])
            ram_assert.append([ram_address, data])
            time_counter += 1
        # Clock cycle with receiver ID
        if time_counter == data_packet[0]:
            mapped_source_id = data_packet[2] + 1
            packet_content = str(bin(receiver_id)[2:].zfill(data_width))
            packet_content = str(bin(mapped_source_id)[2:].zfill(id_width)) + packet_content[id_width:]
            data_in.append([time_counter, packet_content])
            ram_assert.append([ram_address, data])
            time_counter += 1
        # Time period with data
        if first_packet:
            first_packet = False
        else:
            ram_address += 1
        packet_length = len(data_packet[1])
        num_clock_cycle = -(-packet_length // data_width)
        bit_counter = 0
        for i in range(num_clock_cycle):
            if i == num_clock_cycle - 1:
                data = data_packet[1][bit_counter:].ljust(data_width, '0')
            else:
                data = data_packet[1][bit_counter:bit_counter + data_width]
            data_in.append([time_counter, data])
            ram_assert.append([ram_address, data])
            bit_counter += data_width
            time_counter += 1
            if i < num_clock_cycle - 1:
                ram_address += 1
                if ram_address == 2**address_width:
                    ram_address = 0
        # Time period with no data after all packets
        if time_counter > last_packet_time:
            while time_counter < simulator.until:
                data_in.append([time_counter, str(bin(0)[2:].zfill(data_width))])
                ram_assert.append([ram_address, data])
                time_counter += 1
    # Write to test vector files
    with open(data_in_filename, 'w') as f_data_in:
        for i in range(len(data_in)):
            print(data_in[i][1], file=f_data_in)
    with open(ram_assert_filename, 'w') as f_ram_assert:
        for i in range(len(ram_assert)):
            print(
                str(bin(ram_assert[i][0])[2:].zfill(address_width)) + '_' + ram_assert[i][1],
                file=f_ram_assert
            )
    return data_in, ram_assert
