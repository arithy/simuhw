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

from simuhw import (
    Source, Drain, Adder, HalfAdder, FullAdder, SIMDAdder,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[list[tuple[bytes | None, float]]]]]] = [
    (
        1,
        [
            [
                [(b'\x00', 1e-9), (b'\x01', 4e-9), (None, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 3e-9), (None, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (None, 9e-9)]
            ],
            [
                [(b'\x00', 2e-9), (b'\x01', 3e-9), (b'\x00', 4e-9), (None, 5e-9), (b'\x01', 6e-9), (None, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (None, 5e-9), (b'\x00', 6e-9), (None, 7e-9)]
            ],
            [
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (b'\x01', 4e-9), (None, 5e-9), (b'\x00', 6e-9), (None, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 3e-9), (None, 5e-9), (b'\x01', 6e-9), (None, 7e-9)]
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
                    (b'\x01', 1e-9), (b'\x02', 5e-9), (b'\xfe', 9e-9), (None, 13e-9)
                ],
                [
                    (b'\x01', 2e-9), (b'\x02', 3e-9), (b'\xfe', 4e-9),
                    (None, 6e-9), (b'\x01', 7e-9), (b'\x02', 8e-9),
                    (b'\xfe', 10e-9), (b'\x01', 11e-9), (None, 12e-9)
                ]
            ],
            [
                [
                    (b'\x02', 2e-9), (b'\x03', 3e-9), (b'\xff', 4e-9), (b'\x00', 5e-9),
                    (None, 6e-9), (b'\x03', 7e-9), (b'\x04', 8e-9), (b'\x00', 9e-9),
                    (b'\xfc', 10e-9), (b'\xff', 11e-9), (None, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 5e-9), (None, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (b'\x00', 11e-9), (None, 12e-9)
                ]
            ],
            [
                [
                    (b'\x03', 2e-9), (b'\x04', 3e-9), (b'\x00', 4e-9), (b'\x01', 5e-9),
                    (None, 6e-9), (b'\x04', 7e-9), (b'\x05', 8e-9), (b'\x01', 9e-9),
                    (b'\xfd', 10e-9), (b'\x00', 11e-9), (None, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 4e-9), (None, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (None, 12e-9)
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
                    (b'\x00\x02\x00\x00\x00', 1e-9), (b'\x00\x04\x00\x00\x00', 5e-9), (b'\x01\xfc\x00\x00\x00', 9e-9), (None, 13e-9)
                ],
                [
                    (b'\x00\x03\xff\xff\xff', 2e-9), (b'\x00\x05\xff\xff\xff', 3e-9), (b'\x01\xfd\xff\xff\xff', 4e-9),
                    (None, 6e-9), (b'\x00\x03\xff\xff\xff', 7e-9), (b'\x00\x05\xff\xff\xff', 8e-9),
                    (b'\x01\xfd\xff\xff\xff', 10e-9), (b'\x00\x03\xff\xff\xff', 11e-9), (None, 12e-9)
                ]
            ],
            [
                [
                    (b'\x00\x05\xff\xff\xff', 2e-9), (b'\x00\x07\xff\xff\xff', 3e-9), (b'\x01\xff\xff\xff\xff', 4e-9), (b'\x00\x01\xff\xff\xff', 5e-9),
                    (None, 6e-9), (b'\x00\x07\xff\xff\xff', 7e-9), (b'\x00\x09\xff\xff\xff', 8e-9), (b'\x00\x01\xff\xff\xff', 9e-9),
                    (b'\x01\xf9\xff\xff\xff', 10e-9), (b'\x01\xff\xff\xff\xff', 11e-9), (None, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 5e-9), (None, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (b'\x00', 11e-9), (None, 12e-9)
                ]
            ],
            [
                [
                    (b'\x00\x06\x00\x00\x00', 2e-9), (b'\x00\x08\x00\x00\x00', 3e-9), (b'\x00\x00\x00\x00\x00', 4e-9), (b'\x00\x02\x00\x00\x00', 5e-9),
                    (None, 6e-9), (b'\x00\x08\x00\x00\x00', 7e-9), (b'\x00\x0a\x00\x00\x00', 8e-9), (b'\x00\x02\x00\x00\x00', 9e-9),
                    (b'\x01\xfa\x00\x00\x00', 10e-9), (b'\x00\x00\x00\x00\x00', 11e-9), (None, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 4e-9), (None, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (None, 12e-9)
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
        ar: Adder = Adder(w)
        ar.port_o.connect(to.port_i)
        for i in range(2):
            ti[i].port_o.connect(ar.ports_i[i])
        ar.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, ar])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[1][1][0]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_HalfAdder() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        pco: ChannelProbe = ChannelProbe('carry', 1)
        ti: list[Source] = [Source(w, d) for d in t[1][0]]
        to: Drain = Drain(w)
        tco: Drain = Drain(1)
        ar: HalfAdder = HalfAdder(w)
        ar.port_o.connect(to.port_i)
        ar.port_co.connect(tco.port_i)
        for i in range(2):
            ti[i].port_o.connect(ar.ports_i[i])
        ar.port_o.add_probe(po)
        ar.port_co.add_probe(pco)
        sim: Simulator = Simulator(ti + [to, tco, ar])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[1][1][0]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]
        c: list[tuple[bytes | None, float]] = t[1][1][1]
        assert len(pco.data) == len(c)
        for io, o in enumerate(pco.data):
            assert o[0] == c[io][0]
            assert o[1] == c[io][1]


def test_FullAdder() -> None:
    for t in _test_data:
        w: int = t[0]
        for j, ci in enumerate([b'\x00', b'\x01', None]):
            po: ChannelProbe = ChannelProbe('out', w)
            pco: ChannelProbe = ChannelProbe('carry', 1)
            ti: list[Source] = [Source(w, d) for d in t[1][0]]
            tci: Source = Source(1, [(ci, 0.0)])
            to: Drain = Drain(w)
            tco: Drain = Drain(1)
            ar: FullAdder = FullAdder(w)
            ar.port_o.connect(to.port_i)
            ar.port_co.connect(tco.port_i)
            for i in range(2):
                ti[i].port_o.connect(ar.ports_i[i])
            tci.port_o.connect(ar.port_ci)
            ar.port_o.add_probe(po)
            ar.port_co.add_probe(pco)
            sim: Simulator = Simulator(ti + [to, tci, tco, ar])
            sim.start(show_time=True)
            r: list[tuple[bytes | None, float]] = t[1][1 + j][0]
            assert len(po.data) == len(r)
            for io, o in enumerate(po.data):
                assert o[0] == r[io][0]
                assert o[1] == r[io][1]
            c: list[tuple[bytes | None, float]] = t[1][1 + j][1]
            assert len(pco.data) == len(c)
            for io, o in enumerate(pco.data):
                assert o[0] == c[io][0]
                assert o[1] == c[io][1]


def test_SIMDAdder() -> None:
    data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[tuple[bytes | None, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xff\xfe\x02\x01', 5e-9), (None, 15e-9)
                ],
                [
                    (b'\x02\x01\xff\xfd', 10e-9)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xf1\xff\xf1\xfe', 11e-9), (b'\x01\xff\x01\xfe', 12e-9), (b'\x02\x00\x01\xfe', 14e-9),
                (None, 15e-9)
            ]
        )
    ]
    for t in data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w if i < 2 else s, d) for i, d in enumerate(t[2])]
        to: Drain = Drain(w)
        ar: SIMDAdder = SIMDAdder(w, t[1])
        ar.port_o.connect(to.port_i)
        ti[0].port_o.connect(ar.ports_i[0])
        ti[1].port_o.connect(ar.ports_i[1])
        ti[2].port_o.connect(ar.port_s)
        ar.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, ar])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[3]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert abs(o[1] - r[io][1]) <= _EPS
