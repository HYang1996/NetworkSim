__author__ = ['Hongyi Yang']
__all__ = [
    'print_delay_lut',
    'generate_testvector'
]

import os

from NetworkSim.simulation.simulator.base import BaseSimulator


def print_delay_lut(simulator=None, upstream=False):
    """
    Print delay LUT

    Generate a default simulator and print transmitter delay LUT.

    0 - N IDs are mapped to 1 - (N + 1) IDs.
    """
    if simulator is None:
        simulator = BaseSimulator(bidirectional=True)
        simulator.initialise()
    if upstream:
        delay = simulator.upstream_transmitter[0].tuning_delay
    else:
        delay = simulator.downstream_transmitter[0].tuning_delay
    for i in range(100):
        for j in range(100):
            print(
                "14'b" + str(bin(i + 1)[2:].zfill(7)) + str(bin(j + 1)[2:].zfill(7)) + ":",
                "delay <= 8'b" + str(bin(int(delay[i, j]))[2:].zfill(8)) + ";",
                "// curr:", i + 1, "dest:", j + 1, "delay:", int(delay[i, j])
            )


def generate_testvector(
    simulator,
    transmitter_id=1,
    id_width=7,
    address_width=8,
    data_width=128,
    output_dir=None,
):
    """
    Testvector generation for transmitters.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used for testvector generation.
    transmitter_id : int, optional
        The ID of the transmitter of choice, by default ``1``
    address_width : int, optional
        The bit width of transmitter RAM address, by default ``8``
    data_width : int, optional
        The bit width of the transmitter RAM data, by default ``128``
    output_dir : str, optional
        Output directory for the testvectors, by default ``None`` \
            (the `testvectors` directory under Digital-Design).
    bidirectional : bool, optional
        If bi-directional transmission scheme is carried out. Default is ``False``.

    Returns
    -------
    ram_content_tv, data_out_tv : list
        Two lists (or four lists in the case of bi-directional transmission) \
            containing RAM content and output data signal to be checked against.
    """
    # Mapping SystemVerilog ID to NetworkSim ID
    mapped_transmitter_id = transmitter_id - 1
    file_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(file_dir, '../../../Digital-Design/SystemVerilog-Project/testvectors')
    if not simulator.bidirectional:
        ram_filename = os.path.join(output_dir, 'transmitter_ram.tv')
        data_out_assert_filename = os.path.join(output_dir, 'transmitter_data_out_assert.tv')
    else:
        cw_ram_filename = os.path.join(output_dir, 'transmitter_ram_cw.tv')
        cw_data_out_assert_filename = os.path.join(output_dir, 'transmitter_data_out_assert_cw.tv')
        acw_ram_filename = os.path.join(output_dir, 'transmitter_ram_acw.tv')
        acw_data_out_assert_filename = os.path.join(output_dir, 'transmitter_data_out_assert_acw.tv')

    def update_ram_address(ram_address):
        """
        Function to update RAM address during iterations.

        Parameters
        ----------
        ram_address : int
            The RAM address to be updated.

        Returns
        -------
        new_ram_address : int
            The updated RAM address.
        """
        if ram_address + 1 == 2 ** address_width:
            return 0
        else:
            return ram_address + 1

    def is_upstream(destination_id):
        """
        Check if the destination node is an upstream node.

        Parameters
        ----------
        destination_id : int
            ID of the destination node.

        Returns
        -------
        is_upstream : bool
            ``True`` if the destination is upstream, ``False`` if downstream.
        """
        _difference = destination_id - mapped_transmitter_id
        if _difference < 0:
            _difference += simulator.model.network.num_nodes
        if _difference <= simulator.model.network.num_nodes / 2:
            return False
        else:
            return True

    def generate_ram_tv():
        """
        Function to generate RAM content testvector input.

        Returns
        -------
        ram_content : list
            List of RAM content testvectors, including address and data.
        """
        time_counter = 0
        if simulator.bidirectional:
            cw_ram_address = 0
            acw_ram_address = 0
            cw_ram_content = []
            acw_ram_content = []
        else:
            ram_address = 0
            ram_content = []
        last_packet_time = simulator.RAM[mapped_transmitter_id].generated_data_packet[-1][0]
        for data_packet in simulator.RAM[mapped_transmitter_id].generated_data_packet:
            if simulator.bidirectional:
                if is_upstream(destination_id=data_packet[3]):
                    upstream = True
                else:
                    upstream = False
            # Time period with no data
            while time_counter < int(data_packet[0]):
                if simulator.bidirectional:
                    cw_content = [time_counter, cw_ram_address, str(bin(0)[2:].zfill(data_width))]
                    acw_content = [time_counter, acw_ram_address, str(bin(0)[2:].zfill(data_width))]
                    cw_ram_content.append(cw_content)
                    acw_ram_content.append(acw_content)
                else:
                    content = [time_counter, ram_address, str(bin(0)[2:].zfill(data_width))]
                    ram_content.append(content)
                time_counter += 1
            # Clock cycle with source and destination ID
            if time_counter == int(data_packet[0]):
                # Mapping NetworkSim ID to SystemVerilog ID
                mapped_destination_id = data_packet[3] + 1
                # Append destination ID
                packet_content = str(bin(mapped_destination_id)[2:].zfill(data_width))
                # Insert source ID
                packet_content = str(bin(transmitter_id)[2:].zfill(id_width)) + packet_content[id_width:]
                if simulator.bidirectional:
                    if upstream:
                        cw_content = content = [time_counter, cw_ram_address, str(bin(0)[2:].zfill(data_width))]
                        acw_content = [time_counter, acw_ram_address, packet_content]
                        acw_ram_address = update_ram_address(acw_ram_address)
                    else:
                        cw_content = [time_counter, cw_ram_address, packet_content]
                        acw_content = content = [time_counter, acw_ram_address, str(bin(0)[2:].zfill(data_width))]
                        cw_ram_address = update_ram_address(cw_ram_address)
                    cw_ram_content.append(cw_content)
                    acw_ram_content.append(acw_content)
                else:
                    content = [time_counter, ram_address, packet_content]
                    ram_content.append(content)
                    ram_address = update_ram_address(ram_address)
                time_counter += 1
            # Time period with data
            packet_length = len(data_packet[2])
            num_clock_cycle = -(-packet_length // data_width)
            bit_counter = 0
            for i in range(num_clock_cycle):
                if i == num_clock_cycle - 1:
                    data = data_packet[2][bit_counter:].ljust(data_width, '0')
                else:
                    data = data_packet[2][bit_counter:bit_counter + data_width]
                if simulator.bidirectional:
                    if upstream:
                        cw_content = [time_counter, cw_ram_address, str(bin(0)[2:].zfill(data_width))]
                        acw_content = [time_counter, acw_ram_address, data]
                        acw_ram_address = update_ram_address(acw_ram_address)
                    else:
                        cw_content = [time_counter, cw_ram_address, data]
                        acw_content = [time_counter, acw_ram_address, str(bin(0)[2:].zfill(data_width))]
                        cw_ram_address = update_ram_address(cw_ram_address)
                    cw_ram_content.append(cw_content)
                    acw_ram_content.append(acw_content)
                else:
                    content = [time_counter, ram_address, data]
                    ram_content.append(content)
                    ram_address = update_ram_address(ram_address)
                bit_counter += data_width
                time_counter += 1
            # Time period with no data after all packets
            if time_counter > last_packet_time:
                while time_counter < simulator.until:
                    if simulator.bidirectional:
                        cw_content = [time_counter, cw_ram_address, str(bin(0)[2:].zfill(data_width))]
                        acw_content = [time_counter, acw_ram_address, str(bin(0)[2:].zfill(data_width))]
                        cw_ram_content.append(cw_content)
                        acw_ram_content.append(acw_content)
                    else:
                        content = [time_counter, ram_address, str(bin(0)[2:].zfill(data_width))]
                        ram_content.append(content)
                    time_counter += 1
        if simulator.bidirectional:
            return cw_ram_content, acw_ram_content
        else:
            return ram_content

    def generate_data_out_tv():
        """
        Function to generate transmitter data output testvectors.

        Returns
        -------
        data_out : list
            The list of data output testvectors, including empty slot check flag and output data.
        """
        def generate_data_output(data_packet_record):
            time_counter = 0
            data_out = []
            last_packet_time = data_packet_record[-1][0]
            for data_packet in data_packet_record:
                # Time period with no data
                while time_counter < int(data_packet[0]):
                    data_out.append([time_counter, 0, str(bin(0)[2:].zfill(data_width))])
                    time_counter += 1
                # Clock cycle with destination ID
                if time_counter == int(data_packet[0]):
                    # Mapping NetworkSim ID to SystemVerilog ID
                    mapped_destination_id = data_packet[2] + 1
                    # Append destination ID
                    packet_content = str(bin(mapped_destination_id)[2:].zfill(data_width))
                    # Insert source ID
                    packet_content = str(bin(transmitter_id)[2:].zfill(id_width)) + packet_content[id_width:]
                    data_out.append([time_counter, 1, packet_content])
                    time_counter += 1
                # Time period with data
                packet_length = len(data_packet[1])
                num_clock_cycle = -(-packet_length // data_width)
                bit_counter = 0
                for i in range(num_clock_cycle):
                    if i == num_clock_cycle - 1:
                        data = data_packet[1][bit_counter:].ljust(data_width, '0')
                    else:
                        data = data_packet[1][bit_counter:bit_counter + data_width]
                    data_out.append([time_counter, 0, data])
                    bit_counter += data_width
                    time_counter += 1
                # Time period with no data after all packets
                if time_counter > last_packet_time:
                    while time_counter < simulator.until:
                        data_out.append([time_counter, 0, str(bin(0)[2:].zfill(data_width))])
                        time_counter += 1
            return data_out

        if simulator.bidirectional:
            cw_data_packet_record = simulator.downstream_transmitter[mapped_transmitter_id].transmitted_data_packet
            acw_data_packet_record = simulator.upstream_transmitter[mapped_transmitter_id].transmitted_data_packet
            return generate_data_output(data_packet_record=cw_data_packet_record), \
                generate_data_output(data_packet_record=acw_data_packet_record)
        else:
            data_packet_record = simulator.transmitter[mapped_transmitter_id].transmitted_data_packet
            return generate_data_output(data_packet_record=data_packet_record)

    if simulator.bidirectional:
        cw_ram_content_tv, acw_ram_content_tv = generate_ram_tv()
        cw_data_out_tv, acw_data_out_tv = generate_data_out_tv()
    else:
        ram_content_tv = generate_ram_tv()
        data_out_tv = generate_data_out_tv()

    if not simulator.bidirectional:
        # Write to test vector files
        with open(ram_filename, 'w') as f_ram:
            for i in range(len(ram_content_tv)):
                print(
                    str(bin(ram_content_tv[i][1])[2:].zfill(address_width)) + '_' + ram_content_tv[i][2],
                    file=f_ram
                )
        with open(data_out_assert_filename, 'w') as f_data_out_assert:
            for i in range(len(data_out_tv)):
                print(
                    str(bin(data_out_tv[i][1])[2:].zfill(1)) + '_' + data_out_tv[i][2],
                    file=f_data_out_assert
                )
    else:
        # Write to test vector files
        with open(cw_ram_filename, 'w') as f_ram_cw:
            for i in range(len(cw_ram_content_tv)):
                print(
                    str(bin(cw_ram_content_tv[i][1])[2:].zfill(address_width)) + '_' + cw_ram_content_tv[i][2],
                    file=f_ram_cw
                )
        with open(cw_data_out_assert_filename, 'w') as f_data_out_assert_cw:
            for i in range(len(cw_data_out_tv)):
                print(
                    str(bin(cw_data_out_tv[i][1])[2:].zfill(1)) + '_' + cw_data_out_tv[i][2],
                    file=f_data_out_assert_cw
                )
        with open(acw_ram_filename, 'w') as f_ram_acw:
            for i in range(len(acw_ram_content_tv)):
                print(
                    str(bin(acw_ram_content_tv[i][1])[2:].zfill(address_width)) + '_' + acw_ram_content_tv[i][2],
                    file=f_ram_acw
                )
        with open(acw_data_out_assert_filename, 'w') as f_data_out_assert_acw:
            for i in range(len(acw_data_out_tv)):
                print(
                    str(bin(acw_data_out_tv[i][1])[2:].zfill(1)) + '_' + acw_data_out_tv[i][2],
                    file=f_data_out_assert_acw
                )

    if simulator.bidirectional:
        return cw_ram_content_tv, acw_ram_content_tv, cw_data_out_tv, acw_data_out_tv
    else:
        return ram_content_tv, data_out_tv
