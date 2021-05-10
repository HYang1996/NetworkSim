__all__ = ["ParallelSimulator"]
__author__ = ["Hongyi Yang"]

import pandas as pd
from joblib import Parallel, delayed

from NetworkSim.architecture.base.network import Network
from NetworkSim.architecture.setup.model import Model
from NetworkSim.simulation.simulator.base import BaseSimulator


class ParallelSimulator:
    """
    Parallel simulator class to enable multiple simulations to be run in parallel with minimum input parameters.

    All parameters of the simulation should be input as a list, and in one of the following fashions:

    - If the parameter is not specified, i.e. parameter value is ``None``, the parameter is set to the default value.
    - If one value of the parameter is specified, i.e. `parameter=[param_value]`, all simulations run on the same \
        specified value.
    - Parameter values for all simulations are specified. The indices of the values in the list indicate the \
        numbers of the simulators. Therefore, if two simulations with TT-FR and FT-TR are to be run, the parameters \
        should be set to: `transmitter_type=['T', 'F'], receiver_type=['F', 'T']`.

    The number of simulators correspond to the length of the list in which all parameter values are specified. For \
    example, if `average_data_rate=[10, 20, 30, 40, 50]`, 5 simulations will be created, and the simulator number \
    corresponds to the index of the parameter values in the list input. The `summary()` function can be called \
    after the simulation for an inspection of detailed parameters of each simulator used.

    Parameters
    ----------
    until : float, optional
        The end time of the simulations. This should be specified if the simulation does not run on convergence. \
            Default is ``None``.
    convergence : bool, optional
        Automatic convergence mode of simulation. Default is ``True``.
    sem_tr : float, optional
        The threshold standard error of mean (SEM) for convergence. Default is ``None``.
    bs : int, optional
        The batch size for SEM calculation during convergence. Default is ``None``.
    num_nodes : int, optional
        The total number of nodes in the network. Default value follows that in the `Network` class (``100``).
    transmitter_type : str, optional
        The type of transmitter, chosen from the following:

        - `tunable`, `t` or `T`
            Tunable transmitter (fixed receiver must be chosen).
        - `fixed`, `f`, or `F`
            Fixed transmitter (tunable receiver must be chosen).

        Default is ``tunable``.
    receiver_type : str, optional
        The type of receivers, chosen from the following:

        - `tunable`, `t` or `T`
            Tunable receiver (fixed transmitter must be chosen).
        - `fixed`, `f`, or `F`
            Fixed receiver (tunable transmitter must be chosen).

        Default is ``fixed``.
    traffic_generation_method : str, optional
        The source traffic generation method, chosen from the following:

        - `poisson`
            Poisson (biased negative exponential) distribution.
        - `pareto`
            Pareto distribution.

        Default is ``poisson``.
    max_data_rate : float, optional
        The maximum data rate at each node, in Gbit/s. Default is ``100``.
    average_data_rate : float, optional
        The expected average data rate at each node, in Gbit/s. Default is ``50``.
    bidirectional : bool, optional
        The type of network architecture, either bidirectional or unidirectional. \
            Default is ``False``, which is unidirectional.
    seed : int, optional
        The seed used for source traffic generation. Default is ``1``.
    n_jobs : int, optional
        The number of processors used for parallel operations. Default is ``-1`` (all available processors).
    """

    def __init__(
            self,
            until=None,
            convergence=None,
            sem_tr=None,
            bs=None,
            num_nodes=None,
            transmitter_type=None,
            receiver_type=None,
            traffic_generation_method=None,
            max_data_rate=None,
            average_data_rate=None,
            bidirectional=None,
            seed=None,
            n_jobs=-1
    ):
        if until is None:
            until = [None]
        self.until = until
        if convergence is None:
            convergence = [None]
        self.convergence = convergence
        if sem_tr is None:
            sem_tr = [None]
        self.sem_tr = sem_tr
        if bs is None:
            bs = [None]
        self.bs = bs
        if num_nodes is None:
            num_nodes = [None]
        self.num_nodes = num_nodes
        if transmitter_type is None:
            transmitter_type = [None]
        self.transmitter_type = transmitter_type
        if receiver_type is None:
            receiver_type = [None]
        self.receiver_type = receiver_type
        if traffic_generation_method is None:
            traffic_generation_method = [None]
        self.traffic_generation_method = traffic_generation_method
        if max_data_rate is None:
            max_data_rate = [None]
        self.max_data_rate = max_data_rate
        if average_data_rate is None:
            average_data_rate = [None]
        self.average_data_rate = average_data_rate
        if bidirectional is None:
            bidirectional = [False]
        self.bidirectional = bidirectional
        if seed is None:
            seed = [1]
        self.seed = seed
        self.n_jobs = n_jobs
        self.simulator = None
        self.num_param = None
        self.env = None

    def _check_parameters(self):
        """
        Function to check input parameters and standardise their format.
        """
        # Check input consistency and type
        _length = []
        _params = [
            self.until,
            self.convergence,
            self.sem_tr,
            self.bs,
            self.num_nodes,
            self.transmitter_type,
            self.receiver_type,
            self.traffic_generation_method,
            self.max_data_rate,
            self.average_data_rate,
            self.bidirectional,
            self.seed
        ]
        for _param in _params:
            if isinstance(_param, list):
                if len(_param) > 1:
                    _length.append(len(_param))
            else:
                raise ValueError("Input parameter must be a list.")
        if _length.count(_length[0]) == len(_length):
            _length = _length[0]
            # Ensure consistency input list length
            if len(self.until) == 1:
                self.until = self.until * _length
            if len(self.convergence) == 1:
                self.convergence = self.convergence * _length
            if len(self.sem_tr) == 1:
                self.sem_tr = self.sem_tr * _length
            if len(self.bs) == 1:
                self.bs = self.bs * _length
            if len(self.num_nodes) == 1:
                self.num_nodes = self.num_nodes * _length
            if len(self.transmitter_type) == 1:
                self.transmitter_type = self.transmitter_type * _length
            if len(self.receiver_type) == 1:
                self.receiver_type = self.receiver_type * _length
            if len(self.traffic_generation_method) == 1:
                self.traffic_generation_method = self.traffic_generation_method * _length
            if len(self.max_data_rate) == 1:
                self.max_data_rate = self.max_data_rate * _length
            if len(self.average_data_rate) == 1:
                self.average_data_rate = self.average_data_rate * _length
            if len(self.bidirectional) == 1:
                self.bidirectional = self.bidirectional * _length
            if len(self.seed) == 1:
                self.seed = self.seed * _length
        else:
            raise ValueError("The numbers of input parameters do not match.")
        return _length

    def _initialise_simulator(self, simulator_id):
        """
        Function to initialise individual simulators.

        Parameters
        ----------
        simulator_id: int
            The ID of the simulator.
        """
        if self.num_nodes[simulator_id] is not None:
            _network = Network(num_nodes=self.num_nodes[simulator_id])
            _model = Model(network=_network, bidirectional=self.bidirectional[simulator_id])
        else:
            _model = Model(bidirectional=self.bidirectional[simulator_id])
        if self.max_data_rate[simulator_id] is not None:
            _model.constants['maximum_bit_rate'] = self.max_data_rate[simulator_id]
        if self.average_data_rate[simulator_id] is not None:
            _model.constants['average_bit_rate'] = self.average_data_rate[simulator_id]
        self.simulator[simulator_id] = BaseSimulator(
            until=self.until[simulator_id],
            convergence=self.convergence[simulator_id],
            sem_tr=self.sem_tr[simulator_id],
            bs=self.bs[simulator_id],
            model=_model,
            transmitter_type=self.transmitter_type[simulator_id],
            receiver_type=self.receiver_type[simulator_id],
            traffic_generation_method=self.traffic_generation_method[simulator_id],
            bidirectional=self.bidirectional[simulator_id],
            id=simulator_id,
            seed=self.seed[simulator_id]
        )
        self.simulator[simulator_id].initialise()

    def _run_simulator(self, simulator_id):
        """
        Function to run individual simulators.

        Parameters
        ----------
        simulator_id : int
            The ID of the simulator.
        """
        self.simulator[simulator_id].run()

    def initialise(self):
        """
        Initialisation of parallel simulations.
        """
        self.num_param = self._check_parameters()
        self.simulator = [None] * self.num_param
        Parallel(n_jobs=self.n_jobs, require='sharedmem')(delayed(
            self._initialise_simulator)(i) for i in range(self.num_param))

    def run(self):
        """
        Run all simulations in parallel.
        """
        Parallel(n_jobs=self.n_jobs, require='sharedmem')(
            delayed(self._run_simulator)(i) for i in range(self.num_param))

    def info(self, simulation_id, info_type, component_type, component_id):
        """
        Obtain simulation information from individual simulators.

        Parameters
        ----------
        simulation_id : int
            The ID of the simulator.
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

        """
        return self.simulator[simulation_id].info(
            info_type=info_type,
            component_type=component_type,
            component_id=component_id
        )

    def summary(self, simulator_id=None, summary_type=None):
        """
        Obtain summaries of the simulations.

        Parameters
        ----------
        simulator_id : int, optional
            The simulator ID of choice. Default is ``None``. If no ID is specified, a combined generic summary of \
            the key parameters used in all simulators is produced.
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

            This is an individual summary of the specified simulator, and therefore a `simulator_id` must be \
            specified.
        """
        if summary_type is None and simulator_id is None:
            _summary = []
            for i in range(len(self.simulator)):
                _individual_summary = self.simulator[i].summary()['Value'].tolist()
                _individual_summary.insert(0, i)
                _summary.append(_individual_summary)
            _headers = [
                'BaseSimulator ID',
                'Total Number of Nodes',
                'Transmitter Type',
                'Receiver Type',
                'Source Traffic Generation Method',
                'Direction of Transmission',
                'Designed Average Data Rate (Gbit/s)',
                'Designed Maximum Data Rate (Gbit/s)',
                'Total Number of Data Packet Transmitted',
                'Total Number of Transmission Error',
                'Estimated Average Queueing Delay (ns)',
                'Estimated Average Transfer Delay (ns)',
                'Average Queueing Delay Latency (ns)',
                'Average Transfer Delay Latency (ns)',
                'Final Data Rate (Gbit/s)',
                'Simulation Runtime (s)'
            ]
            return pd.DataFrame(_summary, columns=_headers)
        else:
            if simulator_id is None or not 0 <= simulator_id <= len(self.simulator):
                return ValueError("Please enter a valid simulator ID.")
            else:
                return self.simulator[simulator_id].summary(summary_type=summary_type)
