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

from typing import cast

from simuhw import (
    Word, Unknown, HighZ, Source, Drain,
    Buffer, Inverter, TriStateBuffer, TriStateInverter,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[tuple[Word, float]]], dict[type, list[list[tuple[Word, float]]]]]] = [
    (
        1,
        [
            [(cast(list[Word], [b'\x00', b'\x01', HighZ, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            [(cast(list[Word], [b'\x00', b'\x01', HighZ, Unknown])[i % 4], (1 + 4 * i) * 1e-9) for i in range(4)]
        ],
        {
            Buffer: [
                [(cast(list[Word], [b'\x00', b'\x01', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)]
            ],
            Inverter: [
                [(cast(list[Word], [b'\x01', b'\x00', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)]
            ],
            TriStateBuffer: [
                [
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [b'\x00', b'\x01', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ],
                [
                    *((cast(list[Word], [b'\x00', b'\x01', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ]
            ],
            TriStateInverter: [
                [
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [b'\x01', b'\x00', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ],
                [
                    *((cast(list[Word], [b'\x01', b'\x00', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ]
            ]
        }
    ),
    (
        8,
        [
            [(cast(list[Word], [b'\x1a', b'\xe5', HighZ, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            [(cast(list[Word], [b'\x00', b'\x01', HighZ, Unknown])[i % 4], (1 + 4 * i) * 1e-9) for i in range(4)]
        ],
        {
            Buffer: [
                [(cast(list[Word], [b'\x1a', b'\xe5', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            ],
            Inverter: [
                [(cast(list[Word], [b'\xe5', b'\x1a', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            ],
            TriStateBuffer: [
                [
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [b'\x1a', b'\xe5', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ],
                [
                    *((cast(list[Word], [b'\x1a', b'\xe5', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ]
            ],
            TriStateInverter: [
                [
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [b'\xe5', b'\x1a', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ],
                [
                    *((cast(list[Word], [b'\xe5', b'\x1a', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ]
            ]
        }
    ),
    (
        33,
        [
            [(cast(list[Word], [b'\x01\x55\x55\xaa\xaa', b'\x00\xaa\xaa\x55\x55', HighZ, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            [(cast(list[Word], [b'\x00', b'\x01', HighZ, Unknown])[i % 4], (1 + 4 * i) * 1e-9) for i in range(4)]
        ],
        {
            Buffer: [
                [(cast(list[Word], [b'\x01\x55\x55\xaa\xaa', b'\x00\xaa\xaa\x55\x55', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            ],
            Inverter: [
                [(cast(list[Word], [b'\x00\xaa\xaa\x55\x55', b'\x01\x55\x55\xaa\xaa', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(16)],
            ],
            TriStateBuffer: [
                [
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [b'\x01\x55\x55\xaa\xaa', b'\x00\xaa\xaa\x55\x55', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ],
                [
                    *((cast(list[Word], [b'\x01\x55\x55\xaa\xaa', b'\x00\xaa\xaa\x55\x55', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ]
            ],
            TriStateInverter: [
                [
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [b'\x00\xaa\xaa\x55\x55', b'\x01\x55\x55\xaa\xaa', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ],
                [
                    *((cast(list[Word], [b'\x00\xaa\xaa\x55\x55', b'\x01\x55\x55\xaa\xaa', Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(0, 4)),
                    *((cast(list[Word], [HighZ, HighZ, HighZ, HighZ])[i % 4], (1 + i) * 1e-9) for i in range(4, 8)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(8, 12)),
                    *((cast(list[Word], [Unknown, Unknown, Unknown, Unknown])[i % 4], (1 + i) * 1e-9) for i in range(12, 16))
                ]
            ]
        }
    )
]


def test_Buffer() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1][0])
        to: Drain = Drain(w)
        dev: Buffer = Buffer(w)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        a: list[tuple[Word, float]] = t[2][Buffer][0]
        r: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
        assert len(po.signals) == len(r)
        for o, q in zip(po.signals, r):
            assert o.word == q[0]
            assert abs(o.time - q[1]) <= _EPS


def test_Inverter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1][0])
        to: Drain = Drain(w)
        dev: Inverter = Inverter(w)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        a: list[tuple[Word, float]] = t[2][Inverter][0]
        r: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
        assert len(po.signals) == len(r)
        for o, q in zip(po.signals, r):
            assert o.word == q[0]
            assert abs(o.time - q[1]) <= _EPS


def test_TriStateBuffer() -> None:
    for t in _test_data:
        w: int = t[0]
        for j in range(2):
            po: ChannelProbe = ChannelProbe('out', w)
            ti: list[Source] = [Source(u, d) for u, d in zip([w, 1], t[1])]
            to: Drain = Drain(w)
            dev: TriStateBuffer = TriStateBuffer(w) if j == 0 else TriStateBuffer(w, active_high=False)
            for i, p in enumerate([dev.port_i, dev.port_c]):
                ti[i].port_o.connect(p)
            dev.port_o.connect(to.port_i)
            dev.port_o.add_probe(po)
            sim: Simulator = Simulator([*ti, to, dev])
            sim.start(show_time=True)
            a: list[tuple[Word, float]] = t[2][TriStateBuffer][j]
            r: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
            assert len(po.signals) == len(r)
            for o, q in zip(po.signals, r):
                assert o.word == q[0]
                assert abs(o.time - q[1]) <= _EPS


def test_TriStateInverter() -> None:
    for t in _test_data:
        w: int = t[0]
        for j in range(2):
            po: ChannelProbe = ChannelProbe('out', w)
            ti: list[Source] = [Source(u, d) for u, d in zip([w, 1], t[1])]
            to: Drain = Drain(w)
            dev: TriStateInverter = TriStateInverter(w) if j == 0 else TriStateInverter(w, active_high=False)
            for i, p in enumerate([dev.port_i, dev.port_c]):
                ti[i].port_o.connect(p)
            dev.port_o.connect(to.port_i)
            dev.port_o.add_probe(po)
            sim: Simulator = Simulator([*ti, to, dev])
            sim.start(show_time=True)
            a: list[tuple[Word, float]] = t[2][TriStateInverter][j]
            r: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
            assert len(po.signals) == len(r)
            for o, q in zip(po.signals, r):
                assert o.word == q[0]
                assert abs(o.time - q[1]) <= _EPS
