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
from functools import reduce

from simuhw import (
    Word, Unknown, Source, Drain,
    IntegerConverter, SignedIntegerConverter, SIMD_IntegerConverter, SIMD_SignedIntegerConverter,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


def test_IntegerConverter() -> None:
    test_data: list[tuple[int, int, list[tuple[Word, float]], list[tuple[Word, float]]]] = [
        (
            7, 33,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x00', b'\x01', b'\x3e', b'\x3f',
                    b'\x40', b'\x41', b'\x7e', b'\x7f',
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x00\x00\x00\x00\x3e', b'\x00\x00\x00\x00\x3f',
                    b'\x00\x00\x00\x00\x40', b'\x00\x00\x00\x00\x41', b'\x00\x00\x00\x00\x7e', b'\x00\x00\x00\x00\x7f',
                    Unknown
                ]))
            ]
        ),
        (
            33, 7,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x01\xff\xff\xff\x80', b'\x01\xff\xff\xff\x81', b'\x01\xff\xff\xff\xbe', b'\x01\xff\xff\xff\xbf',
                    b'\x01\xff\xff\xff\xc0', b'\x01\xff\xff\xff\xc1', b'\x01\xff\xff\xff\xfe', b'\x01\xff\xff\xff\xff',
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x00', b'\x01', b'\x3e', b'\x3f',
                    b'\x40', b'\x41', b'\x7e', b'\x7f',
                    Unknown
                ]))
            ]
        )
    ]
    for t in test_data:
        wi: int = t[0]
        wo: int = t[1]
        po: ChannelProbe = ChannelProbe('out', wo)
        ti: Source = Source(wi, t[2])
        to: Drain = Drain(wo)
        dev: IntegerConverter = IntegerConverter(wi, wo)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SignedIntegerConverter() -> None:
    test_data: list[tuple[int, int, list[tuple[Word, float]], list[tuple[Word, float]]]] = [
        (
            7, 33,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x00', b'\x01', b'\x3e', b'\x3f',
                    b'\x40', b'\x41', b'\x7e', b'\x7f',
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x00\x00\x00\x00\x3e', b'\x00\x00\x00\x00\x3f',
                    b'\x01\xff\xff\xff\xc0', b'\x01\xff\xff\xff\xc1', b'\x01\xff\xff\xff\xfe', b'\x01\xff\xff\xff\xff',
                    Unknown
                ]))
            ]
        ),
        (
            33, 7,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x01\xff\xff\xff\x80', b'\x01\xff\xff\xff\x81', b'\x01\xff\xff\xff\xbe', b'\x01\xff\xff\xff\xbf',
                    b'\x00\x00\x00\x00\x40', b'\x00\x00\x00\x00\x41', b'\x00\x00\x00\x00\x7e', b'\x00\x00\x00\x00\x7f',
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    b'\x00', b'\x01', b'\x3e', b'\x3f',
                    b'\x40', b'\x41', b'\x7e', b'\x7f',
                    Unknown
                ]))
            ]
        )
    ]
    for t in test_data:
        wi: int = t[0]
        wo: int = t[1]
        po: ChannelProbe = ChannelProbe('out', wo)
        ti: Source = Source(wi, t[2])
        to: Drain = Drain(wo)
        dev: SignedIntegerConverter = SignedIntegerConverter(wi, wo)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[3]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_IntegerConverter() -> None:
    test_data: list[tuple[int, int, int, list[tuple[Word, float]], list[tuple[Word, float]]]] = [
        (
            4, 7, 9,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x00', b'\x01', b'\x3e', b'\x3f'])),
                        0
                    ).to_bytes(4),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x40', b'\x41', b'\x7e', b'\x7f'])),
                        0
                    ).to_bytes(4),
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x00\x00', b'\x00\x01', b'\x00\x3e', b'\x00\x3f'])),
                        0
                    ).to_bytes(5),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x00\x40', b'\x00\x41', b'\x00\x7e', b'\x00\x7f'])),
                        0
                    ).to_bytes(5),
                    Unknown
                ]))
            ]
        ),
        (
            4, 9, 7,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x01\x80', b'\x01\x81', b'\x01\xbe', b'\x01\xbf'])),
                        0
                    ).to_bytes(5),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x01\xc0', b'\x01\xc1', b'\x01\xfe', b'\x01\xff'])),
                        0
                    ).to_bytes(5),
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x00', b'\x01', b'\x3e', b'\x3f'])),
                        0
                    ).to_bytes(4),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x40', b'\x41', b'\x7e', b'\x7f'])),
                        0
                    ).to_bytes(4),
                    Unknown
                ]))
            ]
        )
    ]
    for t in test_data:
        m: int = t[0]
        wi: int = t[1]
        wo: int = t[2]
        po: ChannelProbe = ChannelProbe('out', wo * m)
        ti: Source = Source(wi * m, t[3])
        to: Drain = Drain(wo * m)
        dev: SIMD_IntegerConverter = SIMD_IntegerConverter(m, wi, wo)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[4]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_SignedIntegerConverter() -> None:
    test_data: list[tuple[int, int, int, list[tuple[Word, float]], list[tuple[Word, float]]]] = [
        (
            4, 7, 9,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x00', b'\x01', b'\x3e', b'\x3f'])),
                        0
                    ).to_bytes(4),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x40', b'\x41', b'\x7e', b'\x7f'])),
                        0
                    ).to_bytes(4),
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x00\x00', b'\x00\x01', b'\x00\x3e', b'\x00\x3f'])),
                        0
                    ).to_bytes(5),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x01\xc0', b'\x01\xc1', b'\x01\xfe', b'\x01\xff'])),
                        0
                    ).to_bytes(5),
                    Unknown
                ]))
            ]
        ),
        (
            4, 9, 7,
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x01\x80', b'\x01\x81', b'\x01\xbe', b'\x01\xbf'])),
                        0
                    ).to_bytes(5),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (9 * i) for i, d in enumerate([b'\x00\x40', b'\x00\x41', b'\x00\x7e', b'\x00\x7f'])),
                        0
                    ).to_bytes(5),
                    Unknown
                ]))
            ],
            [
                (d, (1 + i) * 1e-9) for i, d in enumerate(cast(list[Word], [
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x00', b'\x01', b'\x3e', b'\x3f'])),
                        0
                    ).to_bytes(4),
                    reduce(
                        lambda x, y: x | y,
                        (int.from_bytes(d) << (7 * i) for i, d in enumerate([b'\x40', b'\x41', b'\x7e', b'\x7f'])),
                        0
                    ).to_bytes(4),
                    Unknown
                ]))
            ]
        )
    ]
    for t in test_data:
        m: int = t[0]
        wi: int = t[1]
        wo: int = t[2]
        po: ChannelProbe = ChannelProbe('out', wo * m)
        ti: Source = Source(wi * m, t[3])
        to: Drain = Drain(wo * m)
        dev: SIMD_SignedIntegerConverter = SIMD_SignedIntegerConverter(m, wi, wo)
        ti.port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[4]
        assert len(po) == len(r)
        for ru, rv in zip(po, r):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS
