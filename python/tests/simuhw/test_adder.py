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
    Word, Unknown, Source, Drain, Adder, HalfAdder, FullAdder, SIMD_Adder,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[list[tuple[Word, float]]]]]] = [
    (
        1,
        [
            [
                [(b'\x00', 1e-9), (b'\x01', 4e-9), (Unknown, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 3e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (Unknown, 9e-9)]
            ],
            [
                [(b'\x00', 2e-9), (b'\x01', 3e-9), (b'\x00', 4e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (Unknown, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)]
            ],
            [
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 3e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (Unknown, 7e-9)]
            ],
            [
                [], []
            ]
        ]
    ),
    (
        8,
        [
            [
                [
                    (b'\x01', 1e-9), (b'\x02', 5e-9), (b'\xfe', 9e-9), (Unknown, 13e-9)
                ],
                [
                    (b'\x01', 2e-9), (b'\x02', 3e-9), (b'\xfe', 4e-9),
                    (Unknown, 6e-9), (b'\x01', 7e-9), (b'\x02', 8e-9),
                    (b'\xfe', 10e-9), (b'\x01', 11e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [
                    (b'\x02', 2e-9), (b'\x03', 3e-9), (b'\xff', 4e-9), (b'\x00', 5e-9),
                    (Unknown, 6e-9), (b'\x03', 7e-9), (b'\x04', 8e-9), (b'\x00', 9e-9),
                    (b'\xfc', 10e-9), (b'\xff', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 5e-9), (Unknown, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (b'\x00', 11e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [
                    (b'\x03', 2e-9), (b'\x04', 3e-9), (b'\x00', 4e-9), (b'\x01', 5e-9),
                    (Unknown, 6e-9), (b'\x04', 7e-9), (b'\x05', 8e-9), (b'\x01', 9e-9),
                    (b'\xfd', 10e-9), (b'\x00', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [], []
            ]
        ]
    ),
    (
        33,
        [
            [
                [
                    (b'\x00\x02\x00\x00\x00', 1e-9), (b'\x00\x04\x00\x00\x00', 5e-9), (b'\x01\xfc\x00\x00\x00', 9e-9), (Unknown, 13e-9)
                ],
                [
                    (b'\x00\x03\xff\xff\xff', 2e-9), (b'\x00\x05\xff\xff\xff', 3e-9), (b'\x01\xfd\xff\xff\xff', 4e-9),
                    (Unknown, 6e-9), (b'\x00\x03\xff\xff\xff', 7e-9), (b'\x00\x05\xff\xff\xff', 8e-9),
                    (b'\x01\xfd\xff\xff\xff', 10e-9), (b'\x00\x03\xff\xff\xff', 11e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [
                    (b'\x00\x05\xff\xff\xff', 2e-9), (b'\x00\x07\xff\xff\xff', 3e-9), (b'\x01\xff\xff\xff\xff', 4e-9), (b'\x00\x01\xff\xff\xff', 5e-9),
                    (Unknown, 6e-9), (b'\x00\x07\xff\xff\xff', 7e-9), (b'\x00\x09\xff\xff\xff', 8e-9), (b'\x00\x01\xff\xff\xff', 9e-9),
                    (b'\x01\xf9\xff\xff\xff', 10e-9), (b'\x01\xff\xff\xff\xff', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 5e-9), (Unknown, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (b'\x00', 11e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [
                    (b'\x00\x06\x00\x00\x00', 2e-9), (b'\x00\x08\x00\x00\x00', 3e-9), (b'\x00\x00\x00\x00\x00', 4e-9), (b'\x00\x02\x00\x00\x00', 5e-9),
                    (Unknown, 6e-9), (b'\x00\x08\x00\x00\x00', 7e-9), (b'\x00\x0a\x00\x00\x00', 8e-9), (b'\x00\x02\x00\x00\x00', 9e-9),
                    (b'\x01\xfa\x00\x00\x00', 10e-9), (b'\x00\x00\x00\x00\x00', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [], []
            ]
        ]
    )
]


def test_Adder() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1][0]]
        to: Drain = Drain(w)
        dev: Adder = Adder(w)
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[1][1][0]
        assert len(po) == len(r)
        for o, q in zip(po, r):
            assert o.word == q[0]
            assert abs(o.time - q[1]) <= _EPS


def test_HalfAdder() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('carry', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1][0]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: HalfAdder = HalfAdder(w)
        dev.port_o.connect(to[0].port_i)
        dev.port_co.connect(to[1].port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        dev.port_o.add_probe(po[0])
        dev.port_co.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[1][1]):
            assert len(p) == len(r)
            for o, q in zip(p, r):
                assert o.word == q[0]
                assert abs(o.time - q[1]) <= _EPS


def test_FullAdder() -> None:
    for t in _test_data:
        w: int = t[0]
        for j, ci in enumerate([b'\x00', b'\x01', Unknown]):
            po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('carry', 1)]
            ti: list[Source] = [Source(u, d) for u, d in zip([w, w, 1], [*t[1][0], cast(list[tuple[Word, float]], [(ci, 0.0)])])]
            to: list[Drain] = [Drain(w), Drain(1)]
            dev: FullAdder = FullAdder(w)
            dev.port_o.connect(to[0].port_i)
            dev.port_co.connect(to[1].port_i)
            ti[0].port_o.connect(dev.ports_i[0])
            ti[1].port_o.connect(dev.ports_i[1])
            ti[2].port_o.connect(dev.port_ci)
            dev.port_o.add_probe(po[0])
            dev.port_co.add_probe(po[1])
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, t[1][1 + j]):
                assert len(p) == len(r)
                for o, q in zip(p, r):
                    assert o.word == q[0]
                    assert abs(o.time - q[1]) <= _EPS


def test_SIMD_Adder() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[tuple[Word, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xff\xfe\x02\x01', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x02\x01\xff\xfd', 10e-9)
                ],
                [
                    (cast(list[Word], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xf1\xff\xf1\xfe', 11e-9), (b'\x01\xff\x01\xfe', 12e-9), (b'\x02\x00\x01\xfe', 14e-9),
                (Unknown, 15e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_Adder = SIMD_Adder(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for o, q in zip(po, r):
            assert o.word == q[0]
            assert abs(o.time - q[1]) <= _EPS
