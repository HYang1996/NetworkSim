__all__ = [
    "load_model",
    "save_model",
    "clear_env"
]
__author__ = ["Hongyi Yang"]

import pickle
import bz2
import os
from tqdm.auto import tqdm

from NetworkSim.simulation.simulator.base import BaseSimulator
from NetworkSim.simulation.simulator.parallel import ParallelSimulator


def load_model(fname=None, dir=None):
    """
    Function to load previously saved pickle files as models.

    Parameters
    ----------
    fname : str, optional
        File name of the model, by default ``None``, \
            such that all models under the directory are loaded.
    dir : str, optional
        Directory of the models, by default ``None``, \
            corresponding to the `models` directory.

    Returns
    -------
    simulator : list
        A list of simulators loaded.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if dir is None:
        load_dir = os.path.join(dir_path, '../../../', 'models')
    else:
        load_dir = dir
    os.chdir(load_dir)
    simulators = []
    for filename in tqdm(os.listdir(load_dir), desc="Scanning files"):
        _load_file = False
        if fname is None or filename == fname:
            _load_file = True
        if _load_file:
            try:
                if os.path.getsize(filename) > 0:
                    print("Load", filename)
                    # with open(filename, 'rb') as input:
                    #     _simulator = pickle.load(input)
                    input = bz2.BZ2File(filename, 'rb')
                    _simulator = pickle.load(input)
                    if isinstance(_simulator, BaseSimulator) or isinstance(_simulator, ParallelSimulator):
                        simulators.append(_simulator)
                    else:
                        print(filename, "not recognised as a valid simulator object.")
            except pickle.PickleError:
                print(filename, "cannot be unpickled.")
                continue
    os.chdir(dir_path)
    return simulators


def clear_env(simulator, minimal):
    """
    Function to clear all `simpy Environment` in the simulator.

    Parameters
    ----------
    simulator : BaseSimulator
        The simulator whose `env` variable is to be cleared.
    minimal : bool, optional
        If the size is further reduced.

    Returns
    -------
    simulator : BaseSimulator
        The simulator with all `env` variable cleared.
    """
    simulator.env = None
    for ram_process in simulator.RAM:
        ram_process.env = None
    if simulator.bidirectional:
        for transmitter in simulator.upstream_transmitter:
            transmitter.env = None
        for transmitter in simulator.downstream_transmitter:
            transmitter.env = None
        for receiver in simulator.upstream_receiver:
            receiver.env = None
        for receiver in simulator.downstream_receiver:
            receiver.env = None
        if minimal:
            simulator.upstream_transmitter = None
            simulator.downstream_transmitter = None
            simulator.receiver = None
            simulator.model.data_rings = None
            simulator.model.control_ring = None
            simulator.model.reversed_data_rings = None
            for ram in simulator.RAM:
                ram.model = None
                ram.add_to_queue_record = None
                ram.pop_from_queue_record = None
                ram.generated_data_packet = None
    else:
        for transmitter in simulator.transmitter:
            transmitter.env = None
        for receiver in simulator.receiver:
            receiver.env = None
        if minimal:
            simulator.transmitter = None
            simulator.receiver = None
            simulator.model.data_rings = None
            simulator.model.control_ring = None
            for ram in simulator.RAM:
                ram.model = None
                ram.add_to_queue_record = None
                ram.pop_from_queue_record = None
                ram.generated_data_packet = None

    return simulator


def save_model(simulator, fname, dir=None, minimal=True):
    """
    Function to save simulation models as pickle files.

    Note that all `env` variables present in the objects are cleared before saving.

    Parameters
    ----------
    simulator : BaseSimulator or ParallelSimulator
        The simulator to be saved.
    fname : str
        The file name of the saved model.
    dir : str, optional
        The output directory of the saved model, by default ``None``, \
            corresponding to the `models` directory.
    minimal : bool, optional
        If file size is further reduced by removing transmitter and receiver objects.
    """
    if isinstance(simulator, BaseSimulator):
        simulator = clear_env(simulator, minimal=minimal)
    elif isinstance(simulator, ParallelSimulator):
        for base_simulator in simulator.simulator:
            base_simulator = clear_env(base_simulator, minimal=minimal)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if dir is None:
        load_dir = os.path.join(dir_path, '../../../', 'models')
    else:
        load_dir = dir
    os.chdir(load_dir)
    # with open(fname, 'wb') as output:
    #     pickle.dump(simulator, output)
    output = bz2.BZ2File(fname, 'w')
    pickle.dump(simulator, output)
    os.chdir(dir_path)
