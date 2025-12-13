# SimuHW

## Overview

**SimuHW** is a behavioral hardware simulator provided as a Python module.

Python 3.11 or later is required.

## Installation

### Release Version

You can install the release version by the following command.

```sh
$ python -m pip install simuhw
```

### Development Version

You can install the development version by the following commands.

```sh
$ cd simuhw   # the repository root directory
$ make req
$ make dist
$ python -m pip install --no-index --find-links=./dist simuhw
```

## Usage

### Concept

- **Word**: a chunk of bits being transferred by wires.
- **Device**: a hardware element such as a wire, switching devices, and memory devices.
- **Channel**: a wire to transfer *words*.
- **Memory**: a memory device to memorize *words* associated with specific addresses.
- **Port**: an endpoint provided by a *device* to input or output *words*.
- **Probe**: an entity to record *word* values with the respective times, whenever the value of the *word* passing through a specific *port* or stored at a specific address in a *memory* changes.

### Import of Module

To use SimuHW, import `simuhw` module. An example is shown below.
```py
import simuhw as hw
```

### Simulation of Hardware Devices

1. Create instances of the derived classes of [`Device`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Device) class. As of version 0.1.0, the following device classes are available.
    
    - Utility
      - [`Source`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Source)
      - [`Drain`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Drain)
      - [`Group`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Group)
    - Clock
      - [`Clock`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Clock)
    - Channel
      - [`Channel`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Channel)
      - [`MultiplexChannel`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.MultiplexChannel)
    - Branch
      - [`DataCombiner`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DataCombiner)
     - [`DataSplitter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DataSplitter)
     - [`Arbitrator`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Arbitrator)
     - [`Multiplexer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Multiplexer)
     - [`Demultiplexer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Demultiplexer)
     - [`DataRetainDemultiplexer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DataRetainDemultiplexer)
     - [`Distributor`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Distributor)
   - Elementary Combinational Circuit
     - [`BufferGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.BufferGate)
     - [`NOTGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.NOTGate)
     - [`ANDGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.ANDGate)
     - [`ORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.ORGate)
      - [`XORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.XORGate)
      - [`NANDGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.NANDGate)
      - [`NORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.NORGate)
      - [`XNORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.XNORGate)
    - Elementary Sequential Circuit
      - [`DLatch`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DLatch)
      - [`DFlipFlop`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DFlipFlop)
    - Memory
      - [`LevelTriggeredMemory`](https://arithy.github.io/simuhw/apidoc/simuhw.memory.html#simuhw.memory.LevelTriggeredMemory)
      - [`EdgeTriggeredMemory`](https://arithy.github.io/simuhw/apidoc/simuhw.memory.html#simuhw.memory.EdgeTriggeredMemory)
    
    An example is shown below.
    
     ```py
     width: int = 16  # Word size in bits
     source: hw.Source = hw.Source(width, [
         (b'\x00\x01', 0.0e-9),
         (b'\xc1\x85', 3.0e-9),
         (b'\xd3\xbb', 6.0e-9),
         (b'\xf2\x3a', 10.0e-9)
     ])
     drain: hw.Drain = hw.Drain(width)
     ```
    
1. Connect the output ports to the input ports of the device class instances.
   An example is shown below.
   
    ```py
    source.port_o.connect(drain.port_i)
    ```
   
1. Create instances of [`ChannelProbe`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.ChannelProbe) class or [`MemoryProbe`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.MemoryProbe) class. `ChannelProbe` class instances can be added to input ports or output ports, and `MemoryProbe` class instances can be added to instances of the derived classes of `Memory` class.
   An example is shown below.
   
    ```py
    probe: hw.ChannelProbe = hw.ChannelProbe('out', width)
    ```
   
1. Add the probes to the ports or the memory.
   An example is shown below.
   
    ```py
    drain.port_i.add_probe(probe)
    ```
   
1. Create an instances of [`LogicAnalyzer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LogicAnalyzer) class.
   An example is shown below.
   
    ```py
    la: hw.LogicAnalyzer = hw.LogicAnalyzer()
    ```
   
1. Add the probes to the logic analyzer.
   An example is shown below.
   
    ```py
    la.add_probe(probe)
    ```
   
1. Create an instance of [`Simulator`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Simulator) class.
   An example is shown below.
   
    ```py
    sim: hw.Simulator = hw.Simulator([source, drain])
    ```
   
1. Start the simulation.
   An example is shown below.
    ```py
    sim.start()
    ```

1. Save the word value change timings recorded in the probes to a [VCD](https://en.wikipedia.org/wiki/Value_change_dump) file.
   An example is shown below.
   
    ```py
    with open('test.vcd', mode='w') as file:
        la.save_as_vcd(file)
    ```
   
1. View the VCD file using a waveform viewer such as [GTKWave](https://gtkwave.sourceforge.net/).

The whole source code of the example above is shown below.

```py
import simuhw as hw

width: int = 16  # Word size in bits
source: hw.Source = hw.Source(width, [
    (b'\x00\x01', 0.0e-9),
    (b'\xc1\x85', 3.0e-9),
    (b'\xd3\xbb', 6.0e-9),
    (b'\xf2\x3a', 10.0e-9)
])
drain: hw.Drain = hw.Drain(width)
source.port_o.connect(drain.port_i)
probe: hw.ChannelProbe = hw.ChannelProbe('out', width)
drain.port_i.add_probe(probe)
la: hw.LogicAnalyzer = hw.LogicAnalyzer()
la.add_probe(probe)
sim: hw.Simulator = hw.Simulator([source, drain])
sim.start()
with open('test.vcd', mode='w') as file:
    la.save_as_vcd(file)
```

This example simulates a Source device and a Drain device which are connected directly, and saves word value change timings at the input port of the Drain device to the file `test.vcd`.
