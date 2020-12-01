[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/HYang1996/NetworkSim/master?filepath=examples)

# NetworkSim Package

## Workflow

1. Writing new classes and methods
    1. Update new files in the [Package Structure](#package-structure) section
    1. Include comments and docstrings in the codes
    1. Create or improve example notebooks whenever necessary
    1. Create unit tests whenever necessary and verify locally
1. Formatting
    1. Use flake8 for formatting checks
1. Documentation
    1. Use Sphinx for documentation

## Package Structure

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
    



## Usage

### Formatting

Run flake8 for formatting checks:
```python
flake8 NetworkSim/
```

### Tests

Run tests in a module:
```python
pytest test_example.py
```

Run tests in a directory:
```python
pytest example_directory/
```

Run all unit tests:
```python
pytest NetworkSim/
```

Note, if `ModuleNotFoundError: No module named 'NetworkSim'` is raised, use the alternative command followed by the test directory:
```python
python3 -m pytest
```

### Documentation

The documentation of this project is build using Sphinx.

Go to the `docs` directory:
```
cd docs
```
Run the command to build documentation files:
```
make clean html
```
View the documentation web page:
```
open build/html/index.html
```
