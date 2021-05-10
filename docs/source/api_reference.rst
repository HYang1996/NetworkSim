.. _api_reference:

=============
API Reference
=============

.. autosummary::
    :toctree: modules/auto_generated/

.. include:: includes/api_css.rst

.. _architecture_ref:

Network Signal Configuration
============================

The :mod:`NetworkSim.architecture.signal` module contains definitions of the control and data signals used in the ring network.

.. automodule:: NetworkSim.architecture.signal
    :no-members:
    :no-inherited-members:

Signal Configuration
--------------------

.. currentmodule:: NetworkSim.architecture.signal

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    ControlSignal
    DataSignal

Network Architecture Base Configuration
=======================================

The :mod:`NetworkSim.architecture.base` module contains useful components for the configuration of the optical ring network hardware architecture.

.. automodule:: NetworkSim.architecture.base
    :no-members:
    :no-inherited-members:

Node Configuration
------------------

.. currentmodule:: NetworkSim.architecture.base.node

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Node

Network Configuration
---------------------

.. currentmodule:: NetworkSim.architecture.base.network

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Network

Ring Configuration
------------------

.. currentmodule:: NetworkSim.architecture.base.ring

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Ring

Network Architecture Setup
=======================================

The :mod:`NetworkSim.architecture.setup` module enables integration of the network components into a complete network model.

.. automodule:: NetworkSim.architecture.setup
    :no-members:
    :no-inherited-members:

Model Configuration
-------------------

.. currentmodule:: NetworkSim.architecture.setup.model

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Model

.. _simulation_ref:

Simulation Tools
================

The :mod:`NetworkSim.simulation.tools` module contains essential tools used for the simulation.

.. automodule:: NetworkSim.simulation.tools
    :no-members:
    :no-inherited-members:

Network Performance Analysis
----------------------------

.. currentmodule:: NetworkSim.simulation.tools.performance_analysis

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    get_queueing_delay
    get_service_delay
    get_transfer_delay
    get_final_batch_delay
    get_extended_run_delay
    get_overall_delay
    get_final_batch_throughput
    get_extended_run_throughput
    get_overall_throughput

Probability Distributions for Discrete Event Simulation
-------------------------------------------------------

.. currentmodule:: NetworkSim.simulation.tools.distribution

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Distribution

Synchronised Clocks
-------------------

.. currentmodule:: NetworkSim.simulation.tools.clock

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    TransmitterDataClock
    ReceiverDataClock
    ControlClock

Simulation Information
----------------------

.. currentmodule:: NetworkSim.simulation.tools.info

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Info

Simulation Summary
------------------

.. currentmodule:: NetworkSim.simulation.tools.summary

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    Summary

Simulation Results Plotting
---------------------------
Plots can also be directly generated from simulation summary.

.. currentmodule:: NetworkSim.simulation.tools.plot

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    init
    plot_latency_heatmap
    plot_latency_scatter
    plot_latency
    plot_latency_throughput
    plot_count
    plot_latency_3d
    plot_batch_throughput
    plot_analytical_simulation_latency

Simulation Model Loading and Saving
-----------------------------------

.. currentmodule:: NetworkSim.simulation.tools.load_save

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    load_model
    save_model
    clear_env

Tools used for Publication Purposes
-----------------------------------

.. currentmodule:: NetworkSim.simulation.tools.publication

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    init
    plot_delay
    plot_throughput
    plot_buffer
    plot_delay_heatmap
    plot_packet_heatmap
    plot_ook_ber
    plot_scaled_network_delay

Simulation Processes
====================

The :mod:`NetworkSim.simulation.process` module contains essential processes used for the simulation.

.. automodule:: NetworkSim.simulation.process
    :no-members:
    :no-inherited-members:

RAM Process
-----------

.. currentmodule:: NetworkSim.simulation.process.ram

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    RAM

Transmitter Process
-------------------

.. currentmodule:: NetworkSim.simulation.process.transmitter

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseTransmitter
    FT
    TT
    TT_U
    TT_D

Receiver Process
----------------

.. currentmodule:: NetworkSim.simulation.process.receiver

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseReceiver
    FR
    TR
    FR_U
    FR_D

Simulation Setup
================

The :mod:`NetworkSim.simulation.simulator` module contains a wrapper to set up all necessary processes for the simulation.

.. automodule:: NetworkSim.simulation.simulator
    :no-members:
    :no-inherited-members:

Basic Simulation Wrapper
------------------------

.. currentmodule:: NetworkSim.simulation.simulator.base

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    BaseSimulator

Parallel Simulation
-------------------

.. currentmodule:: NetworkSim.simulation.simulator.parallel

.. autosummary::
    :toctree: modules/auto_generated/
    :template: class.rst

    ParallelSimulator


SystemVerilog Integration
=========================
The :mod:`NetworkSim.system_verilog` module contains useful functions to generate relevant files used for writing and verification of the SystemVerilog modules in the project.

Receiver Module
---------------

.. currentmodule:: NetworkSim.system_verilog.receiver

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    generate_testvector

Transmitter Module
------------------

.. currentmodule:: NetworkSim.system_verilog.transmitter

.. autosummary::
    :toctree: modules/auto_generated/
    :template: function.rst

    print_delay_lut
    generate_testvector