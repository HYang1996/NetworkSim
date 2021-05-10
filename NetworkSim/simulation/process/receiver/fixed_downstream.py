__all__ = ["FR_D"]
__author__ = ["Hongyi Yang"]

from NetworkSim.simulation.process.receiver.fixed import FR


class FR_D(FR):
    """
    Fixed receiver simulator corresponding to downstream transmitters.

    Parameters
    ----------
    env : simpy Environment
        The simulation environment.
    receiver_id : int
        The receiver ID.
    model : Model, optional
        The network model used for the simulation.
        Default is ``Model()``.

    Attributes
    ----------
    received_data_packet_df : pandas DataFrame
        A DataFrame keeping the information of the received data packets, containing the columns:

        - `Timestamp`
        - `Raw Packet`
        - `Source ID`
    """

    def __init__(
            self,
            env,
            until,
            receiver_id,
            simulator,
            model=None
    ):
        super().__init__(
            env=env,
            until=until,
            receiver_id=receiver_id,
            simulator=simulator,
            model=model
        )
