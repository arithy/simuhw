# SimuHW: A behavioral hardware simulator provided as a Python module.
#
# Copyright (c) 2024-2026 Arihiro Yoshida. All rights reserved.
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
    'Word', 'Unknown', 'HighZ', 'Signal',
    'Probe', 'ChannelProbe', 'MemoryProbe',
    'LogicAnalyzer',
    'Simulator',
    'InputPort', 'OutputPort',
    'Device', 'Source', 'LogicLowSource', 'LogicHighSource', 'LogicUnknownSource', 'HighZSource', 'Drain',
    'Group',
    'Delay',
    'Clock',
    'WordCombiner', 'WordSplitter', 'Multiplexer', 'Demultiplexer', 'WordRetainingDemultiplexer', 'Junction', 'Distributor',
    'Channel',
    'Operator', 'UnaryOperator', 'BinaryOperator', 'TernaryOperator',
    'SIMD_Operator', 'SIMD_UnaryOperator', 'SIMD_BinaryOperator', 'SIMD_TernaryOperator',
    'Buffer', 'Inverter', 'TriStateBuffer', 'TriStateInverter',
    'ANDGate', 'ORGate', 'XORGate', 'NANDGate', 'NORGate', 'XNORGate',
    'DLatch',
    'DFlipFlop',
    'Shifter', 'LeftShifter', 'RightShifter', 'ArithmeticRightShifter', 'LeftRotator', 'RightRotator',
    'SIMD_Shifter', 'SIMD_LeftShifter', 'SIMD_RightShifter', 'SIMD_ArithmeticRightShifter', 'SIMD_LeftRotator', 'SIMD_RightRotator',
    'BitOperator', 'PopulationCounter', 'LeadingZeroCounter', 'TrailingZeroCounter', 'BitReverser',
    'SIMD_BitOperator', 'SIMD_PopulationCounter', 'SIMD_LeadingZeroCounter', 'SIMD_TrailingZeroCounter', 'SIMD_BitReverser',
    'Negator', 'SIMD_Negator',
    'Adder', 'HalfAdder', 'FullAdder', 'SIMD_Adder',
    'Subtractor', 'HalfSubtractor', 'FullSubtractor', 'SIMD_Subtractor',
    'Multiplier', 'SignedMultiplier', 'SIMD_Multiplier', 'SIMD_SignedMultiplier',
    'Divider', 'SignedDivider', 'SIMD_Divider', 'SIMD_SignedDivider',
    'Remainder', 'SignedRemainder', 'SIMD_Remainder', 'SIMD_SignedRemainder',
    'Comparator', 'SignedComparator', 'SIMD_Comparator', 'SIMD_SignedComparator',
    'IntegerConverter', 'SignedIntegerConverter', 'SIMD_IntegerConverter', 'SIMD_SignedIntegerConverter',
    'LookupTable'
]

from ._version import __version__  # noqa:F401

from ._type import Word, Unknown, HighZ, Signal
from ._analyzer import Probe, ChannelProbe, MemoryProbe, LogicAnalyzer
from ._simulator import Simulator
from ._base import InputPort, OutputPort, Device, Source, LogicLowSource, LogicHighSource, LogicUnknownSource, HighZSource, Drain
from ._group import Group
from ._delay import Delay
from ._clock import Clock
from ._branch import WordCombiner, WordSplitter, Multiplexer, Demultiplexer, WordRetainingDemultiplexer, Junction, Distributor
from ._channel import Channel
from ._operator import (
    Operator, UnaryOperator, BinaryOperator, TernaryOperator,
    SIMD_Operator, SIMD_UnaryOperator, SIMD_BinaryOperator, SIMD_TernaryOperator
)
from ._buffer import Buffer, Inverter, TriStateBuffer, TriStateInverter
from ._gate import ANDGate, ORGate, XORGate, NANDGate, NORGate, XNORGate
from ._latch import DLatch
from ._flipflop import DFlipFlop
from ._shifter import (
    Shifter, LeftShifter, RightShifter, ArithmeticRightShifter, LeftRotator, RightRotator,
    SIMD_Shifter, SIMD_LeftShifter, SIMD_RightShifter, SIMD_ArithmeticRightShifter, SIMD_LeftRotator, SIMD_RightRotator
)
from ._bit_op import (
    BitOperator, PopulationCounter, LeadingZeroCounter, TrailingZeroCounter, BitReverser,
    SIMD_BitOperator, SIMD_PopulationCounter, SIMD_LeadingZeroCounter, SIMD_TrailingZeroCounter, SIMD_BitReverser
)
from ._negator import Negator, SIMD_Negator
from ._adder import Adder, HalfAdder, FullAdder, SIMD_Adder
from ._subtractor import Subtractor, HalfSubtractor, FullSubtractor, SIMD_Subtractor
from ._multiplier import Multiplier, SignedMultiplier, SIMD_Multiplier, SIMD_SignedMultiplier
from ._divider import Divider, SignedDivider, SIMD_Divider, SIMD_SignedDivider
from ._remainder import Remainder, SignedRemainder, SIMD_Remainder, SIMD_SignedRemainder
from ._comparator import Comparator, SignedComparator, SIMD_Comparator, SIMD_SignedComparator
from ._converter import IntegerConverter, SignedIntegerConverter, SIMD_IntegerConverter, SIMD_SignedIntegerConverter
from ._lut import LookupTable
