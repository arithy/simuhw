# SimuHW: A behavioral hardware simulator provided as a Python module.
#
# Copyright (c) 2024-2025 Arihiro Yoshida. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__all__ = [
    'LogicAnalyzer',
    'Probe', 'ChannelProbe', 'MemoryProbe',
    'Simulator',
    'InputPort', 'OutputPort',
    'Device', 'Source', 'Drain',
    'Group',
    'Clock',
    'BufferGate', 'NOTGate', 'ANDGate', 'ORGate', 'XORGate', 'NANDGate', 'NORGate', 'XNORGate',
    'DataCombiner', 'DataSplitter', 'Arbitrator', 'Multiplexer', 'Demultiplexer', 'DataRetainingDemultiplexer', 'Distributor',
    'Channel', 'MultiplexChannel',
    'DLatch',
    'DFlipFlop'
]

from ._version import __version__  # noqa:F401

from ._analyzer import Probe, ChannelProbe, MemoryProbe, LogicAnalyzer
from ._simulator import Simulator
from ._base import InputPort, OutputPort, Device, Source, Drain
from ._group import Group
from ._clock import Clock
from ._gate import BufferGate, NOTGate, ANDGate, ORGate, XORGate, NANDGate, NORGate, XNORGate
from ._branch import DataCombiner, DataSplitter, Arbitrator, Multiplexer, Demultiplexer, DataRetainingDemultiplexer, Distributor
from ._channel import Channel, MultiplexChannel
from ._latch import DLatch
from ._flipflop import DFlipFlop
