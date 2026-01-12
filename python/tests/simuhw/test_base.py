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

from simuhw._base import combine_bits, extract_bits, to_signed_int
from simuhw import (
    Word, Unknown, HighZ,
    Source, LogicLowSource, LogicHighSource, LogicUnknownSource, HighZSource, Drain,
    ChannelProbe, Simulator
)


_test_data: list[int] = [0, 1, 2, 3, 7, 8, 9, 30, 31, 32, 33, 62, 63, 64, 65, 66]


def test_combine_bits() -> None:
    for n0 in _test_data:
        for i0 in range(-1, n0):
            k0: int = (1 << i0) if i0 >= 0 else 0
            b0: bytes = k0.to_bytes((n0 + 7) >> 3)
            for n1 in _test_data:
                for i1 in range(-1, n1):
                    k1: int = (1 << i1) if i1 >= 0 else 0
                    b1: bytes = k1.to_bytes((n1 + 7) >> 3)
                    assert combine_bits(n0, b0, n1, b1) == ((k0 << n1) | k1).to_bytes((n0 + n1 + 7) >> 3)


def test_extract_bits() -> None:
    for n in _test_data:
        for i in range(-1, n):
            k: int = (1 << i) if i >= 0 else 0
            b: bytes = k.to_bytes((n + 7) >> 3)
            for j in range(n + 1):
                for l in range(n - i):
                    assert extract_bits(n, b, j, l) == ((k >> j) & ((1 << l) - 1)).to_bytes((l + 7) >> 3)


def test_to_signed_int() -> None:
    assert to_signed_int(1, 0) == 0
    assert to_signed_int(1, 1) == -1
    assert to_signed_int(33, 0x00fffffffe) == 0xfffffffe
    assert to_signed_int(33, 0x01fffffffe) == -2


def test_Source_and_Drain() -> None:
    w: int = 10
    d: list[list[tuple[Word, float]]] = [
        [(b'\x00\x01', 1.0), (b'\x00\x80', 3.0), (b'\xab\xcd', 3.0), (b'\x00\x80', 4.0), (b'\xab\xcd', 4.0), (Unknown, 5.0), (b'\x01\x00', 4.0), (b'\x02\x00', 6.0)],
        [(b'\x00\x01', 1.0), (b'\xab\xcd', 3.0), (Unknown, 5.0), (b'\x02\x00', 6.0)]  # resulted from filtering by a probe
    ]
    po: ChannelProbe = ChannelProbe('out', w)
    ti: Source = Source(w, d[0])
    to: Drain = Drain(w)
    ti.port_o.connect(to.port_i)
    to.port_i.add_probe(po)
    sim: Simulator = Simulator([ti, to])
    sim.start(show_time=True)
    assert len(po) == len(d[1])
    for ru, rv in zip(po, d[1]):
        assert ru.word == rv[0]
        assert ru.time == rv[1]


def test_LogicLowSource() -> None:
    w: int = 10
    d: list[tuple[Word, float]] = [(b'\x00\x00', 0.0)]
    po: ChannelProbe = ChannelProbe('out', w)
    ti: Source = LogicLowSource(w)
    to: Drain = Drain(w)
    ti.port_o.connect(to.port_i)
    to.port_i.add_probe(po)
    sim: Simulator = Simulator([ti, to])
    sim.start(show_time=True)
    assert len(po) == len(d)
    for ru, rv in zip(po, d):
        assert ru.word == rv[0]
        assert ru.time == rv[1]


def test_LogicHighSource() -> None:
    w: int = 10
    d: list[tuple[Word, float]] = [(b'\x03\xff', 0.0)]
    po: ChannelProbe = ChannelProbe('out', w)
    ti: Source = LogicHighSource(w)
    to: Drain = Drain(w)
    ti.port_o.connect(to.port_i)
    to.port_i.add_probe(po)
    sim: Simulator = Simulator([ti, to])
    sim.start(show_time=True)
    assert len(po) == len(d)
    for ru, rv in zip(po, d):
        assert ru.word == rv[0]
        assert ru.time == rv[1]


def test_LogicUnknownSource() -> None:
    w: int = 10
    d: list[tuple[Word, float]] = []
    po: ChannelProbe = ChannelProbe('out', w)
    ti: Source = LogicUnknownSource(w)
    to: Drain = Drain(w)
    ti.port_o.connect(to.port_i)
    to.port_i.add_probe(po)
    sim: Simulator = Simulator([ti, to])
    sim.start(show_time=True)
    assert len(po) == len(d)
    for ru, rv in zip(po, d):
        assert ru.word == rv[0]
        assert ru.time == rv[1]


def test_HighZSource() -> None:
    w: int = 10
    d: list[tuple[Word, float]] = [(HighZ, 0.0)]
    po: ChannelProbe = ChannelProbe('out', w)
    ti: Source = HighZSource(w)
    to: Drain = Drain(w)
    ti.port_o.connect(to.port_i)
    to.port_i.add_probe(po)
    sim: Simulator = Simulator([ti, to])
    sim.start(show_time=True)
    assert len(po) == len(d)
    for ru, rv in zip(po, d):
        assert ru.word == rv[0]
        assert ru.time == rv[1]
