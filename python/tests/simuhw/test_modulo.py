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
    Source, Drain, Modulo, SignedModulo, SIMDModulo, SIMDSignedModulo,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[tuple[bytes | None, float]]], list[list[list[tuple[bytes | None, float]]]]]] = [
    (
        1,
        [
            [(b'\x00', 1e-9), (b'\x01', 4e-9), (None, 7e-9)],
            [(b'\x00', 2e-9), (b'\x01', 3e-9), (None, 5e-9), (b'\x00', 6e-9), (b'\x01', 8e-9), (None, 9e-9)]
        ],
        [
            [
                [(b'\x00', 2e-9), (None, 5e-9), (b'\x00', 6e-9), (None, 7e-9)],
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (None, 5e-9), (b'\x01', 6e-9), (None, 7e-9)]
            ],
            [
                [(b'\x00', 2e-9), (None, 5e-9), (b'\x00', 6e-9), (None, 7e-9)],
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (None, 5e-9), (b'\x01', 6e-9), (None, 7e-9)]
            ]
        ]
    ),
    (
        8,
        [
            [
                ([b'\x00', b'\x01', b'\x80', b'\xff', None][i % 5], (1 + 5 * i) * 1e-9) for i in range(5)
            ],
            [
                ([b'\x00', b'\x02', b'\x7f', b'\xff', None][i % 5], (1 + i) * 1e-9) for i in range(25)
            ]
        ],
        [
            [
                [
                    (b'\x00', 1e-9), (None, 5e-9),
                    (b'\x00', 6e-9), (b'\x01', 7e-9), (None, 10e-9),
                    (b'\x00', 11e-9), (b'\x01', 13e-9), (b'\x80', 14e-9), (None, 15e-9),
                    (b'\x00', 16e-9), (b'\x01', 17e-9), (b'\x00', 19e-9), (None, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (None, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (None, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (None, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (None, 20e-9)
                ]
            ],
            [
                [
                    (b'\x00', 1e-9), (None, 5e-9),
                    (b'\x00', 6e-9), (b'\x01', 7e-9), (b'\x00', 9e-9), (None, 10e-9),
                    (b'\x00', 11e-9), (b'\xff', 13e-9), (b'\x00', 14e-9), (None, 15e-9),
                    (b'\x00', 16e-9), (b'\xff', 17e-9), (b'\x00', 19e-9), (None, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (None, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (None, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (None, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (None, 20e-9)
                ]
            ]
        ]
    ),
    (
        33,
        [
            [
                (
                    [b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x01\x00\x00\x00\x00', b'\x01\xff\xff\xff\xff', None][i % 5],
                    (1 + 5 * i) * 1e-9
                ) for i in range(5)
            ],
            [
                (
                    [b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x02', b'\x00\xff\xff\xff\xff', b'\x01\xff\xff\xff\xff', None][i % 5],
                    (1 + i) * 1e-9
                ) for i in range(25)
            ]
        ],
        [
            [
                [
                    (b'\x00\x00\x00\x00\x00', 1e-9), (None, 5e-9),
                    (b'\x00\x00\x00\x00\x00', 6e-9), (b'\x00\x00\x00\x00\x01', 7e-9), (None, 10e-9),
                    (b'\x00\x00\x00\x00\x00', 11e-9), (b'\x00\x00\x00\x00\x01', 13e-9), (b'\x01\x00\x00\x00\x00', 14e-9), (None, 15e-9),
                    (b'\x00\x00\x00\x00\x00', 16e-9), (b'\x00\x00\x00\x00\x01', 17e-9), (b'\x00\x00\x00\x00\x00', 19e-9), (None, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (None, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (None, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (None, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (None, 20e-9)
                ]
            ],
            [
                [
                    (b'\x00\x00\x00\x00\x00', 1e-9), (None, 5e-9),
                    (b'\x00\x00\x00\x00\x00', 6e-9), (b'\x00\x00\x00\x00\x01', 7e-9), (b'\x00\x00\x00\x00\x00', 9e-9), (None, 10e-9),
                    (b'\x00\x00\x00\x00\x00', 11e-9), (b'\x01\xff\xff\xff\xff', 13e-9), (b'\x00\x00\x00\x00\x00', 14e-9), (None, 15e-9),
                    (b'\x00\x00\x00\x00\x00', 16e-9), (b'\x01\xff\xff\xff\xff', 17e-9), (b'\x00\x00\x00\x00\x00', 19e-9), (None, 20e-9)
                ],
                [
                    (b'\x01', 1e-9), (b'\x00', 2e-9), (None, 5e-9),
                    (b'\x01', 6e-9), (b'\x00', 7e-9), (None, 10e-9),
                    (b'\x01', 11e-9), (b'\x00', 12e-9), (None, 15e-9),
                    (b'\x01', 16e-9), (b'\x00', 17e-9), (None, 20e-9)
                ]
            ]
        ]
    )
]


def test_Modulo() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: Modulo = Modulo(w)
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


def test_SignedModulo() -> None:
    for t in _test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', 1)]
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SignedModulo = SignedModulo(w)
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


def test_SIMDModulo() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]]] = [
        (
            [32, 2, 8],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf2\x80\x3e\x1b', 5e-9), (None, 15e-9)
                ],
                [
                    (b'\x01\xff\x08\x0c', 10e-9)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                [
                    (b'\x00\x80\x06\x0b', 11e-9), (b'\x00\x80\x06\x03', 12e-9), (b'\x00\xf9\x05\xc7', 13e-9), (b'\x00\xf5\x70\x6f', 14e-9),
                    (None, 15e-9)
                ],
                [
                    (b'\x8a', 11e-9), (b'\x00', 12e-9),
                    (None, 15e-9)
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        e: int = t[0][2]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', e)]
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: list[Drain] = [Drain(w), Drain(e)]
        dev: SIMDModulo = SIMDModulo(w, t[1])
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


def test_SIMDSignedModulo() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]]] = [
        (
            [32, 2, 8],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf2\x80\x3e\x1b', 5e-9), (None, 15e-9)
                ],
                [
                    (b'\x01\xff\x08\x0c', 10e-9)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                [
                    (b'\x00\x00\x0e\x0f', 11e-9), (b'\x00\x00\x06\x03', 12e-9), (b'\xfe\x7a\x05\xc7', 13e-9), (b'\xfe\x7a\x6e\x63', 14e-9),
                    (None, 15e-9)
                ],
                [
                    (b'\x8a', 11e-9), (b'\x00', 12e-9),
                    (None, 15e-9)
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        e: int = t[0][2]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('overflow', e)]
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: list[Drain] = [Drain(w), Drain(e)]
        dev: SIMDSignedModulo = SIMDSignedModulo(w, t[1])
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
