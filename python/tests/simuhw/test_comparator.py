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
    DataWord, Unknown, Source, Drain, Comparator, SignedComparator, SIMD_Comparator, SIMD_SignedComparator,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


def test_Comparator() -> None:
    test_data: list[tuple[int, list[list[list[tuple[DataWord, float]]]]]] = [
        (
            1,
            [
                [
                    [(b'\x00', 1e-9), (b'\x01', 4e-9), (Unknown, 7e-9)],
                    [(b'\x00', 2e-9), (b'\x01', 3e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (Unknown, 9e-9)]
                ],
                [
                    [(b'\x00', 2e-9), (b'\x01', 3e-9), (b'\x00', 4e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (Unknown, 7e-9)]
                ]
            ]
        ),
        (
            8,
            [
                [
                    [
                        (b'\x01', 1e-9), (b'\x7f', 5e-9), (b'\xfe', 9e-9), (Unknown, 13e-9)
                    ],
                    [
                        (b'\x01', 2e-9), (b'\x80', 3e-9), (b'\xfe', 4e-9),
                        (Unknown, 6e-9), (b'\x01', 7e-9), (b'\x80', 8e-9),
                        (b'\xfe', 10e-9), (b'\x01', 11e-9), (Unknown, 12e-9)
                    ]
                ],
                [
                    [
                        (b'\x00', 2e-9), (b'\xff', 3e-9),
                        (Unknown, 6e-9), (b'\x01', 7e-9), (b'\xff', 8e-9), (b'\x01', 9e-9),
                        (b'\x00', 10e-9), (b'\x01', 11e-9), (Unknown, 12e-9)
                    ]
                ]
            ]
        ),
        (
            33,
            [
                [
                    [
                        (b'\x00\x02\x00\x00\x00', 1e-9), (b'\x00\xff\xff\xff\xff', 5e-9), (b'\x01\xfc\x00\x00\x00', 9e-9), (Unknown, 13e-9)
                    ],
                    [
                        (b'\x00\x03\x00\x00\x00', 2e-9), (b'\x01\x00\x00\x00\x00', 3e-9), (b'\x01\xfd\x00\x00\x00', 4e-9),
                        (Unknown, 6e-9), (b'\x00\x03\x00\x00\x00', 7e-9), (b'\x01\x00\x00\x00\x00', 8e-9),
                        (b'\x01\xfc\x00\x00\x00', 10e-9), (b'\x00\x03\x00\x00\x00', 11e-9), (Unknown, 12e-9)
                    ]
                ],
                [
                    [
                        (b'\x01\xff\xff\xff\xff', 2e-9),
                        (Unknown, 6e-9), (b'\x00\x00\x00\x00\x01', 7e-9), (b'\x01\xff\xff\xff\xff', 8e-9), (b'\x00\x00\x00\x00\x01', 9e-9),
                        (b'\x00\x00\x00\x00\x00', 10e-9), (b'\x00\x00\x00\x00\x01', 11e-9), (Unknown, 12e-9)
                    ]
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1][0]]
        to: Drain = Drain(w)
        dev: Comparator = Comparator(w)
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[1][1][0]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SignedComparator() -> None:
    test_data: list[tuple[int, list[list[list[tuple[DataWord, float]]]]]] = [
        (
            1,
            [
                [
                    [(b'\x00', 1e-9), (b'\x01', 4e-9), (Unknown, 7e-9)],
                    [(b'\x00', 2e-9), (b'\x01', 3e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (Unknown, 9e-9)]
                ],
                [
                    [(b'\x00', 2e-9), (b'\x01', 3e-9), (b'\x00', 4e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (Unknown, 7e-9)]
                ]
            ]
        ),
        (
            8,
            [
                [
                    [
                        (b'\x01', 1e-9), (b'\x7f', 5e-9), (b'\xfe', 9e-9), (Unknown, 13e-9)
                    ],
                    [
                        (b'\x01', 2e-9), (b'\x80', 3e-9), (b'\xfe', 4e-9),
                        (Unknown, 6e-9), (b'\x01', 7e-9), (b'\x80', 8e-9),
                        (b'\xfe', 10e-9), (b'\x01', 11e-9), (Unknown, 12e-9)
                    ]
                ],
                [
                    [
                        (b'\x00', 2e-9), (b'\x01', 3e-9),
                        (Unknown, 6e-9), (b'\x01', 7e-9),
                        (b'\x00', 10e-9), (b'\xff', 11e-9), (Unknown, 12e-9)
                    ]
                ]
            ]
        ),
        (
            33,
            [
                [
                    [
                        (b'\x00\x02\x00\x00\x00', 1e-9), (b'\x00\xff\xff\xff\xff', 5e-9), (b'\x01\xfc\x00\x00\x00', 9e-9), (Unknown, 13e-9)
                    ],
                    [
                        (b'\x00\x03\x00\x00\x00', 2e-9), (b'\x01\x00\x00\x00\x00', 3e-9), (b'\x01\xfd\x00\x00\x00', 4e-9),
                        (Unknown, 6e-9), (b'\x00\x03\x00\x00\x00', 7e-9), (b'\x01\x00\x00\x00\x00', 8e-9),
                        (b'\x01\xfc\x00\x00\x00', 10e-9), (b'\x00\x03\x00\x00\x00', 11e-9), (Unknown, 12e-9)
                    ]
                ],
                [
                    [
                        (b'\x01\xff\xff\xff\xff', 2e-9), (b'\x00\x00\x00\x00\x01', 3e-9),
                        (Unknown, 6e-9), (b'\x00\x00\x00\x00\x01', 7e-9),
                        (b'\x00\x00\x00\x00\x00', 10e-9), (b'\x01\xff\xff\xff\xff', 11e-9), (Unknown, 12e-9)
                    ]
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1][0]]
        to: Drain = Drain(w)
        dev: SignedComparator = SignedComparator(w)
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[1][1][0]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_Comparator() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[DataWord, float]]], list[tuple[DataWord, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\x7f\xff\x80\x01', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x80\x01\x7f\x01', 10e-9)
                ],
                [
                    (cast(list[DataWord], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xf1\x11\x1f\x00', 11e-9), (b'\xff\x01\x01\x00', 12e-9), (b'\xff\xff\x00\x01', 13e-9), (b'\xff\xff\xff\xff', 14e-9),
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
        dev: SIMD_Comparator = SIMD_Comparator(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_SignedComparator() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[DataWord, float]]], list[tuple[DataWord, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\x7f\xff\x80\x01', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x80\x01\x7f\x01', 10e-9)
                ],
                [
                    (cast(list[DataWord], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\x1f\xff\xf1\x00', 11e-9), (b'\x01\xff\xff\x00', 12e-9), (b'\x00\x01\xff\xff', 13e-9), (b'\x00\x00\x00\x01', 14e-9),
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
        dev: SIMD_SignedComparator = SIMD_SignedComparator(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS
