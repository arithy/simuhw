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

import io
import difflib

from simuhw import Unknown, HighZ, Signal, ChannelProbe, MemoryProbe, LogicAnalyzer


def test_LogicAnalyzer() -> None:
    lwd: list[int | type[Unknown | HighZ]] = [
        0x_00_00_01_00_00_00_fe_00_01,
        0x_00_40_01_00_00_40_fe_00_40,
        Unknown,
        0x_00_80_01_00_00_80_fe_00_83,
        HighZ,
        0x_01_00_01_00_01_00_fe_01_02
    ]
    lcp: list[ChannelProbe] = [ChannelProbe(f'channel_{i:02}', i) for i in [1, 2, 7, 8, 9, 31, 32, 33, 63, 64, 65]]
    lmp: list[MemoryProbe] = [MemoryProbe(f'memory_{i:02}', i) for i in [1, 2, 7, 8, 9, 31, 32, 33, 63, 64, 65]]
    la: LogicAnalyzer = LogicAnalyzer()
    for cp in lcp:
        la.add_probe(cp)
    for mp in lmp:
        la.add_probe(mp)
    for icp, cp in enumerate(lcp):
        for iwd, wd in enumerate(lwd):
            cp.append(Signal(
                (wd & ((1 << cp.width) - 1)).to_bytes((cp.width + 7) >> 3, byteorder='big') if isinstance(wd, int) else wd,
                (icp + iwd) * 1e-9
            ))
    for imp, mp in enumerate(lmp):
        for iwd, wd in enumerate(reversed(lwd)):
            mp.append(Signal((
                wd & ((1 << mp.width) - 1)).to_bytes((mp.width + 7) >> 3, byteorder='big') if isinstance(wd, int) else wd,
                (imp + iwd + 1) * 1e-9
            ))
    with io.StringIO() as out:
        la.save_as_vcd(out)
        assert '\n'.join(difflib.unified_diff(_ref_vcd().splitlines(), out.getvalue().splitlines())) == ''


def _ref_vcd() -> str:
    return '''\
$timescale 1ps $end
$var wire 1 0 channel_01 $end
$var wire 2 1 channel_02 $end
$var wire 7 2 channel_07 $end
$var wire 8 3 channel_08 $end
$var wire 9 4 channel_09 $end
$var wire 31 5 channel_31 $end
$var wire 32 6 channel_32 $end
$var wire 33 7 channel_33 $end
$var wire 63 8 channel_63 $end
$var wire 64 9 channel_64 $end
$var wire 65 10 channel_65 $end
$var reg 1 11 memory_01 $end
$var reg 2 12 memory_02 $end
$var reg 7 13 memory_07 $end
$var reg 8 14 memory_08 $end
$var reg 9 15 memory_09 $end
$var reg 31 16 memory_31 $end
$var reg 32 17 memory_32 $end
$var reg 33 18 memory_33 $end
$var reg 63 19 memory_63 $end
$var reg 64 20 memory_64 $end
$var reg 65 21 memory_65 $end
$dumpvars
bx 0
bxx 1
bxxxxxxx 2
bxxxxxxxx 3
bxxxxxxxxx 4
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 5
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 6
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 7
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 8
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 9
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 10
bx 11
bxx 12
bxxxxxxx 13
bxxxxxxxx 14
bxxxxxxxxx 15
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 16
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 17
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 18
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 19
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 20
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 21
$end
#0
b1 0
#1000
b0 0
b01 1
b0 11
#2000
bx 0
b00 1
b0000001 2
bz 11
b10 12
#3000
b1 0
bxx 1
b1000000 2
b00000001 3
b1 11
bzz 12
b0000010 13
#4000
bz 0
b11 1
bxxxxxxx 2
b01000000 3
b000000001 4
bx 11
b11 12
bzzzzzzz 13
b00000010 14
#5000
b0 0
bzz 1
b0000011 2
bxxxxxxxx 3
b001000000 4
b0000000111111100000000000000001 5
b0 11
bxx 12
b0000011 13
bzzzzzzzz 14
b100000010 15
#6000
b10 1
bzzzzzzz 2
b10000011 3
bxxxxxxxxx 4
b1000000111111100000000001000000 5
b00000000111111100000000000000001 6
b1 11
b00 12
bxxxxxxx 13
b10000011 14
bzzzzzzzzz 15
b0000000111111100000000100000010 16
#7000
b0000010 2
bzzzzzzzz 3
b010000011 4
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 5
b01000000111111100000000001000000 6
b000000000111111100000000000000001 7
b01 12
b1000000 13
bxxxxxxxx 14
b010000011 15
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 16
b00000000111111100000000100000010 17
#8000
b00000010 3
bzzzzzzzzz 4
b0000000111111100000000010000011 5
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 6
b001000000111111100000000001000000 7
b000000000000001000000000000000000000000111111100000000000000001 8
b0000001 13
b01000000 14
bxxxxxxxxx 15
b0000000111111100000000010000011 16
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 17
b100000000111111100000000100000010 18
#9000
b100000010 4
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 5
b10000000111111100000000010000011 6
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 7
b100000000000001000000000000000001000000111111100000000001000000 8
b0000000000000001000000000000000000000000111111100000000000000001 9
b00000001 14
b001000000 15
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 16
b10000000111111100000000010000011 17
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 18
b000000000000001000000000000000100000000111111100000000100000010 19
#10000
b0000000111111100000000100000010 5
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 6
b010000000111111100000000010000011 7
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 8
b0100000000000001000000000000000001000000111111100000000001000000 9
b00000000000000001000000000000000000000000111111100000000000000001 10
b000000001 15
b1000000111111100000000001000000 16
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 17
b010000000111111100000000010000011 18
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 19
b0000000000000001000000000000000100000000111111100000000100000010 20
#11000
b00000000111111100000000100000010 6
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 7
b000000000000001000000000000000010000000111111100000000010000011 8
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 9
b00100000000000001000000000000000001000000111111100000000001000000 10
b0000000111111100000000000000001 16
b01000000111111100000000001000000 17
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 18
b000000000000001000000000000000010000000111111100000000010000011 19
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 20
b10000000000000001000000000000000100000000111111100000000100000010 21
#12000
b100000000111111100000000100000010 7
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 8
b1000000000000001000000000000000010000000111111100000000010000011 9
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 10
b00000000111111100000000000000001 17
b001000000111111100000000001000000 18
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 19
b1000000000000001000000000000000010000000111111100000000010000011 20
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 21
#13000
b000000000000001000000000000000100000000111111100000000100000010 8
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 9
b01000000000000001000000000000000010000000111111100000000010000011 10
b000000000111111100000000000000001 18
b100000000000001000000000000000001000000111111100000000001000000 19
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 20
b01000000000000001000000000000000010000000111111100000000010000011 21
#14000
b0000000000000001000000000000000100000000111111100000000100000010 9
bzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz 10
b000000000000001000000000000000000000000111111100000000000000001 19
b0100000000000001000000000000000001000000111111100000000001000000 20
bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 21
#15000
b10000000000000001000000000000000100000000111111100000000100000010 10
b0000000000000001000000000000000000000000111111100000000000000001 20
b00100000000000001000000000000000001000000111111100000000001000000 21
#16000
b00000000000000001000000000000000000000000111111100000000000000001 21
#20000
'''
