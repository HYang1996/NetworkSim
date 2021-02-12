__all__ = ["Summary"]
__author__ = ["Hongyi Yang"]

from NetworkSim.simulation.tools.performance_analysis import get_transfer_delay, get_queueing_delay

import numpy as np
import pandas as pd


class Summary:
    """
    Summary class to generate summaries for a given simulator.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator used in the simulation.
    """

    def __init__(
            self,
            simulator
    ):
        self.simulator = simulator

    def simulation_summary(self):
        """
        Overall summary of the simulation.

        Returns
        -------
        simulation_summary : pandas DataFrame
            A DataFrame containing a few key parameters in the simulation.
        """
        _rows = {
            'Total Number of Nodes': self.simulator.model.network.num_nodes,
            'Transmitter Type': self.simulator.transmitter_type,
            'Receiver Type': self.simulator.receiver_type,
            'Source Traffic Generation Method': self.simulator.traffic_generation_method,
            'Designed Average Data Rate (Gbit/s)': self.simulator.model.constants['average_bit_rate'],
            'Designed Maximum Data Rate (Gbit/s)': self.simulator.model.constants['maximum_bit_rate'],
            'Total Number of Data Packet Transmitted': len(self.simulator.latency),
            'Total Number of Transmission Error': len(self.simulator.error),
            'Estimated Average Queueing Delay (ns)': get_queueing_delay(self.simulator),
            'Estimated Average Transfer Delay (ns)': get_transfer_delay(self.simulator),
            'Average Queueing Delay Latency (ns)': np.mean(
                list(self.simulator.latency[i]['Queueing Delay'] for i in range(len(self.simulator.latency)))),
            'Average Transfer Delay Latency (ns)': np.mean(
                list(self.simulator.latency[i]['Transfer Delay'] for i in range(len(self.simulator.latency)))),
            'Final Data Rate (Gbit/s)': self.simulator.latency[-1]['Data Rate'],
            'Simulation Runtime (s)': self.simulator.runtime
        }
        summary = pd.DataFrame.from_dict(_rows, orient='index', columns=['Value'])
        summary.index.name = 'Simulation Parameter'
        return summary

    def ram_summary(self):
        """
        Summary of the transmitter RAMs.

        Returns
        -------
        ram_summary : pandas DataFrame
            A DataFrame with the packet generation information of each RAM, containing the columns:

            - `RAM ID`
                The RAM ID.
            - `Total Number of Data Packet Generated`
                The total number of data packets generated at each RAM.
            - `Percentage of Data Packet Generated (%)`
                Percentage of data packets generated at each RAM, compared to the total number of data packets \
                generated in all RAMs in the network.
        """
        _num_packet = [len(self.simulator.RAM[i].generated_data_packet)
                       for i in range(self.simulator.model.network.num_nodes)]
        _total_num_packet = np.sum(_num_packet)
        _percentage_generated = [_num_packet[i] / _total_num_packet * 100
                                 for i in range(self.simulator.model.network.num_nodes)]
        _ram_dict = {
            'RAM ID': list(range(self.simulator.model.network.num_nodes)),
            'Total Number of Data Packet Generated': _num_packet,
            'Percentage of Data Packet Generated (%)': _percentage_generated
        }
        return pd.DataFrame(_ram_dict)

    def transmitter_summary(self):
        """
        Summary of transmitters.

        Returns
        -------
        transmitter_summary : pandas DataFrame
            A DataFrame with the information on control and data packets transmitted from each transmitter, \
            containing the columns:

            - `Transmitter ID`
                The transmitter ID.
            - `Total Number of Control Packet Transmitted`
                Total number of control packets transmitted from each transmitter.
            - `Percentage of Control Packet Transmitted (%)`
                Percentage of control packets transmitted from each transmitter, compared to the total number \
                of control packets transmitted in the network.
            - `Total Number of Data Packet Transmitted`
                Total number of data packets transmitted from each transmitter.
            - `Percentage of Data Packet Transmitted (%)`
                Percentage of data packets transmitted from each transmitter, compared to the total number \
                of data packets transmitted in the network.
        """
        _num_control_packet = [len(self.simulator.transmitter[i].transmitted_control_packet)
                               for i in range(self.simulator.model.network.num_nodes)]
        _num_data_packet = [len(self.simulator.transmitter[i].transmitted_data_packet)
                            for i in range(self.simulator.model.network.num_nodes)]
        _total_control_packet = np.sum(_num_control_packet)
        _total_data_packet = np.sum(_num_data_packet)
        _percentage_control_packet = [_num_control_packet[i] / _total_control_packet * 100
                                      for i in range(self.simulator.model.network.num_nodes)]
        _percentage_data_packet = [_num_data_packet[i] / _total_data_packet * 100
                                   for i in range(self.simulator.model.network.num_nodes)]
        _transmitter_dict = {
            'Transmitter ID': list(range(self.simulator.model.network.num_nodes)),
            'Total Number of Control Packet Transmitted': _num_control_packet,
            'Percentage of Control Packet Transmitted (%)': _percentage_control_packet,
            'Total Number of Data Packet Transmitted': _num_data_packet,
            'Percentage of Data Packet Transmitted (%)': _percentage_data_packet
        }
        return pd.DataFrame(_transmitter_dict)

    def receiver_summary(self):
        """
        Summary of receivers.

        Returns
        -------
        receiver_summary : pandas DataFrame
            A DataFrame with the information on control and data packets received at each receiver, \
            containing the columns:

            - `Receiver ID`
                The receiver ID.
            - `Total Number of Control Packet Received`
                Total number of control packets received at each receiver.
            - `Percentage of Control Packet Received (%)`
                Percentage of control packets received at each receiver, compared to the total number \
                of control packets received in the network.
            - `Total Number of Data Packet Received`
                Total number of data packets received at each receiver.
            - `Percentage of Data Packet Received (%)`
                Percentage of data packets received at each receiver, compared to the total number \
                of data packets received in the network.
        """
        _num_control_packet = [len(self.simulator.receiver[i].received_control_packet)
                               for i in range(self.simulator.model.network.num_nodes)]
        _num_data_packet = [len(self.simulator.receiver[i].received_data_packet)
                            for i in range(self.simulator.model.network.num_nodes)]
        _total_control_packet = np.sum(_num_control_packet)
        _total_data_packet = np.sum(_num_data_packet)
        _percentage_control_packet = [_num_control_packet[i] / _total_control_packet * 100
                                      for i in range(self.simulator.model.network.num_nodes)]
        _percentage_data_packet = [_num_data_packet[i] / _total_data_packet * 100
                                   for i in range(self.simulator.model.network.num_nodes)]
        _receiver_dict = {
            'Receiver ID': list(range(self.simulator.model.network.num_nodes)),
            'Total Number of Control Packet Received': _num_control_packet,
            'Percentage of Control Packet Received (%)': _percentage_control_packet,
            'Total Number of Data Packet Received': _num_data_packet,
            'Percentage of Data Packet Received (%)': _percentage_data_packet
        }
        return pd.DataFrame(_receiver_dict)

    def latency_summary(self):
        """
        Summary of transmission latency.

        Returns
        -------
        average_latency_summary : pandas DataFrame
            A DataFrame of average latencies from one node to another. The columns represent destination nodes while \
            the index values represent source nodes.
        """
        # Initialise n x n array (n is the number of nodes in the network)
        # Row == Source Node, Column == Destination Node
        _n = self.simulator.model.network.num_nodes
        _latency_average = np.zeros([_n, _n])
        _latency_sum = np.zeros([_n, _n])
        _count = np.zeros([_n, _n])
        # Record latency information
        for latency_info in self.simulator.latency:
            _latency_sum[latency_info[1]][latency_info[2]] += latency_info[4]
            _count[latency_info[1]][latency_info[2]] += 1
        # Calculate latency mean
        for i in range(_n):
            for j in range(_n):
                if _count[i][j] == 0:
                    _latency_average[i][j] = np.nan
                else:
                    _latency_average[i][j] = _latency_sum[i][j] / _count[i][j]
        _rows = ['Source Node ' + str(i) for i in range(_n)]
        _columns = ['Destination Node ' + str(i) for i in range(_n)]
        return pd.DataFrame(_latency_average, index=_rows, columns=_columns)
