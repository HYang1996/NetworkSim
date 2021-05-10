__all__ = ["BaseSimulator"]
__author__ = ["Hongyi Yang", "Cheuk Ming Chung"]

from timeit import default_timer as timer
import simpy
import pandas as pd
from tqdm.auto import trange
from tqdm.auto import tqdm
import numpy as np
from scipy.stats import sem as SEM

from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.process.ram import RAM
from NetworkSim.simulation.process.receiver.fixed import FR
from NetworkSim.simulation.process.receiver.fixed_upstream import FR_U
from NetworkSim.simulation.process.receiver.fixed_downstream import FR_D
from NetworkSim.simulation.process.receiver.tunable import TR
from NetworkSim.simulation.process.transmitter.fixed import FT
from NetworkSim.simulation.process.transmitter.tunable import TT
from NetworkSim.simulation.process.transmitter.tunable_upstream import TT_U
from NetworkSim.simulation.process.transmitter.tunable_downstream import TT_D
from NetworkSim.simulation.tools.info import Info
from NetworkSim.simulation.tools.summary import Summary
from NetworkSim.simulation.tools.plot import plot_latency, plot_latency_throughput, plot_count


class BaseSimulator:
    """
    Simulation wrapper to create a discrete event simulation of the ring network.

    Parameters
    ----------
    until : float
        The end time of the simulation. Default is ``None``.
    convergence : bool
        Automatic convergence mode of simulation. Default is ``True``.
    sem_tr : float
        The threshold standard error of mean (SEM) for convergence. Default is ``0.05``.
    bs : int
        The batch size for SEM calculation during convergence. Default is ``10000``.
    env: simpy Environment, optional
        The environment in which the simulation is carried out. Default is ``simpy.Environment()``.
    model : Model, optional
        The network model used for the simulation. Default is ``Model()``.
    transmitter_type: str
        The type of transmitter used for the simulation, chosen from the list:

        - `fixed`, `f` or `F`
            Fixed transmitter.
        - `tunable`, `t` or `T`
            Tunable transmitter.

        Default is  ``tunable``.
    receiver_type: str
        The type of receiver used for the simulation, chosen from the list:

        - `fixed`, `f` or `F`
            Fixed receiver.
        - `tunable`, `t`, or `T`
            Tunable receiver.

        Default is  ``fixed``.
    traffic_generation_method : str
        The method used for generate source traffic, chosen from the list:

        - `poisson`
            Poisson distribution.
        - `pareto`
            Pareto distribution.

        Default is ``poisson``.
    bidirectional : bool, optional
        The type of network architecture, either bidirectional or unidirectional. \
            Default is ``False``, which is unidirectional.
    seed : int, optional
        The seed used for source traffic generation. Default is ``1``.

    ----------
    latency : list
        A list of packet transmission latency recorded during the simulation, containing the keys:

        - `Latency Timestamp` : float
            The timestamp when the latency is recorded.
        - `Source ID` : int
            The ID of the source node.
        - `Destination ID` : int
            The ID of the destination node.
        - `Queueing Delay` : float
            The recorded queueing delay latency.
        - `Transfer Delay` : float
            The recorded transfer delay latency.
        - `Data Rate` : float
            The data rate recorded as the operation is completed.

    error : list
        A list of transmission errors occurred during the simulation, containing the keys:

        - `Error Timestamp` : float
            The timestamp when the error occurred.
        - `Source ID` : int
            The ID of the source node.
        - `Destination ID` : int
            The ID of the destination node.
        - `Error Type` : str
            The type of error recorded.
    """

    def __init__(
            self,
            until=None,
            convergence=True,
            sem_tr=None,
            bs=None,
            extended=True,
            env=None,
            model=None,
            transmitter_type=None,
            receiver_type=None,
            traffic_generation_method=None,
            bidirectional=False,
            id=0,
            seed=None,
    ):
        # Check for simulator operation mode
        if until is None:
            if not convergence:
                raise ValueError("Either fixed-time or convergence simulation must be chosen.")
        else:
            convergence = False
        self.until = until
        self.convergence = convergence
        # Check for standard error of mean range
        if convergence:
            if sem_tr is None:
                sem_tr = 0.05
            if sem_tr <= 0 or sem_tr >= 1:
                raise ValueError("Standard error of mean (sem) for convergence must lie between 0 and 1.")
        self.sem_tr = sem_tr
        if bs is None:
            bs = 10000
        self.bs = bs
        self.extended = extended
        if env is None:
            env = simpy.Environment()
        self.env = env
        if model is None:
            model = Model(bidirectional=bidirectional)
        if transmitter_type is None:
            transmitter_type = 'T'
        if receiver_type is None:
            receiver_type = 'F'
        if traffic_generation_method is None:
            traffic_generation_method = 'poisson'
        self.transmitter_type = transmitter_type
        self.receiver_type = receiver_type
        self.traffic_generation_method = traffic_generation_method
        self.bidirectional = bidirectional
        # Check for bidirectional ring consistency
        if model.bidirectional != self.bidirectional:
            raise ValueError("Please ensure Model bidirectional value is consistent with Simulator.")
        self.id = id
        self.model = model
        if seed is None:
            seed = 1
        self.seed = seed
        self.RAM = [None] * self.model.network.num_nodes
        if self.bidirectional:
            self.upstream_transmitter = [None] * self.model.network.num_nodes
            self.downstream_transmitter = [None] * self.model.network.num_nodes
            self.upstream_receiver = [None] * self.model.network.num_nodes
            self.downstream_receiver = [None] * self.model.network.num_nodes
        else:
            self.transmitter = [None] * self.model.network.num_nodes
            self.receiver = [None] * self.model.network.num_nodes
        self._fixed_keywords = {'fixed', 'f', 'F'}
        self._tunable_keywords = {'tunable', 't', 'T'}
        self.runtime = None
        self.latency = []
        self.error = []
        self.TT_FR_tuning_delay = None
        self.ram_queue_delay = []
        self.batch_stats = []

    def _initialise_ram(self, node_id):
        """
        RAM initialisation.

        Parameters
        ----------
        node_id : int
            Id of the node (RAM).
        """
        # Create RAM process
        self.RAM[node_id] = RAM(
            env=self.env,
            until=self.until,
            ram_id=node_id,
            model=self.model,
            distribution=self.traffic_generation_method,
            bidirectional=self.bidirectional,
            seed=self.seed
        )
        # Initialise RAM process
        self.RAM[node_id].initialise()

    def _initialise_transmitter(self, node_id):
        """
        Transmitter initialisation.

        Parameters
        ----------
        node_id : int
            ID of the node (transmitter).
        """
        if self.bidirectional:
            if self.transmitter_type in self._tunable_keywords:
                # Transmitter in upstream direction
                self.upstream_transmitter[node_id] = TT_U(
                    env=self.env,
                    until=self.until,
                    ram=self.RAM[node_id],
                    transmitter_id=node_id,
                    model=self.model,
                    simulator=self
                )
                # Transmitter in downstream direction
                self.downstream_transmitter[node_id] = TT_D(
                    env=self.env,
                    until=self.until,
                    ram=self.RAM[node_id],
                    transmitter_id=node_id,
                    model=self.model,
                    simulator=self
                )
            else:
                raise NotImplementedError("Only tunable transmitter is implemented for bi-directional systems.")
            self.upstream_transmitter[node_id].initialise()
            self.downstream_transmitter[node_id].initialise()
        else:
            # Create and initialise transmitter process
            if self.transmitter_type in self._fixed_keywords:
                self.transmitter[node_id] = FT(
                    env=self.env,
                    until=self.until,
                    ram=self.RAM[node_id],
                    transmitter_id=node_id,
                    model=self.model,
                    simulator=self
                )
            elif self.transmitter_type in self._tunable_keywords:
                self.transmitter[node_id] = TT(
                    env=self.env,
                    until=self.until,
                    ram=self.RAM[node_id],
                    transmitter_id=node_id,
                    model=self.model,
                    simulator=self
                )
            else:
                raise NotImplementedError("Transmitter type not implemented.")
            self.transmitter[node_id].initialise()

    def _initialise_receiver(self, node_id):
        """
        Receiver initialisation.

        Parameters
        ----------
        node_id : int
            ID of the node (receiver).
        """
        if self.bidirectional:
            if self.receiver_type in self._fixed_keywords:
                self.upstream_receiver[node_id] = FR_U(
                    env=self.env,
                    until=self.until,
                    receiver_id=node_id,
                    model=self.model,
                    simulator=self
                )
                self.downstream_receiver[node_id] = FR_D(
                    env=self.env,
                    until=self.until,
                    receiver_id=node_id,
                    model=self.model,
                    simulator=self
                )
            else:
                raise NotImplementedError("Only fixed receiver is implemented for bi-directional systems.")
            self.upstream_receiver[node_id].initialise()
            self.downstream_receiver[node_id].initialise()
        else:
            # Create and initialise receiver process
            if self.receiver_type in self._fixed_keywords:
                self.receiver[node_id] = FR(
                    env=self.env,
                    until=self.until,
                    receiver_id=node_id,
                    model=self.model,
                    simulator=self
                )
            elif self.receiver_type in self._tunable_keywords:
                self.receiver[node_id] = TR(
                    env=self.env,
                    until=self.until,
                    receiver_id=node_id,
                    model=self.model,
                    simulator=self
                )
            else:
                raise NotImplementedError("Receiver type not implemented.")
            self.receiver[node_id].initialise()

    def initialise(self):
        """
        Initialisation of the simulation, where RAM, transmitter, and receiver processes are added to the environment.
        """
        # Check if the combination is implemented
        if self.transmitter_type in self._fixed_keywords and self.receiver_type in self._fixed_keywords:
            raise NotImplementedError("The FT-FR model is not implemented.")
        if self.transmitter_type in self._tunable_keywords and self.receiver_type in self._tunable_keywords:
            raise NotImplementedError("The TT-TR model is not implemented.")
        # Initialise all three subsystems
        for node_id in range(self.model.network.num_nodes):
            self._initialise_ram(node_id=node_id)
            self._initialise_transmitter(node_id=node_id)
            self._initialise_receiver(node_id=node_id)

    def run(self):
        """
        Run simulation.
        """
        _start_time = timer()
        # Fixed-time mode
        if not self.convergence:
            desc = 'Simulator ' + str(self.id) + ' (convergence disabled)'
            for i in trange(1, self.until, desc=desc):
                self.env.run(until=i)
        # Automatic convergence mode
        else:
            # initialise parameters
            sem = np.inf
            mean_data_rate = np.inf
            until = 1
            batch_number = 1
            start = 0

            def compute_batch_sem(last_sem, last_mean, start):
                """Function to compute batch SEM of data rate.

                Parameters
                ----------
                last_sem : float
                    Previous SEM value.
                last_mean : float
                    Previous batch mean.
                start : int
                    Index of the starting pointer of the `latency` list.

                Returns
                -------
                sem, end, mean_data_rate : float, int, float
                    Calculated batch data rate SEM value, the last index of the `latency` list \
                        and the mean data rate of the batch.
                """
                # Check if latency is updated
                end = len(self.latency)
                if start == end:
                    return last_sem, start, last_mean
                # Calculate batch SEM
                batch = self.latency[start:]
                batch_data_rate = list([record['Data Rate'] for record in batch])
                sem = SEM(batch_data_rate) * 2
                mean_data_rate = np.mean(batch_data_rate)
                return sem, end, mean_data_rate

            def update_until(until):
                """Function to update the `until` values in all processes.

                Parameters
                ----------
                until : int
                    New until value.
                """
                for ram in self.RAM:
                    ram.until = until
                if self.bidirectional:
                    for upstream_transmitter in self.upstream_transmitter:
                        upstream_transmitter.until = until
                    for downstream_transmitter in self.downstream_transmitter:
                        downstream_transmitter.until = until
                    for upstream_receiver in self.upstream_receiver:
                        upstream_receiver.until = until
                    for downstream_receiver in self.downstream_receiver:
                        downstream_receiver.until = until
                else:
                    for transmitter in self.transmitter:
                        transmitter.until = until
                    for receiver in self.receiver:
                        receiver.until = until

            # Run batches until convergence
            pbar_while = tqdm(total=batch_number + 1, desc='Simulator ' + str(self.id) + ' (convergence enabled)')
            while sem >= self.sem_tr:
                # Update until values and run batch
                update_until(until=until + self.bs)
                desc_for = 'Simulator ' + str(self.id) + ' Batch ' + str(batch_number)
                pbar_for = trange(until, until + self.bs, desc=desc_for, leave=False)
                for i in pbar_for:
                    self.env.run(until=i)
                # Compute and record batch statistics
                stats = {}
                stats['timestamp'] = until + self.bs - 1
                stats['start_index'] = start
                sem, start, mean_data_rate = compute_batch_sem(last_sem=sem, start=start, last_mean=mean_data_rate)
                stats['end_index'] = start
                stats['sem'] = sem
                stats['mean'] = mean_data_rate
                self.batch_stats.append(stats)
                until += self.bs
                batch_number += 1
                desc_while = 'Simulator %d (convergence enabled, batch SEM %.5f)' % (self.id, sem)
                pbar_while.set_description(desc=desc_while)
                pbar_while.update(1)

            # Run extended simulations after convergence
            if self.extended:
                # Run for another 50% of time
                extended_begin = int(self.env.now) + 1
                extended_until = int(self.env.now * 1.5) + 1
                update_until(until=extended_until)
                desc = 'Simulator ' + str(self.id) + ' Extended Run'
                for i in trange(extended_begin, extended_until, desc=desc):
                    self.env.run(until=i)

        _end_time = timer()
        self.runtime = _end_time - _start_time

    def info(
            self,
            info_type=None,
            component_type=None,
            component_id=None):
        """
        Obtain information of simulation components. Check `Info` class fore more details.

        Parameters
        ----------
        info_type : str
            The type of information requested, chosen from the following:

            - `control` or `c`
                Information on control ring. When `device_type == None`, this returns all packet transmission \
                information on the control ring, otherwise it refers to control packets transmitted by a transmitter \
                or control packets received by a receiver. `component_id` is not required in this case.
            - `data` or `d`
                Information on data ring. When `device_type == None`, this returns all packet transmission \
                information on the data ring, otherwise it refers to data packets transmitted by a transmitter \
                or data packets received by a receiver. An `component_id` must be specified in this case.

        component_type : str
            The type of component in the simulation, chosen from the following:

            - `ram` or `RAM`
                Transmitter RAM information, where data packets are generated. An `component_id` must be specified \
                in this case, but `info_type` is not required.
            - `transmitter` or `t`
                Transmitter packet information. Both `component_id` and `info_type` must be specified.
            - `receiver` or `r`
                Receiver packet information. Both `component_id` and `info_type` must be specified.

        component_id : int
            The ID of the component of choice.

        Returns
        -------
        info : pandas DataFrame
            A DataFrame containing the information requested.
        """
        _ram_keywords = {'ram', 'RAM'}
        _transmitter_keywords = {'transmitter', 't'}
        _receiver_keywords = {'receiver', 'r'}
        _info = Info(simulator=self)
        if component_type is None:
            return _info.ring_info(ring_id=component_id, info_type=info_type)
        elif component_type in _ram_keywords:
            return _info.ram_info(device_id=component_id)
        elif component_type in _transmitter_keywords:
            return _info.transmitter_info(device_id=component_id, info_type=info_type)
        elif component_type in _receiver_keywords:
            return _info.receiver_info(device_id=component_id, info_type=info_type)
        else:
            raise ValueError("Type of information requested is not recognised.")

    def summary(
        self,
        summary_type=None,
        output_format='df',
        node_id=None,
        latency_type=None,
        bar3d=False,
        data_range=None,
    ):
        """
        Obtain a summary of the simulation performed. Refer to `Summary` class for more details.

        Parameters
        ----------
        summary_type : str, optional
            The type of summary, chosen from the following:

            - `None`
                No `summary_type` input, and a generic summary is returned.
            - `latency` or `l`
                Latency summary, with latency information for all source-destination combinations.
            - `ram` or `RAM`
                Transmitter RAM data generation summary.
            - `transmitter` or `t`
                Transmitter summary.
            - `receiver` or `r`
                Receiver summary.
            - `count` or `c`
                Total packet transmission count.
            - `queue` or `q`
                Queue size in RAMs.
        output_format : str, optional
            The format of the summary, chosen from the following:

            - `df`
                Return a pandas DataFrame, which is the default output format.
            - `csv`
                Export a summary of the simulation performed as a csv file. Refer to `Summary` class for more details.
            - `plot`
                A plot of the summary selected.
        node_id : int, optional
            The node ID used for latency summary plot output.
        latency_type : string, optional
            The latency type of interset, by default is ``None``, which is transfer delay. \
                Setting it as `queueing delay` or `qd` switches it to queueing delay.
        bar3d : bool, optional
            Enable 3d bar plot for queueing delay, default is ``False``.
        data_range : str, optional
            The range of data selected for latency and delay summary, chosen from the following:

            - `all` or `a`
                All simulation data.
            - `extended` or `e`
                Extended simulation data in convergence mode.
            - `batch` or `b`
                Last batch data in convergence mode.

            Default is ``None``, \
                which is extended data for convergence mode and all data for non-convergence mode.
        """
        _latency_keywords = {'latency', 'l'}
        _ram_keywords = {'ram', 'RAM'}
        _transmitter_keywords = {'transmitter', 't'}
        _receiver_keywords = {'receiver', 'r'}
        _count_keywords = {'count', 'c'}
        _queueing_delay_keywords = {'queueing delay', 'qd'}
        _queue_size_keywords = {'queue', 'q'}
        _summary = Summary(simulator=self)
        summary_df = None
        _summary_name = None
        if summary_type is None:
            summary_df = _summary.simulation_summary()
            summary_type = 'simulation'
        elif summary_type in _ram_keywords:
            summary_df = _summary.ram_summary()
        elif summary_type in _transmitter_keywords:
            summary_df = _summary.transmitter_summary()
        elif summary_type in _receiver_keywords:
            summary_df = _summary.receiver_summary()
        elif summary_type in _latency_keywords:
            if latency_type in _queueing_delay_keywords:
                summary_df = _summary.packet_delay_summary()
            else:
                summary_df = _summary.latency_summary(data_range=data_range, latency_type=latency_type)
        elif summary_type in _count_keywords:
            summary_df = _summary.packet_count_summary()
        elif summary_type in _queue_size_keywords:
            summary_df = _summary.ram_queue_summary()
        else:
            raise ValueError("Summary type is not recognised.")

        # Output summary based on format selected
        if output_format == 'df':
            return summary_df
        elif output_format == 'csv':
            _summary_name = summary_type
            _file_name = _summary_name + "_summary.csv"
            summary_df.to_csv(_file_name, index=False)
        elif output_format == 'plot':
            if summary_type == 'simulation':
                return plot_latency_throughput(self.latency)
            elif summary_type in _latency_keywords:
                return plot_latency(
                    simulator=self,
                    latency=summary_df,
                    node_id=node_id,
                    latency_type=latency_type,
                    bar3d=bar3d
                )
            elif summary_type in _count_keywords:
                return plot_count(summary_df)
            else:
                raise ValueError("Plot type not recognised.")
        else:
            raise ValueError("Output format not recognised.")

    def export_data_as_csv(self, file_name=None, data=None, index=None, columns=None):
        """
        Export a python list as a csv file.

        Parameters
        ----------
        file_name: string
            Name of the output csv file

        data : ndarray (structured or homogeneous), Iterable, dict, or DataFrame
            The data to be exported as csv file

        index: list, optional
            Index to use for resulting csv file

        columns: list, optional
            Column labels to use for csv file
        """
        if not isinstance(file_name, str):
            raise ValueError("file_name must be a string.")
        elif file_name.rfind(".csv", -4) == -1:
            file_name = file_name + ".csv"
        df = pd.DataFrame(data, columns=columns, index=index)
        row_names = False
        if index:
            row_names = True
        df.to_csv(file_name, index=row_names)
