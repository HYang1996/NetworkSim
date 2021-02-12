__author__ = ['Hongyi Yang']
__all__ = [
    'print_delay_lut'
]

from NetworkSim.simulation.simulator.base import BaseSimulator


def print_delay_lut(simulator=None):
    """
    Print delay LUT

    Generate a default simulator and print transmitter delay LUT.
    """
    if simulator is None:
        simulator = BaseSimulator(until=10000)
        simulator.initialise()
    delay = simulator.transmitter[0].tuning_delay
    for i in range(100):
        for j in range(100):
            print(
                "14'b" + str(bin(i)[2:].zfill(7)) + str(bin(j)[2:].zfill(7)) + ":",
                "delay <= 8'b" + str(bin(int(delay[i, j]))[2:].zfill(8)) + ";",
                "// curr:", i, "dest:", j, "delay:", int(delay[i, j])
            )
