__all__ = ["Network"]
__author__ = ["Hongyi Yang"]

import pandas as pd


class Network:
    """
    Constructor of the network architecture

    Parameters
    ----------
    length : float, optional
        The length of the ring in meters. Default is ``120``.
    num_nodes : int, optional
        The number of nodes in the network. Default is ``100``.
    direction: int, optional
        Direction of travel of the signals (``1`` or ``-1``).
        Default is ``1``, indicating a positive direction.

    Attributes
    ----------
    interval_length : float
        The interval length between two neighbouring nodes.
    """

    def __init__(
            self,
            length=120,
            num_nodes=100,
            direction=1
    ):
        self.length = length
        self.num_nodes = num_nodes
        self.direction = direction
        self.interval_length = self.get_interval()

    def get_interval(self):
        """
        Obtain the interval distance between the consecutive two nodes.

        Returns
        -------
        interval : float
            The interval length in meters.
        """
        return self.length / self.num_nodes

    # Get distance between the start and end node
    def get_distance(self, start, end):
        """
        Obtain the interval between each node in meters.

        Parameters
        ----------
        start : int
            The start node ID.
        end : int
            The end node ID.

        Returns
        -------
        distance : float
            The calculated distance between the two nodes in meters.
        """
        # Catch input errors
        if start < 0 or end < 0 or start > self.num_nodes - 1 or end > self.num_nodes - 1:
            raise ValueError('The input start or end node must be within the range of 0 to ' + str(self.num_nodes - 1))
        # Swap start and end if the ring operates in reversed direction
        if self.direction == -1:
            start, end = end, start
        # Calculate distance
        if start < end:
            distance = (end - start) * self.interval_length
        else:
            distance = (self.num_nodes + end - start) * self.interval_length
        return distance

    def summary(self):
        """
        Obtain a summary of the network.

        Returns
        -------
        summary : pandas DataFrame
            A summary DataFrame containing the columns:

            - `Network Length (m)`
            - `Number of Nodes`
            - `Interval Length (m)`
        """
        summary = {
            'Network Length (m)': [self.length],
            'Number of Nodes': [self.num_nodes],
            'Interval Length (m)': [self.interval_length]
        }
        return pd.DataFrame(data=summary)
