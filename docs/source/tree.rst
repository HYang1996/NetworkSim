.. code-block:: bash

    NetworkSim
    ├── architecture
    │   ├── base
    │   │   ├── network.py
    │   │   ├── node.py
    │   │   └── ring.py
    │   ├── setup
    │   │   └── model.py
    │   └── signal
    │       ├── control.py
    │       └── data.py
    ├── simulation
    │   ├── process
    │   │   ├── ram.py
    │   │   ├── receiver
    │   │   │   ├── base.py
    │   │   │   └── tunable.py
    │   │   └── transmitter
    │   │       ├── base.py
    │   │       └── fixed.py
    │   ├── setup
    │   │   └── simulator.py
    │   └── tools
    │       ├── clock.py
    │       └── distribution.py
    └── tests
        ├── test_packet_movement_on_ring.py
        └── test_source_traffic_generation.py




