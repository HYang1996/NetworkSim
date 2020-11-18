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
    """

    def __init__(
            self,
            size=1500
    ):
        self.size = size

    def generate_packet(self, seed=None):
        """
        Data packet generation.

        Parameters
        ----------
        seed : int
            Randomisation seed.

        Returns
        -------
        data_packet : str
            The data packet string in binary.
        """
        random.seed(seed)
        # Generate all bits (8 * number of bytes)
        return bin(random.randint(0, 2 ** (8 * self.size) - 1))[2:].zfill(8 * self.size)
