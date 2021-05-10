__all__ = ["Info"]
__author__ = ["Hongyi Yang"]

import pandas as pd


class Info:
    """
    Information class to generate basic information of modules involved in the simulation.
    """

    def __init__(
            self,
            simulator
    ):
        self.simulator = simulator

    def ram_info(self, device_id):
        """
        Obtain information on generated data packets in transmitter RAM.

        Parameters
        ----------
        device_id : int
            The ID of the RAM.

        Returns
        -------
        generated_packets : pandas DataFrame
            A DataFrame with the generated data packets that have been stored in transmitter RAM, \
            containing the columns:

            - `Timestamp` : float
                The timestamp when the packet is generated using the method chosen.
            - `Interarrival to Next` : float
                The interarrival time from this packet to the next one.
            - `Raw Packet` : str or list
                The raw data packet generated, in string format if simulation is not abstract, and in list format \
                if simulation is abstract.
            - `Destination ID` : int
                The destination node ID to which the data packet is supposed to be sent.
        """
        _info = self.simulator.RAM[device_id].generated_data_packet
        return pd.DataFrame(_info, columns=[
            'Data Packet Generation Timestamp',
            'Interarrival Time to Next Packet',
            'Raw Packet Content',
            'Packet Destination Node ID'
        ])

    def transmitter_info(self, device_id, info_type):
        """
        Obtain information on transmitted control or data packets in transmitter.

        Parameters
        ----------
        device_id : int
            The ID of the transmitter.
        info_type : str
            The type of ring on which the transmitter transmits the packets.

        Returns
        -------
        transmitted_packets : pandas DataFrame
            A DataFrame with the transmitted control or data packets.

            If control ring is selected, the output contains the columns:

            - `Transmission Timestamp` : float
                The timestamp when the control packet is transmitted onto the control ring.
            - `Raw Packet` : str or list
                The transmitted raw control packet, in the format of a list if abstract simulation is used \
                or string if the simulation is not abstract.
            - `Destination ID` : int
                The destination node ID to which the control packet is transmitted.

            If data ring is selected, the output contains the columns:

            - `Transmission Timestamp` : float
                The timestamp when the data packet is transmitted onto the data rings.
            - `Raw Packet` : str or list
                The transmitted raw data packet, in the format of a list if abstract simulation is used \
                or string if the simulation is not abstract.
            - `Destination ID` : int
                The destination node ID to which the data packet is transmitted.
        """
        _control_keywords = {'control', 'c'}
        _data_keywords = {'data', 'd'}
        # Select output data
        if info_type in _control_keywords:
            _info = self.simulator.transmitter[device_id].transmitted_control_packet
            return pd.DataFrame(_info, columns=[
                'Control Packet Transmission Timestamp',
                'Raw Packet Content',
                'Packet Destination Node ID'
            ])
        elif info_type in _data_keywords:
            _info = self.simulator.transmitter[device_id].transmitted_data_packet
            return pd.DataFrame(_info, columns=[
                'Data Packet Transmission Timestamp',
                'Raw Packet Content',
                'Packet Destination Node ID'
            ])
        else:
            raise ValueError("Ring type not recognised. Please select either 'control' for control ring "
                             "or 'data' for data rings.")

    def receiver_info(self, device_id, info_type):
        """
        Obtain information on received control or data packets in receiver.

        Parameters
        ----------
        device_id : int
            The ID of the receiver.
        info_type : str
            The type of information requested, chosen from the following:

            - `control`
                Received control packets.
            - `data`
                Received data packets.
            - `queue`
                RAM queue of control packets.

        Returns
        -------
        packet_information : pandas DataFrame
            A DataFrame with the receiver=d control or data packets.

            If control ring is selected, the output contains the columns:

            - `Reception Timestamp` : float
                The timestamp when the control packet is received from the control ring.
            - `Raw Packet` : str or list
                The received raw control packet, in the format of a list if abstract simulation is used \
                or string if the simulation is not abstract.
            - `Source ID` : int
                The source node ID from which the control packet is received.

            If data ring is selected, the output contains the columns:

            - `Reception Timestamp` : float
                The timestamp when the data packet is received from the data rings.
            - `Raw Packet` : str or list
                The received raw data packet, in the format of a list if abstract simulation is used \
                or string if the simulation is not abstract.
            - `Source ID` : int
                The source node ID from which the data packet is received.

            If internal RAM queue is selected, the output contains the columns:

            - `Operation Timestamp` : float
                The timestamp when the operation is carried out.
            - `Raw Packet` : str
                The raw control packet.
            - `Source ID` : int
                Source ID of the control packet.
            - `Operation` : str
                Operation carried out on the packet in the queue.
        """
        _control_keywords = {'control', 'c'}
        _data_keywords = {'data', 'd'}
        _queue_keywords = {'queue', 'q'}
        # Select output data
        if info_type in _control_keywords:
            _info = self.simulator.receiver[device_id].received_control_packet
            return pd.DataFrame(_info, columns=[
                'Control Packet Reception Timestamp',
                'Raw Control Packet Content',
                'Packet Source Node ID'
            ])
        elif info_type in _data_keywords:
            _info = self.simulator.receiver[device_id].received_data_packet
            return pd.DataFrame(_info, columns=[
                'Data Packet Reception Timestamp',
                'Raw Data Packet Content',
                'Packet Source Node ID'
            ])
        elif info_type in _queue_keywords:
            _info = self.simulator.receiver[device_id].queue_record
            return pd.DataFrame(_info, columns=[
                'Operation Timestamp',
                'Raw Control Packet Content',
                'Packet Source Node ID',
                'Operation'
            ])
        else:
            raise ValueError("Ring type not recognised. Please select either 'control' for control ring "
                             "or 'data' for data rings.")

    def ring_info(self, ring_id, info_type):
        """
        Obtain packet transmission information on the control or data ring.

        Returns
        -------
        packet_record : pandas DataFrame
            A DataFrame containing the information on all packet transmission on the ring, including the columns:

            - `Generation Timestamp` : float
                The timestamp when the packet is generated and stored in the RAM.
            - `Transmission Timestamp` : float
                The timestamp when the packet is added onto the ring by the transmitter.
            - `Reception Timestamp` : float
                The timestamp when the packet is received by the receiver.
            - `Raw Packet` : str
                The raw packet content.
            - `Source Node` : int
                The ID of the source node.
            - `Destination Node` : int
                The ID of the destination node.
            - `Status` : str
                The status of the packet, can be ``added`` or ``removed``.
            - Total Packet Count : int
                The total number of packets on the ring at the time of the operation.
        """
        _control_keywords = {'control', 'c'}
        _data_keywords = {'data', 'd'}
        if info_type in _control_keywords:
            _info = self.simulator.model.control_ring.packet_record
        elif info_type in _data_keywords:
            if ring_id is None:
                raise ValueError("Data Ring ID must be specified.")
            else:
                _info = self.simulator.model.data_rings[ring_id].packet_record
        else:
            raise ValueError("Type of information requested is not recognised.")
        return pd.DataFrame(_info, columns=[
            'Generation Timestamp',
            'Transmission Timestamp',
            'Reception Timestamp',
            'Packet Raw Content',
            'Source Node ID',
            'Destination Node ID',
            'Packet Status on Ring',
            'Real-Time Total Packet Count'
        ])
