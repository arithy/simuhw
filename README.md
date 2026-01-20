# SimuHW

## Overview

**SimuHW** is a behavioral hardware simulator provided as a Python module.

Python 3.11 or later is required.

The GitHub page is [https://github.com/arithy/simuhw](https://github.com/arithy/simuhw).

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
$ make clean
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

1. Create instances of the derived classes of [`Device`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Device) class. As of version 0.3.0, the following device classes are available.
    
    - Utility
      - [`Source`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Source)
      - [`LogicLowSource`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LogicLowSource)
      - [`LogicHighSource`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LogicHighSource)
      - [`LogicUnknownSource`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LogicUnknownSource)
      - [`HighZSource`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.HighZSource)
      - [`Drain`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Drain)
      - [`Delay`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Delay)
      - [`Group`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Group)
    - Clock
      - [`Clock`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Clock)
    - Channel
      - [`Channel`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Channel)
    - Branch
      - [`WordCombiner`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.WordCombiner)
      - [`WordSplitter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.WordSplitter)
      - [`Multiplexer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Multiplexer)
      - [`Demultiplexer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Demultiplexer)
      - [`WordRetainDemultiplexer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.WordRetainDemultiplexer)
      - [`Junction`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Junction)
      - [`Distributor`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Distributor)
    - Elementary Combinational Circuit
      - [`Buffer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Buffer)
      - [`Inverter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Inverter)
      - [`TriStateBuffer`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.TriStateBuffer)
      - [`TriStateInverter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.TriStateInverter)
      - [`ANDGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.ANDGate)
      - [`ORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.ORGate)
      - [`XORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.XORGate)
      - [`NANDGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.NANDGate)
      - [`NORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.NORGate)
      - [`XNORGate`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.XNORGate)
    - Elementary Sequential Circuit
      - [`DLatch`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DLatch)
      - [`DFlipFlop`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.DFlipFlop)
    - Lookup Table
      - [`LookupTable`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LookupTable)
    - Bit Operation
      - [`LeftShifter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LeftShifter)
      - [`RightShifter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.RightShifter)
      - [`ArithmeticRightShifter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.ArithmeticRightShifter)
      - [`LeftRotator`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LeftRotator)
      - [`RightRotator`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.RightRotator)
      - [`PopulationCounter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.PopulationCounter)
      - [`LeadingZeroCounter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.LeadingZeroCounter)
      - [`TrailingZeroCounter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.TrailingZeroCounter)
      - [`BitReverser`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.BitReverser)
      - [`SIMD_LeftShifter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_LeftShifter)
      - [`SIMD_RightShifter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_RightShifter)
      - [`SIMD_ArithmeticRightShifter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_ArithmeticRightShifter)
      - [`SIMD_LeftRotator`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_LeftRotator)
      - [`SIMD_RightRotator`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_RightRotator)
      - [`SIMD_PopulationCounter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_PopulationCounter)
      - [`SIMD_LeadingZeroCounter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_LeadingZeroCounter)
      - [`SIMD_TrailingZeroCounter`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_TrailingZeroCounter)
      - [`SIMD_BitReverser`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_BitReverser)
    - Integer Arithmetic
      - [`Adder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Adder)
      - [`HalfAdder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.HalfAdder)
      - [`FullAdder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.FullAdder)
      - [`Subtractor`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Subtractor)
      - [`HalfSubtractor`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.HalfSubtractor)
      - [`FullSubtractor`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.FullSubtractor)
      - [`Multiplier`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Multiplier)
      - [`SignedMultiplier`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SignedMultiplier)
      - [`Divider`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Divider)
      - [`SignedDivider`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SignedDivider)
      - [`Remainder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.Remainder)
      - [`SignedRemainder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SignedRemainder)
      - [`SIMD_Adder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_Adder)
      - [`SIMD_Subtractor`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_Subtractor)
      - [`SIMD_Multiplier`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_Multiplier)
      - [`SIMD_SignedMultiplier`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_SignedMultiplier)
      - [`SIMD_Divider`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_Divider)
      - [`SIMD_SignedDivider`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_SignedDivider)
      - [`SIMD_Remainder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_Remainder)
      - [`SIMD_SignedRemainder`](https://arithy.github.io/simuhw/apidoc/simuhw.html#simuhw.SIMD_SignedRemainder)
    - Floating-Point Arithmetic
      > Available only if an appropriate version of [softfloatpy](https://pypi.org/project/softfloatpy/) module is found.
      - [`fp.FPNegator`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPNegator)
      - [`fp.FPAdder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPAdder)
      - [`fp.FPSubtractor`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPSubtractor)
      - [`fp.FPMultiplier`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPMultiplier)
      - [`fp.FPFusedMultiplyAdder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPFusedMultiplyAdder)
      - [`fp.FPDivider`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPDivider)
      - [`fp.FPRemainder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPRemainder)
      - [`fp.FPSquareRoot`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPSquareRoot)
      - [`fp.FPComparator`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPComparator)
      - [`fp.FPClassifier`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPClassifier)
      - [`fp.FPToIntegerRounder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPToIntegerRounder)
      - [`fp.FPToIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPToIntegerConverter)
      - [`fp.FPToSignedIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPToSignedIntegerConverter)
      - [`fp.FPFromIntegerRounder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPFromIntegerRounder)
      - [`fp.FPFromSignedIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPFromSignedIntegerConverter)
      - [`fp.FPConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.FPConverter)
      - [`fp.SIMD_FPNegator`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPNegator)
      - [`fp.SIMD_FPAdder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPAdder)
      - [`fp.SIMD_FPSubtractor`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPSubtractor)
      - [`fp.SIMD_FPMultiplier`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPMultiplier)
      - [`fp.SIMD_FPFusedMultiplyAdder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPFusedMultiplyAdder)
      - [`fp.SIMD_FPDivider`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPDivider)
      - [`fp.SIMD_FPRemainder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPRemainder)
      - [`fp.SIMD_FPSquareRoot`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPSquareRoot)
      - [`fp.SIMD_FPComparator`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPComparator)
      - [`fp.SIMD_FPClassifier`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPClassifier)
      - [`fp.SIMD_FPToIntegerRounder`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPToIntegerRounder)
      - [`fp.SIMD_FPToIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPToIntegerConverter)
      - [`fp.SIMD_FPToSignedIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPToSignedIntegerConverter)
      - [`fp.SIMD_FPFromIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPFromIntegerConverter)
      - [`fp.SIMD_FPFromSignedIntegerConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPFromSignedIntegerConverter)
      - [`fp.SIMD_FPConverter`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.html#simuhw.fp.SIMD_FPConverter)
      - [`fp.riscv.FRec7`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.riscv.html#simuhw.fp.riscv.FRec7)
      - [`fp.riscv.FRSqrt7`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.riscv.html#simuhw.fp.riscv.FRSqrt7)
      - [`fp.riscv.SIMD_FRec7`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.riscv.html#simuhw.fp.riscv.SIMD_FRec7)
      - [`fp.riscv.SIMD_FRSqrt7`](https://arithy.github.io/simuhw/apidoc/simuhw.fp.riscv.html#simuhw.fp.riscv.SIMD_FRSqrt7)
    - Arithmetic Logic Unit
      - [`alu.GenericArithmeticLogicUnit`](https://arithy.github.io/simuhw/apidoc/simuhw.alu.html#simuhw.alu.GenericArithmeticLogicUnit)
      - [`alu.FullArithmeticLogicUnit`](https://arithy.github.io/simuhw/apidoc/simuhw.alu.html#simuhw.alu.FullArithmeticLogicUnit)
      - [`alu.SIMD_FullArithmeticLogicUnit`](https://arithy.github.io/simuhw/apidoc/simuhw.alu.html#simuhw.alu.SIMD_FullArithmeticLogicUnit)
      - [`alu.ArithmeticLogicUnit74181`](https://arithy.github.io/simuhw/apidoc/simuhw.alu.html#simuhw.alu.ArithmeticLogicUnit74181)
      - [`alu.LookAheadCarryGenerator74182`](https://arithy.github.io/simuhw/apidoc/simuhw.alu.html#simuhw.alu.LookAheadCarryGenerator74182)
    - Counter
      - [`counter.SynchronousBinaryCounter74161`](https://arithy.github.io/simuhw/apidoc/simuhw.counter.html#simuhw.counter.SynchronousBinaryCounter74161)
      - [`counter.SynchronousBinaryCounter74163`](https://arithy.github.io/simuhw/apidoc/simuhw.counter.html#simuhw.counter.SynchronousBinaryCounter74163)
    - Memory
      - [`memory.LevelTriggeredMemory`](https://arithy.github.io/simuhw/apidoc/simuhw.memory.html#simuhw.memory.LevelTriggeredMemory)
      - [`memory.EdgeTriggeredMemory`](https://arithy.github.io/simuhw/apidoc/simuhw.memory.html#simuhw.memory.EdgeTriggeredMemory)
    
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
