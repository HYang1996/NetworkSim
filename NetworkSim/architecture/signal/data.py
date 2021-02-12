__all__ = ["DataSignal"]
__author__ = ["Hongyi Yang"]

import random


class DataSignal:
    """
    Constructor for data signals.

    The user defines the bit length of the signal packet.

    Parameters
    ----------
    size : int, optional
        The packet size of the data signal, in bytes.
        Default is ``1500`` (12,000 bits).
    abstract : bool, optional
        The abstract mode of the data signals. If `True`, random binary packets will be generated. If `False`, \
        abstract decimal packets will be generated as a list.
    """

    def __init__(
            self,
            size=1500,
            abstract=True
    ):
        self.size = size
        self.abstract = abstract

    def generate_packet(self, seed=None):
        """
        Data packet generation.

        Parameters
        ----------
        seed : int
            Randomisation seed.

        Returns
        -------
        data_packet : str (If `self.abstract == True`)
            The data packet string in binary.
        data_packet : list (If `self.abstract == False`)
            The data packet list in decimal, containing the following:

            - `Node ID`
            - `Packet ID`

            Note that the abstract data packets are directly generated in the `RAM` class.
        """
        if self.abstract:
            raise NotImplementedError("Please generate data packets from RAM class instead to ensure that the data "
                                      "packets are labelled with a correct ID number.")
        else:
            random.seed(seed)
            # Generate all bits (8 * number of bytes)
            return bin(random.randint(0, 2 ** (8 * self.size) - 1))[2:].zfill(8 * self.size)
