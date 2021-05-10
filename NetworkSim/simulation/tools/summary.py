__all__ = ["Summary"]
__author__ = ["Hongyi Yang"]

from NetworkSim.simulation.tools.performance_analysis import \
    get_transfer_delay, get_queueing_delay, get_service_delay, get_overall_delay

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
        if self.simulator.bidirectional:
            _direction = 'bi-directional'
        else:
            _direction = 'uni-directional'
        _rows = {
            'Total Number of Nodes': self.simulator.model.network.num_nodes,
            'Transmitter Type': self.simulator.transmitter_type,
            'Receiver Type': self.simulator.receiver_type,
            'Source Traffic Generation Method': self.simulator.traffic_generation_method,
            'Direction of Transmission': _direction,
            'Designed Average Data Rate (Gbit/s)': self.simulator.model.constants['average_bit_rate'],
            'Designed Maximum Data Rate (Gbit/s)': self.simulator.model.constants['maximum_bit_rate'],
            'Total Number of Data Packet Transmitted': len(self.simulator.latency),
            'Total Number of Transmission Error': len(self.simulator.error),
            'Estimated Average Queueing Delay (ns)':
            get_queueing_delay(self.simulator) + get_service_delay(self.simulator),
            'Estimated Average Transfer Delay (ns)': get_transfer_delay(self.simulator),
            'Average Queueing Delay Latency (ns)': get_overall_delay(self.simulator)['mean_queueing_delay'],
            'Average Transfer Delay Latency (ns)': get_overall_delay(self.simulator)['mean_transfer_delay'],
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

    def latency_summary(self, data_range, latency_type):
        """
        Summary of transmission latency.

        Parameters
        ----------
        data_range : str, optional
            The range of data selected for latency summary, chosen from the following:

            - `all` or `a`
                All simulation data.
            - `extended` or `e`
                Extended simulation data in convergence mode.
            - `batch` or `b`
                Last batch data in convergence mode.

            Default is ``None``, \
                which is extended data for convergence mode and all data for non-convergence mode.

        Returns
        -------
        average_latency_summary : pandas DataFrame
            A DataFrame of average latencies from one node to another. The columns represent destination nodes while \
            the index values represent source nodes.
        """
        _all_range_keywords = {'all', 'a'}
        _extended_range_keywords = {'extended', 'e'}
        _batch_range_keywords = {'batch', 'b'}
        _transfer_delay_keywords = {'transfer_delay', 'td'}
        _queueing_delay_keywords = {'queueing delay', 'qd'}
        if data_range is None:
            if self.simulator.convergence:
                data_range = 'e'
            else:
                data_range = 'a'
        if data_range in _all_range_keywords:
            _latency = self.simulator.latency
        elif data_range in _extended_range_keywords:
            if not self.simulator.convergence:
                raise ValueError("Extended latency summary can only be generated "
                                 "for the simulator with convergence mode enabled.")
            _start = self.simulator.batch_stats[-1]['end_index']
            _latency = self.simulator.latency[_start:]
        elif data_range in _batch_range_keywords:
            if not self.simulator.convergence:
                raise ValueError("Last batch latency summary can only be generated "
                                 "for the simulator with convergence mode enabled.")
            _start = self.simulator.batch_stats[-1]['start_index']
            _end = self.simulator.batch_stats[-1]['end_index']
            _latency = self.simulator.latency[_start:_end]
        else:
            raise ValueError("Latency range not recognised")
        if latency_type in _transfer_delay_keywords or latency_type is None:
            _type = 'Transfer Delay'
        elif latency_type in _queueing_delay_keywords:
            _type = 'Queueing Delay'
        else:
            raise ValueError("Latency type not recognised.")
        # Initialise n x n array (n is the number of nodes in the network)
        # Row == Source Node, Column == Destination Node
        _n = self.simulator.model.network.num_nodes
        _latency_average = np.zeros([_n, _n])
        _latency_sum = np.zeros([_n, _n])
        _count = np.zeros([_n, _n])
        # Record latency information
        for latency_info in _latency:
            _latency_sum[latency_info['Source ID']][latency_info['Destination ID']] += latency_info[_type]
            _count[latency_info['Source ID']][latency_info['Destination ID']] += 1
        # Calculate latency mean
        for i in range(_n):
            for j in range(_n):
                if _count[i][j] == 0:
                    _latency_average[i][j] = 0
                    # _latency_average[i][j] = np.nan
                else:
                    _latency_average[i][j] = _latency_sum[i][j] / _count[i][j]
        _rows = [i for i in range(_n)]
        _columns = [i for i in range(_n)]
        return pd.DataFrame(_latency_average, index=_rows, columns=_columns)

    def packet_count_summary(self):
        """
        Summary of transmission packet count.

        Returns
        -------
        count_summary : pandas DataFrame
            A DataFrame of transmitted packet count. The columns represent destination nodes while \
                the indices represent source nodes.
        """
        # Initialise n x n array (n is the number of nodes in the network)
        # Row == Source Node, Column == Destination Node
        _n = self.simulator.model.network.num_nodes
        _count = np.zeros([_n, _n])
        # Record packet transmission information
        for latency_info in self.simulator.latency:
            _count[latency_info['Source ID']][latency_info['Destination ID']] += 1
        _rows = [i for i in range(_n)]
        _columns = [i for i in range(_n)]
        return pd.DataFrame(_count, index=_rows, columns=_columns)

    def packet_delay_summary(self, normalised=False, std=False):
        """
        Summary of packet delay / queueing delay.
        Packet Delay (also refer as Queueing Delay) = successful transmission time - generation time of the packet

        Returns
        -------
        average_latency_summary : pandas DataFrame
            A DataFrame of average latencies from one node to another. The columns represent destination nodes while \
            the index values represent source nodes.
        """
        # Initialise n x n array (n is the number of nodes in the network)
        # Row == Source Node, Column == Destination Node
        _n = self.simulator.model.network.num_nodes
        _packet_duration = self.simulator.model.data_packet_duration
        _count = np.zeros([_n, _n])
        _sum = np.zeros([_n, _n])
        _packet_info_source_node_pair = [[[] for _ in range(_n)] for _ in range(_n)]
        _mean_packet_delay = np.zeros([_n, _n])
        _std_packet_delay = np.zeros([_n, _n])
        _rows = [i for i in range(_n)]
        _columns = [i for i in range(_n)]
        # Record packet transmission information
        if std:
            for latency_info in self.simulator.latency:
                _packet_info_source_node_pair[latency_info['Source ID']
                                              ][latency_info['Destination ID']].append(latency_info['Queueing Delay'])
            for i in range(_n):
                for j in range(_n):
                    temp_array = np.array(_packet_info_source_node_pair[i][j])
                    if temp_array.size == 0:
                        _mean_packet_delay[i][j] = 0
                        _std_packet_delay[i][j] = 0
                    else:
                        if normalised:
                            temp_array = temp_array / _packet_duration
                            _mean_packet_delay[i][j] = np.mean(temp_array)
                            _std_packet_delay[i][j] = np.std(temp_array)
                        else:
                            _mean_packet_delay[i][j] = np.mean(temp_array)
                            _std_packet_delay[i][j] = np.std(temp_array)
            return pd.DataFrame(_mean_packet_delay, index=_rows, columns=_columns), \
                pd.DataFrame(_std_packet_delay, index=_rows, columns=_columns)
        else:
            for latency_info in self.simulator.latency:
                _count[latency_info['Source ID']][latency_info['Destination ID']] += 1
                _sum[latency_info['Source ID']][latency_info['Destination ID']] += latency_info['Queueing Delay']
            for i in range(_n):
                for j in range(_n):
                    if _count[i][j] == 0 or _sum[i][j] == 0:
                        _mean_packet_delay[i][j] = 0
                    else:
                        if normalised:
                            _mean_packet_delay[i][j] = (_sum[i][j] / _count[i][j]) / _packet_duration
                        else:
                            _mean_packet_delay[i][j] = (_sum[i][j] / _count[i][j])
            return pd.DataFrame(_mean_packet_delay, index=_rows, columns=_columns)

    def ram_queue_summary(self):
        """
        Summary of queue size in the RAMs.

        Returns
        -------
        overall_mean : float
            Overall mean value of the recorded queue size in the RAMs.
        overall_max : float
            Overall maximum value of the recorded queue size in the RAMs.
        queue_size_summary : pandas DataFrame
            A pandas DataFrame containing the following columns for each RAM in the simulator:

            For unidirectional transmission:

            - `Mean Queue Size`
            - `Maximum Queue Size`

            For bidirectional transmission:

            - `Mean Queue Size (Upstream)`
            - `Mean Queue Size (Downstream)`
            - `Maximum Queue Size (Upstream)`
            - `Maximum Queue Size (Downstream)`
        """
        _n = self.simulator.model.network.num_nodes
        mean_queue_size = []
        max_queue_size = []
        mean_queue_size_bi = []
        max_queue_size_bi = []
        _rows = [i for i in range(_n)]
        df = pd.DataFrame(index=_rows)
        for ram in self.simulator.RAM:
            if self.simulator.bidirectional:
                _upstream_queue_record = list(record[1] for record in ram.queue_size_record)
                _downstream_queue_record = list(record[2] for record in ram.queue_size_record)
                mean_queue_size_bi.append([np.mean(_upstream_queue_record), np.mean(_downstream_queue_record)])
                max_queue_size_bi.append([np.max(_upstream_queue_record), np.max(_downstream_queue_record)])
                mean_queue_size.append(np.mean(_upstream_queue_record + _downstream_queue_record))
                max_queue_size.append(np.max(_upstream_queue_record + _downstream_queue_record))
            else:
                _queue_record = list(record[1] for record in ram.queue_size_record)
                mean_queue_size.append(np.mean(_queue_record))
                max_queue_size.append(np.max(_queue_record))
        if self.simulator.bidirectional:
            df[['Mean Queue Size (Upstream)', 'Mean Queue Size (Downstream)']] = pd.DataFrame(mean_queue_size_bi)
            df['Mean Queue Size (Overall)'] = pd.DataFrame(mean_queue_size)
            df[['Maximum Queue Size (Upstream)', 'Maximum Queue Size (Downstream)']] = pd.DataFrame(max_queue_size_bi)
            df['Maximum Queue Size (Overall)'] = pd.DataFrame(max_queue_size)
        else:
            df['Mean Queue Size'] = pd.DataFrame(mean_queue_size)
            df['Maximum Queue Size'] = pd.DataFrame(max_queue_size)
        overall_mean = np.mean(list(mean for mean in mean_queue_size))
        overall_max = np.max(list(mean for mean in max_queue_size))
        return overall_mean, overall_max, df
