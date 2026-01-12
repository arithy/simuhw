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
    Word, Unknown, Source, Drain,
    PopulationCounter, LeadingZeroCounter, TrailingZeroCounter, BitReverser,
    SIMD_PopulationCounter, SIMD_LeadingZeroCounter, SIMD_TrailingZeroCounter, SIMD_BitReverser,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[tuple[Word, float]], dict[type, list[tuple[Word, float]]]]] = [
    (
        2,
        [
            (cast(list[Word], [
                b'\x00', b'\x01', b'\x02', b'\x03', Unknown
            ])[i], (1 + i) * 1e-9) for i in range(5)
        ],
        {
            PopulationCounter: [
                (b'\x00', 1e-9), (b'\x01', 2e-9), (b'\x02', 4e-9), (Unknown, 5e-9)
            ],
            LeadingZeroCounter: [
                (b'\x02', 1e-9), (b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 5e-9)
            ],
            TrailingZeroCounter: [
                (b'\x02', 1e-9), (b'\x00', 2e-9), (b'\x01', 3e-9), (b'\x00', 4e-9), (Unknown, 5e-9)
            ],
            BitReverser: [
                (b'\x00', 1e-9), (b'\x02', 2e-9), (b'\x01', 3e-9), (b'\x03', 4e-9), (Unknown, 5e-9)
            ]
        }
    ),
    (
        8,
        [
            (cast(list[Word], [
                b'\x00', b'\x01', b'\x05', b'\x3a', b'\x1c', b'\x80', b'\xff', Unknown
            ])[i], (1 + i) * 1e-9) for i in range(8)
        ],
        {
            PopulationCounter: [
                (b'\x00', 1e-9), (b'\x01', 2e-9), (b'\x02', 3e-9), (b'\x04', 4e-9), (b'\x03', 5e-9), (b'\x01', 6e-9), (b'\x08', 7e-9), (Unknown, 8e-9)
            ],
            LeadingZeroCounter: [
                (b'\x08', 1e-9), (b'\x07', 2e-9), (b'\x05', 3e-9), (b'\x02', 4e-9), (b'\x03', 5e-9), (b'\x00', 6e-9), (Unknown, 8e-9)
            ],
            TrailingZeroCounter: [
                (b'\x08', 1e-9), (b'\x00', 2e-9), (b'\x01', 4e-9), (b'\x02', 5e-9), (b'\x07', 6e-9), (b'\x00', 7e-9), (Unknown, 8e-9)
            ],
            BitReverser: [
                (b'\x00', 1e-9), (b'\x80', 2e-9), (b'\xa0', 3e-9), (b'\x5c', 4e-9), (b'\x38', 5e-9), (b'\x01', 6e-9), (b'\xff', 7e-9), (Unknown, 8e-9)
            ]
        }
    ),
    (
        33,
        [
            (
                cast(list[Word], [
                    b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x00\x00\x08\x00\x00', b'\x01\xb6\xf3\x8c\x29',
                    b'\x00\x02\x00\xe0\x00', b'\x01\x00\x00\x00\x00', b'\x01\xff\xff\xff\xff', Unknown
                ])[i],
                (1 + i) * 1e-9
            ) for i in range(8)
        ],
        {
            PopulationCounter: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (b'\x00\x00\x00\x00\x01', 2e-9), (b'\x00\x00\x00\x00\x12', 4e-9),
                (b'\x00\x00\x00\x00\x04', 5e-9), (b'\x00\x00\x00\x00\x01', 6e-9), (b'\x00\x00\x00\x00\x21', 7e-9), (Unknown, 8e-9)
            ],
            LeadingZeroCounter: [
                (b'\x00\x00\x00\x00\x21', 1e-9), (b'\x00\x00\x00\x00\x20', 2e-9), (b'\x00\x00\x00\x00\x0d', 3e-9), (b'\x00\x00\x00\x00\x00', 4e-9),
                (b'\x00\x00\x00\x00\x07', 5e-9), (b'\x00\x00\x00\x00\x00', 6e-9), (Unknown, 8e-9)
            ],
            TrailingZeroCounter: [
                (b'\x00\x00\x00\x00\x21', 1e-9), (b'\x00\x00\x00\x00\x00', 2e-9), (b'\x00\x00\x00\x00\x13', 3e-9), (b'\x00\x00\x00\x00\x00', 4e-9),
                (b'\x00\x00\x00\x00\x0d', 5e-9), (b'\x00\x00\x00\x00\x20', 6e-9), (b'\x00\x00\x00\x00\x00', 7e-9), (Unknown, 8e-9)
            ],
            BitReverser: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (b'\x01\x00\x00\x00\x00', 2e-9), (b'\x00\x00\x00\x20\x00', 3e-9), (b'\x01\x28\x63\x9e\xdb', 4e-9),
                (b'\x00\x00\x0e\x00\x80', 5e-9), (b'\x00\x00\x00\x00\x01', 6e-9), (b'\x01\xff\xff\xff\xff', 7e-9), (Unknown, 8e-9)
            ]
        }
    )
]


def test_PopulationCounter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        dev: PopulationCounter = PopulationCounter(w)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[2][PopulationCounter]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_LeadingZeroCounter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        dev: LeadingZeroCounter = LeadingZeroCounter(w)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[2][LeadingZeroCounter]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_TrailingZeroCounter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        dev: TrailingZeroCounter = TrailingZeroCounter(w)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[2][TrailingZeroCounter]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_BitReverser() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        dev: BitReverser = BitReverser(w)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[2][BitReverser]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_PopulationCounter() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[tuple[Word, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (cast(list[Word], [
                        b'\x01\x23\x45\x67', b'\x08\xe1\x86\xff', b'\xff\xff\x86\xe1', b'\xff\x86\xff\xe1', Unknown
                    ])[i], 1e-9 * (1 + i)) for i in range(5)
                ],
                [
                    (cast(list[Word], [
                        b'\x00', b'\x01', b'\x02', b'\x03', Unknown
                    ])[i % 5], 1e-9 * (1 + i)) for i in range(10)
                ]
            ],
            [
                (b'\x01\x12\x12\x23', 1e-9), (b'\x01\x04\x03\x08', 2e-9), (b'\x00\x10\x00\x07', 3e-9), (b'\x00\x00\x00\x17', 4e-9), (Unknown, 5e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_PopulationCounter = SIMD_PopulationCounter(w, t[1])
        for i, p in enumerate([dev.port_i, dev.port_s]):
            ti[i].port_o.connect(p)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_LeadingZeroCounter() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[tuple[Word, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (cast(list[Word], [
                        b'\x01\x23\x45\x9f', b'\x08\x01\x8e\x00', b'\x00\x03\x00\x00', b'\x00\x00\x00\x11', Unknown
                    ])[i], 1e-9 * (1 + i)) for i in range(5)
                ],
                [
                    (cast(list[Word], [
                        b'\x00', b'\x01', b'\x02', b'\x03', Unknown
                    ])[i % 5], 1e-9 * (1 + i)) for i in range(10)
                ]
            ],
            [
                (b'\x43\x22\x11\x00', 1e-9), (b'\x04\x07\x00\x08', 2e-9), (b'\x00\x0e\x00\x10', 3e-9), (b'\x00\x00\x00\x1b', 4e-9), (Unknown, 5e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_LeadingZeroCounter = SIMD_LeadingZeroCounter(w, t[1])
        for i, p in enumerate([dev.port_i, dev.port_s]):
            ti[i].port_o.connect(p)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_TrailingZeroCounter() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[tuple[Word, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (cast(list[Word], [
                        b'\x08\x4c\x2a\x9f', b'\x10\x80\x71\x00', b'\xc0\x00\x00\x00', b'\x88\x00\x00\x00', Unknown
                    ])[i], 1e-9 * (1 + i)) for i in range(5)
                ],
                [
                    (cast(list[Word], [
                        b'\x00', b'\x01', b'\x02', b'\x03', Unknown
                    ])[i % 5], 1e-9 * (1 + i)) for i in range(10)
                ]
            ],
            [
                (b'\x43\x22\x11\x00', 1e-9), (b'\x04\x07\x00\x08', 2e-9), (b'\x00\x0e\x00\x10', 3e-9), (b'\x00\x00\x00\x1b', 4e-9), (Unknown, 5e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_TrailingZeroCounter = SIMD_TrailingZeroCounter(w, t[1])
        for i, p in enumerate([dev.port_i, dev.port_s]):
            ti[i].port_o.connect(p)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_BitReverser() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[tuple[Word, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (cast(list[Word], [
                        b'\x01\x23\x45\x67', b'\x01\x23\x45\x67', b'\x01\x23\x45\x67', b'\x01\x23\x45\x67', Unknown
                    ])[i], 1e-9 * (1 + i)) for i in range(5)
                ],
                [
                    (cast(list[Word], [
                        b'\x00', b'\x01', b'\x02', b'\x03', Unknown
                    ])[i % 5], 1e-9 * (1 + i)) for i in range(10)
                ]
            ],
            [
                (b'\x08\x4c\x2a\x6e', 1e-9), (b'\x80\xc4\xa2\xe6', 2e-9), (b'\xc4\x80\xe6\xa2', 3e-9), (b'\xe6\xa2\xc4\x80', 4e-9), (Unknown, 5e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_BitReverser = SIMD_BitReverser(w, t[1])
        for i, p in enumerate([dev.port_i, dev.port_s]):
            ti[i].port_o.connect(p)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS
