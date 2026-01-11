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
    DataWord, Unknown, Source, Drain, Divider, SignedDivider, SIMD_Divider, SIMD_SignedDivider,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[tuple[DataWord, float]]], list[list[list[tuple[DataWord, float]]]]]] = [
    (
        1,
        [
            [(b'\x00', 1e-9), (b'\x01', 4e-9), (Unknown, 7e-9)],
            [(b'\x00', 2e-9), (b'\x01', 3e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (Unknown, 9e-9)]
        ],
        [
            [
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)],
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (Unknown, 7e-9)]
            ],
            [
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)],
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (Unknown, 7e-9)]
            ]
        ]
    ),
    (
        8,
        [
            [
                (cast(list[DataWord], [b'\x00', b'\x01', b'\x80', b'\xff', Unknown])[i % 5], (1 + 5 * i) * 1e-9) for i in range(5)
            ],
            [
                (cast(list[DataWord], [b'\x00', b'\x02', b'\x7f', b'\xff', Unknown])[i % 5], (1 + i) * 1e-9) for i in range(25)
            ]
        ],
        [
            [
                [
                    (b'\x00', 1e-9), (Unknown, 5e-9),
                    (b'\x00', 6e-9), (Unknown, 10e-9),
                    (b'\x00', 11e-9), (b'\x40', 12e-9), (b'\x01', 13e-9), (b'\x00', 14e-9), (Unknown, 15e-9),
                    (b'\x00', 16e-9), (b'\x7f', 17e-9), (b'\x02', 18e-9), (b'\x01', 19e-9), (Unknown, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (Unknown, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (Unknown, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (Unknown, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (Unknown, 20e-9)
                ]
            ],
            [
                [
                    (b'\x00', 1e-9), (Unknown, 5e-9),
                    (b'\x00', 6e-9), (b'\xff', 9e-9), (Unknown, 10e-9),
                    (b'\x00', 11e-9), (b'\xc0', 12e-9), (b'\xff', 13e-9), (b'\x80', 14e-9), (Unknown, 15e-9),
                    (b'\x00', 16e-9), (b'\x01', 19e-9), (Unknown, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (Unknown, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (Unknown, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (b'\x01', 14e-9), (Unknown, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (Unknown, 20e-9)
                ]
            ]
        ]
    ),
    (
        33,
        [
            [
                (
                    cast(list[DataWord], [
                        b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x01\x00\x00\x00\x00', b'\x01\xff\xff\xff\xff', Unknown
                    ])[i % 5],
                    (1 + 5 * i) * 1e-9
                ) for i in range(5)
            ],
            [
                (
                    cast(list[DataWord], [
                        b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x02', b'\x00\xff\xff\xff\xff', b'\x01\xff\xff\xff\xff', Unknown
                    ])[i % 5],
                    (1 + i) * 1e-9
                ) for i in range(25)
            ]
        ],
        [
            [
                [
                    (b'\x00\x00\x00\x00\x00', 1e-9), (Unknown, 5e-9),
                    (b'\x00\x00\x00\x00\x00', 6e-9), (Unknown, 10e-9),
                    (b'\x00\x00\x00\x00\x00', 11e-9), (b'\x00\x80\x00\x00\x00', 12e-9), (b'\x00\x00\x00\x00\x01', 13e-9), (b'\x00\x00\x00\x00\x00', 14e-9), (Unknown, 15e-9),
                    (b'\x00\x00\x00\x00\x00', 16e-9), (b'\x00\xff\xff\xff\xff', 17e-9), (b'\x00\x00\x00\x00\x02', 18e-9), (b'\x00\x00\x00\x00\x01', 19e-9), (Unknown, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (Unknown, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (Unknown, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (Unknown, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (Unknown, 20e-9)
                ]
            ],
            [
                [
                    (b'\x00\x00\x00\x00\x00', 1e-9), (Unknown, 5e-9),
                    (b'\x00\x00\x00\x00\x00', 6e-9), (b'\x01\xff\xff\xff\xff', 9e-9), (Unknown, 10e-9),
                    (b'\x00\x00\x00\x00\x00', 11e-9), (b'\x01\x80\x00\x00\x00', 12e-9), (b'\x01\xff\xff\xff\xff', 13e-9), (b'\x01\x00\x00\x00\x00', 14e-9), (Unknown, 15e-9),
                    (b'\x00\x00\x00\x00\x00', 16e-9), (b'\x00\x00\x00\x00\x01', 19e-9), (Unknown, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (Unknown, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (Unknown, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (b'\x01', 14e-9), (Unknown, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (Unknown, 20e-9)
                ]
            ]
        ]
    )
]


def test_Divider() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: Divider = Divider(w)
        dev.port_o.connect(to[0].port_i)
        dev.port_e.connect(to[1].port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po[0])
        dev.port_e.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[2][0]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_SignedDivider() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SignedDivider = SignedDivider(w)
        dev.port_o.connect(to[0].port_i)
        dev.port_e.connect(to[1].port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po[0])
        dev.port_e.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[2][1]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_Divider() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[DataWord, float]]], list[list[tuple[DataWord, float]]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf2\x80\x3e\x1b', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x01\xff\x08\x0c', 10e-9)
                ],
                [
                    (cast(list[DataWord], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                [
                    (b'\x02\x00\x01\x00', 11e-9), (b'\xf2\x00\x07\x02', 12e-9), (b'\x00\x79\x00\x07', 13e-9), (b'\x00\x00\x00\x79', 14e-9),
                    (Unknown, 15e-9)
                ],
                [
                    (b'\x01', 11e-9), (b'\x00', 12e-9),
                    (Unknown, 15e-9)
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SIMD_Divider = SIMD_Divider(w, t[1])
        dev.port_o.connect(to[0].port_i)
        dev.port_e.connect(to[1].port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po[0])
        dev.port_e.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[3]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_SignedDivider() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[DataWord, float]]], list[list[tuple[DataWord, float]]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf2\x80\x3e\x1b', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x01\xff\x08\x0c', 10e-9)
                ],
                [
                    (cast(list[DataWord], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                [
                    (b'\x02\x80\x00\x01', 11e-9), (b'\xf2\x80\x07\x02', 12e-9), (b'\xff\xfa\x00\x07', 13e-9), (b'\xff\xff\xff\xfa', 14e-9),
                    (Unknown, 15e-9)
                ],
                [
                    (b'\x01', 11e-9), (b'\x00', 13e-9),
                    (Unknown, 15e-9)
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SIMD_SignedDivider = SIMD_SignedDivider(w, t[1])
        dev.port_o.connect(to[0].port_i)
        dev.port_e.connect(to[1].port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po[0])
        dev.port_e.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[3]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS
