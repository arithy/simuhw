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
    Multiplier, SignedMultiplier, SIMD_Multiplier, SIMD_SignedMultiplier,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[tuple[Word, float]]], list[list[list[tuple[Word, float]]]]]] = [
    (
        1,
        [
            [(b'\x00', 1e-9), (b'\x01', 4e-9), (Unknown, 7e-9)],
            [(b'\x00', 2e-9), (b'\x01', 3e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (Unknown, 9e-9)]
        ],
        [
            [
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)],
                [(b'\x00', 2e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)]
            ],
            [
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)],
                [(b'\x00', 2e-9), (b'\x01', 4e-9), (Unknown, 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9)]
            ]
        ]
    ),
    (
        8,
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
                [
                    (b'\x01', 2e-9), (b'\x02', 3e-9), (b'\xfe', 4e-9), (b'\xfc', 5e-9),
                    (Unknown, 6e-9), (b'\x02', 7e-9), (b'\x04', 8e-9), (b'\xfc', 9e-9),
                    (b'\x04', 10e-9), (b'\xfe', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (b'\x01', 5e-9), (Unknown, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (b'\x00', 11e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [
                    (b'\x01', 2e-9), (b'\x02', 3e-9), (b'\xfe', 4e-9), (b'\xfc', 5e-9),
                    (Unknown, 6e-9), (b'\x02', 7e-9), (b'\x04', 8e-9), (b'\xfc', 9e-9),
                    (b'\x04', 10e-9), (b'\xfe', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x00', 2e-9), (Unknown, 6e-9), (b'\x00', 7e-9), (Unknown, 12e-9)
                ]
            ]
        ]
    ),
    (
        33,
        [
            [
                (b'\x00\x00\x02\xff\xfc', 1e-9), (b'\x00\x00\x00\x08\x00', 5e-9), (b'\x01\xff\xfc\x00\x00', 9e-9), (Unknown, 13e-9)
            ],
            [
                (b'\x00\x00\x03\xff\xfc', 2e-9), (b'\x00\x00\x05\xff\xfa', 3e-9), (b'\x01\xff\xff\xf1\xff', 4e-9),
                (Unknown, 6e-9), (b'\x00\x00\x03\xff\xfc', 7e-9), (b'\x00\x00\x05\xff\xfa', 8e-9),
                (b'\x01\xff\xff\xf1\xff', 10e-9), (b'\x00\x00\x03\xff\xfc', 11e-9), (Unknown, 12e-9)
            ]
        ],
        [
            [
                [
                    (b'\x01\xff\xe4\x00\x10', 2e-9), (b'\x01\xff\xd6\x00\x18', 3e-9), (b'\x01\xd5\xfd\x38\x04', 4e-9), (b'\x01\xff\x8f\xf8\x00', 5e-9),
                    (Unknown, 6e-9), (b'\x00\x1f\xff\xe0\x00', 7e-9), (b'\x00\x2f\xff\xd0\x00', 8e-9), (b'\x00\x00\x18\x00\x00', 9e-9),
                    (b'\x00\x38\x04\x00\x00', 10e-9), (b'\x00\x00\x10\x00\x00', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x01', 2e-9), (Unknown, 6e-9), (b'\x00', 7e-9), (b'\x01', 9e-9), (Unknown, 12e-9)
                ]
            ],
            [
                [
                    (b'\x01\xff\xe4\x00\x10', 2e-9), (b'\x01\xff\xd6\x00\x18', 3e-9), (b'\x01\xd5\xfd\x38\x04', 4e-9), (b'\x01\xff\x8f\xf8\x00', 5e-9),
                    (Unknown, 6e-9), (b'\x00\x1f\xff\xe0\x00', 7e-9), (b'\x00\x2f\xff\xd0\x00', 8e-9), (b'\x00\x00\x18\x00\x00', 9e-9),
                    (b'\x00\x38\x04\x00\x00', 10e-9), (b'\x00\x00\x10\x00\x00', 11e-9), (Unknown, 12e-9)
                ],
                [
                    (b'\x01', 2e-9), (b'\x00', 4e-9), (Unknown, 6e-9), (b'\x00', 7e-9),
                    (b'\x01', 9e-9), (b'\x00', 10e-9), (b'\x01', 11e-9), (Unknown, 12e-9)
                ]
            ]
        ]
    )
]


def test_Multiplier() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: Multiplier = Multiplier(w)
        for i, p in enumerate(dev.ports_i):
            ti[i].port_o.connect(p)
        for i, q in enumerate([dev.port_o, dev.port_e]):
            q.connect(to[i].port_i)
            q.add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for ro, rp in zip(po, t[2][0]):
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS


def test_SignedMultiplier() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SignedMultiplier = SignedMultiplier(w)
        for i, p in enumerate(dev.ports_i):
            ti[i].port_o.connect(p)
        for i, q in enumerate([dev.port_o, dev.port_e]):
            q.connect(to[i].port_i)
            q.add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for ro, rp in zip(po, t[2][1]):
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_Multiplier() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf2\x54\x13\x3e', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x01\x02\x02\x01', 10e-9)
                ],
                [
                    (cast(list[Word], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                [
                    (b'\x02\x08\x06\x0e', 11e-9), (b'\xf2\xa8\x26\x3e', 12e-9), (b'\x38\xa8\x8f\x3e', 13e-9), (b'\xfe\xf6\x8f\x3e', 14e-9),
                    (Unknown, 15e-9)
                ],
                [
                    (b'\x00', 11e-9), (b'\x01', 13e-9),
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
        dev: SIMD_Multiplier = SIMD_Multiplier(w, t[1])
        for i, p in enumerate([*dev.ports_i, dev.port_s]):
            ti[i].port_o.connect(p)
        for i, q in enumerate([dev.port_o, dev.port_e]):
            q.connect(to[i].port_i)
            q.add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for ro, rp in zip(po, t[3]):
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_SignedMultiplier() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf2\xd4\x13\x3e', 5e-9), (Unknown, 15e-9)
                ],
                [
                    (b'\x01\x02\x03\x02', 10e-9)
                ],
                [
                    (cast(list[Word], [Unknown, b'\x00', b'\x01', b'\x02', b'\x03'])[i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                [
                    (b'\x02\x08\x09\x0c', 11e-9), (b'\xf2\xa8\x39\x7c', 12e-9), (b'\xb9\xa8\xe0\x7c', 13e-9), (b'\xc6\x5d\xe0\x7c', 14e-9),
                    (Unknown, 15e-9)
                ],
                [
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (b'\x01', 13e-9),
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
        dev: SIMD_SignedMultiplier = SIMD_SignedMultiplier(w, t[1])
        for i, p in enumerate([*dev.ports_i, dev.port_s]):
            ti[i].port_o.connect(p)
        for i, q in enumerate([dev.port_o, dev.port_e]):
            q.connect(to[i].port_i)
            q.add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for ro, rp in zip(po, t[3]):
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS
