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
    Source, Drain,
    LeftShifter, RightShifter, ArithmeticRightShifter, LeftRotator, RightRotator,
    SIMD_LeftShifter, SIMD_RightShifter, SIMD_ArithmeticRightShifter, SIMD_LeftRotator, SIMD_RightRotator,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


_test_data: list[tuple[int, list[list[tuple[bytes | None, float]]], dict[type, list[tuple[bytes | None, float]]]]] = [
    (
        2,
        [
            [
                ([b'\x00', b'\x01', b'\x02', b'\x03', None][i % 5], (1 + 5 * i) * 1e-9) for i in range(5)
            ],
            [
                ([b'\x00', b'\x01', b'\x02', b'\x03', None][i % 5], (1 + i) * 1e-9) for i in range(25)
            ]
        ],
        {
            LeftShifter: [
                (b'\x00', 1e-9), (None, 5e-9),
                (b'\x01', 6e-9), (b'\x02', 7e-9), (b'\x00', 8e-9), (None, 10e-9),
                (b'\x02', 11e-9), (b'\x00', 12e-9), (None, 15e-9),
                (b'\x03', 16e-9), (b'\x02', 17e-9), (b'\x00', 18e-9), (None, 20e-9)
            ],
            RightShifter: [
                (b'\x00', 1e-9), (None, 5e-9),
                (b'\x01', 6e-9), (b'\x00', 7e-9), (None, 10e-9),
                (b'\x02', 11e-9), (b'\x01', 12e-9), (b'\x00', 13e-9), (None, 15e-9),
                (b'\x03', 16e-9), (b'\x01', 17e-9), (b'\x00', 18e-9), (None, 20e-9)
            ],
            ArithmeticRightShifter: [
                (b'\x00', 1e-9), (None, 5e-9),
                (b'\x01', 6e-9), (b'\x00', 7e-9), (None, 10e-9),
                (b'\x02', 11e-9), (b'\x03', 12e-9), (None, 15e-9),
                (b'\x03', 16e-9), (None, 20e-9)
            ],
            LeftRotator: [
                (b'\x00', 1e-9), (None, 5e-9),
                (b'\x01', 6e-9), (b'\x02', 7e-9), (b'\x01', 8e-9), (b'\x02', 9e-9), (None, 10e-9),
                (b'\x02', 11e-9), (b'\x01', 12e-9), (b'\x02', 13e-9), (b'\x01', 14e-9), (None, 15e-9),
                (b'\x03', 16e-9), (None, 20e-9)
            ],
            RightRotator: [
                (b'\x00', 1e-9), (None, 5e-9),
                (b'\x01', 6e-9), (b'\x02', 7e-9), (b'\x01', 8e-9), (b'\x02', 9e-9), (None, 10e-9),
                (b'\x02', 11e-9), (b'\x01', 12e-9), (b'\x02', 13e-9), (b'\x01', 14e-9), (None, 15e-9),
                (b'\x03', 16e-9), (None, 20e-9)
            ]
        }
    ),
    (
        8,
        [
            [
                ([b'\x00', b'\x01', b'\xb9', b'\x80', b'\xff', None][i % 6], (1 + 8 * i) * 1e-9) for i in range(6)
            ],
            [
                ([b'\x00', b'\x01', b'\x02', b'\x06', b'\x07', b'\x08', b'\x09', None][i % 8], (1 + i) * 1e-9) for i in range(48)
            ]
        ],
        {
            LeftShifter: [
                (b'\x00', 1e-9), (None, 8e-9),
                (b'\x01', 9e-9), (b'\x02', 10e-9), (b'\x04', 11e-9), (b'\x40', 12e-9), (b'\x80', 13e-9), (b'\x00', 14e-9), (None, 16e-9),
                (b'\xb9', 17e-9), (b'\x72', 18e-9), (b'\xe4', 19e-9), (b'\x40', 20e-9), (b'\x80', 21e-9), (b'\x00', 22e-9), (None, 24e-9),
                (b'\x80', 25e-9), (b'\x00', 26e-9), (None, 32e-9),
                (b'\xff', 33e-9), (b'\xfe', 34e-9), (b'\xfc', 35e-9), (b'\xc0', 36e-9), (b'\x80', 37e-9), (b'\x00', 38e-9), (None, 40e-9)
            ],
            RightShifter: [
                (b'\x00', 1e-9), (None, 8e-9),
                (b'\x01', 9e-9), (b'\x00', 10e-9), (None, 16e-9),
                (b'\xb9', 17e-9), (b'\x5c', 18e-9), (b'\x2e', 19e-9), (b'\x02', 20e-9), (b'\x01', 21e-9), (b'\x00', 22e-9), (None, 24e-9),
                (b'\x80', 25e-9), (b'\x40', 26e-9), (b'\x20', 27e-9), (b'\x02', 28e-9), (b'\x01', 29e-9), (b'\x00', 30e-9), (None, 32e-9),
                (b'\xff', 33e-9), (b'\x7f', 34e-9), (b'\x3f', 35e-9), (b'\x03', 36e-9), (b'\x01', 37e-9), (b'\x00', 38e-9), (None, 40e-9)
            ],
            ArithmeticRightShifter: [
                (b'\x00', 1e-9), (None, 8e-9),
                (b'\x01', 9e-9), (b'\x00', 10e-9), (None, 16e-9),
                (b'\xb9', 17e-9), (b'\xdc', 18e-9), (b'\xee', 19e-9), (b'\xfe', 20e-9), (b'\xff', 21e-9), (None, 24e-9),
                (b'\x80', 25e-9), (b'\xc0', 26e-9), (b'\xe0', 27e-9), (b'\xfe', 28e-9), (b'\xff', 29e-9), (None, 32e-9),
                (b'\xff', 33e-9), (None, 40e-9)
            ],
            LeftRotator: [
                (b'\x00', 1e-9), (None, 8e-9),
                (b'\x01', 9e-9), (b'\x02', 10e-9), (b'\x04', 11e-9), (b'\x40', 12e-9), (b'\x80', 13e-9), (b'\x01', 14e-9), (b'\x02', 15e-9), (None, 16e-9),
                (b'\xb9', 17e-9), (b'\x73', 18e-9), (b'\xe6', 19e-9), (b'\x6e', 20e-9), (b'\xdc', 21e-9), (b'\xb9', 22e-9), (b'\x73', 23e-9), (None, 24e-9),
                (b'\x80', 25e-9), (b'\x01', 26e-9), (b'\x02', 27e-9), (b'\x20', 28e-9), (b'\x40', 29e-9), (b'\x80', 30e-9), (b'\x01', 31e-9), (None, 32e-9),
                (b'\xff', 33e-9), (None, 40e-9)
            ],
            RightRotator: [
                (b'\x00', 1e-9), (None, 8e-9),
                (b'\x01', 9e-9), (b'\x80', 10e-9), (b'\x40', 11e-9), (b'\x04', 12e-9), (b'\x02', 13e-9), (b'\x01', 14e-9), (b'\x80', 15e-9), (None, 16e-9),
                (b'\xb9', 17e-9), (b'\xdc', 18e-9), (b'\x6e', 19e-9), (b'\xe6', 20e-9), (b'\x73', 21e-9), (b'\xb9', 22e-9), (b'\xdc', 23e-9), (None, 24e-9),
                (b'\x80', 25e-9), (b'\x40', 26e-9), (b'\x20', 27e-9), (b'\x02', 28e-9), (b'\x01', 29e-9), (b'\x80', 30e-9), (b'\x40', 31e-9), (None, 32e-9),
                (b'\xff', 33e-9), (None, 40e-9)
            ]
        }
    ),
    (
        33,
        [
            [
                (
                    [b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x01\xb6\xf3\x8c\x29', b'\x01\x00\x00\x00\x00', b'\x01\xff\xff\xff\xff', None][i % 6],
                    (1 + 8 * i) * 1e-9
                ) for i in range(6)
            ],
            [
                (
                    [
                        b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x00\x00\x00\x00\x02', b'\x00\x00\x00\x00\x1f',
                        b'\x00\x00\x00\x00\x20', b'\x00\x00\x00\x00\x21', b'\x00\x00\x00\x00\x22', None
                    ][i % 8], (1 + i) * 1e-9
                ) for i in range(48)
            ]
        ],
        {
            LeftShifter: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (None, 8e-9),
                (b'\x00\x00\x00\x00\x01', 9e-9), (b'\x00\x00\x00\x00\x02', 10e-9), (b'\x00\x00\x00\x00\x04', 11e-9),
                (b'\x00\x80\x00\x00\x00', 12e-9), (b'\x01\x00\x00\x00\x00', 13e-9), (b'\x00\x00\x00\x00\x00', 14e-9), (None, 16e-9),
                (b'\x01\xb6\xf3\x8c\x29', 17e-9), (b'\x01\x6d\xe7\x18\x52', 18e-9), (b'\x00\xdb\xce\x30\xa4', 19e-9),
                (b'\x00\x80\x00\x00\x00', 20e-9), (b'\x01\x00\x00\x00\x00', 21e-9), (b'\x00\x00\x00\x00\x00', 22e-9), (None, 24e-9),
                (b'\x01\x00\x00\x00\x00', 25e-9), (b'\x00\x00\x00\x00\x00', 26e-9), (None, 32e-9),
                (b'\x01\xff\xff\xff\xff', 33e-9), (b'\x01\xff\xff\xff\xfe', 34e-9), (b'\x01\xff\xff\xff\xfc', 35e-9),
                (b'\x01\x80\x00\x00\x00', 36e-9), (b'\x01\x00\x00\x00\x00', 37e-9), (b'\x00\x00\x00\x00\x00', 38e-9), (None, 40e-9)
            ],
            RightShifter: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (None, 8e-9),
                (b'\x00\x00\x00\x00\x01', 9e-9), (b'\x00\x00\x00\x00\x00', 10e-9), (None, 16e-9),
                (b'\x01\xb6\xf3\x8c\x29', 17e-9), (b'\x00\xdb\x79\xc6\x14', 18e-9), (b'\x00\x6d\xbc\xe3\x0a', 19e-9),
                (b'\x00\x00\x00\x00\x03', 20e-9), (b'\x00\x00\x00\x00\x01', 21e-9), (b'\x00\x00\x00\x00\x00', 22e-9), (None, 24e-9),
                (b'\x01\x00\x00\x00\x00', 25e-9), (b'\x00\x80\x00\x00\x00', 26e-9), (b'\x00\x40\x00\x00\x00', 27e-9),
                (b'\x00\x00\x00\x00\x02', 28e-9), (b'\x00\x00\x00\x00\x01', 29e-9), (b'\x00\x00\x00\x00\x00', 30e-9), (None, 32e-9),
                (b'\x01\xff\xff\xff\xff', 33e-9), (b'\x00\xff\xff\xff\xff', 34e-9), (b'\x00\x7f\xff\xff\xff', 35e-9),
                (b'\x00\x00\x00\x00\x03', 36e-9), (b'\x00\x00\x00\x00\x01', 37e-9), (b'\x00\x00\x00\x00\x00', 38e-9), (None, 40e-9)
            ],
            ArithmeticRightShifter: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (None, 8e-9),
                (b'\x00\x00\x00\x00\x01', 9e-9), (b'\x00\x00\x00\x00\x00', 10e-9), (None, 16e-9),
                (b'\x01\xb6\xf3\x8c\x29', 17e-9), (b'\x01\xdb\x79\xc6\x14', 18e-9), (b'\x01\xed\xbc\xe3\x0a', 19e-9),
                (b'\x01\xff\xff\xff\xff', 20e-9), (None, 24e-9),
                (b'\x01\x00\x00\x00\x00', 25e-9), (b'\x01\x80\x00\x00\x00', 26e-9), (b'\x01\xc0\x00\x00\x00', 27e-9),
                (b'\x01\xff\xff\xff\xfe', 28e-9), (b'\x01\xff\xff\xff\xff', 29e-9), (None, 32e-9),
                (b'\x01\xff\xff\xff\xff', 33e-9), (None, 40e-9)
            ],
            LeftRotator: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (None, 8e-9),
                (b'\x00\x00\x00\x00\x01', 9e-9), (b'\x00\x00\x00\x00\x02', 10e-9), (b'\x00\x00\x00\x00\x04', 11e-9), (b'\x00\x80\x00\x00\x00', 12e-9),
                (b'\x01\x00\x00\x00\x00', 13e-9), (b'\x00\x00\x00\x00\x01', 14e-9), (b'\x00\x00\x00\x00\x02', 15e-9), (None, 16e-9),
                (b'\x01\xb6\xf3\x8c\x29', 17e-9), (b'\x01\x6d\xe7\x18\x53', 18e-9), (b'\x00\xdb\xce\x30\xa7', 19e-9), (b'\x00\xed\xbc\xe3\x0a', 20e-9),
                (b'\x01\xdb\x79\xc6\x14', 21e-9), (b'\x01\xb6\xf3\x8c\x29', 22e-9), (b'\x01\x6d\xe7\x18\x53', 23e-9), (None, 24e-9),
                (b'\x01\x00\x00\x00\x00', 25e-9), (b'\x00\x00\x00\x00\x01', 26e-9), (b'\x00\x00\x00\x00\x02', 27e-9), (b'\x00\x40\x00\x00\x00', 28e-9),
                (b'\x00\x80\x00\x00\x00', 29e-9), (b'\x01\x00\x00\x00\x00', 30e-9), (b'\x00\x00\x00\x00\x01', 31e-9), (None, 32e-9),
                (b'\x01\xff\xff\xff\xff', 33e-9), (None, 40e-9)
            ],
            RightRotator: [
                (b'\x00\x00\x00\x00\x00', 1e-9), (None, 8e-9),
                (b'\x00\x00\x00\x00\x01', 9e-9), (b'\x01\x00\x00\x00\x00', 10e-9), (b'\x00\x80\x00\x00\x00', 11e-9), (b'\x00\x00\x00\x00\x04', 12e-9),
                (b'\x00\x00\x00\x00\x02', 13e-9), (b'\x00\x00\x00\x00\x01', 14e-9), (b'\x01\x00\x00\x00\x00', 15e-9), (None, 16e-9),
                (b'\x01\xb6\xf3\x8c\x29', 17e-9), (b'\x01\xdb\x79\xc6\x14', 18e-9), (b'\x00\xed\xbc\xe3\x0a', 19e-9), (b'\x00\xdb\xce\x30\xa7', 20e-9),
                (b'\x01\x6d\xe7\x18\x53', 21e-9), (b'\x01\xb6\xf3\x8c\x29', 22e-9), (b'\x01\xdb\x79\xc6\x14', 23e-9), (None, 24e-9),
                (b'\x01\x00\x00\x00\x00', 25e-9), (b'\x00\x80\x00\x00\x00', 26e-9), (b'\x00\x40\x00\x00\x00', 27e-9), (b'\x00\x00\x00\x00\x02', 28e-9),
                (b'\x00\x00\x00\x00\x01', 29e-9), (b'\x01\x00\x00\x00\x00', 30e-9), (b'\x00\x80\x00\x00\x00', 31e-9), (None, 32e-9),
                (b'\x01\xff\xff\xff\xff', 33e-9), (None, 40e-9)
            ]
        }
    )
]


def test_LeftShifter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        dev: LeftShifter = LeftShifter(w)
        dev.port_o.connect(to.port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][LeftShifter]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_RightShifter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        dev: RightShifter = RightShifter(w)
        dev.port_o.connect(to.port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][RightShifter]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_ArithmeticRightShifter() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        dev: ArithmeticRightShifter = ArithmeticRightShifter(w)
        dev.port_o.connect(to.port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][ArithmeticRightShifter]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_LeftRotator() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        dev: LeftRotator = LeftRotator(w)
        dev.port_o.connect(to.port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][LeftRotator]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_RightRotator() -> None:
    for t in _test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        dev: RightRotator = RightRotator(w)
        dev.port_o.connect(to.port_i)
        for i in range(2):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][RightRotator]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_LeftShifter() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[tuple[bytes | None, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf6\xc7\x42\x21', 5e-9), (None, 15e-9)
                ],
                [
                    ([None, b'\x01\x23\x45\x67', b'\x08\x01\x06\x07', b'\x00\x03\x00\x0f', b'\x00\x00\x00\x11'][i % 5], 1e-9 * (10 + i)) for i in range(10)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xfc\x08\x00\x00', 11e-9), (b'\x00\x8e\x80\x80', 12e-9), (b'\xb6\x38\x80\x00', 13e-9), (b'\x84\x42\x00\x00', 14e-9),
                (None, 15e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_LeftShifter = SIMD_LeftShifter(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_RightShifter() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[tuple[bytes | None, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf6\xc7\x42\x21', 5e-9), (None, 15e-9)
                ],
                [
                    ([None, b'\x01\x23\x45\x67', b'\x08\x01\x06\x07', b'\x00\x03\x00\x0f', b'\x00\x00\x00\x11'][i % 5], 1e-9 * (10 + i)) for i in range(10)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xf3\x30\x00\x00', 11e-9), (b'\x00\x63\x01\x00', 12e-9), (b'\x1e\xd8\x00\x00', 13e-9), (b'\x00\x00\x7b\x63', 14e-9),
                (None, 15e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_RightShifter = SIMD_RightShifter(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_ArithmeticRightShifter() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[tuple[bytes | None, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf6\xc7\x42\x21', 5e-9), (None, 15e-9)
                ],
                [
                    ([None, b'\x01\x23\x45\x67', b'\x08\x01\x06\x07', b'\x00\x03\x00\x0f', b'\x00\x00\x00\x11'][i % 5], 1e-9 * (10 + i)) for i in range(10)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xf3\xf0\x00\x00', 11e-9), (b'\xff\xe3\x01\x00', 12e-9), (b'\xfe\xd8\x00\x00', 13e-9), (b'\xff\xff\xfb\x63', 14e-9),
                (None, 15e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_ArithmeticRightShifter = SIMD_ArithmeticRightShifter(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_LeftRotator() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[tuple[bytes | None, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf6\xc7\x42\x21', 5e-9), (None, 15e-9)
                ],
                [
                    ([None, b'\x01\x23\x45\x67', b'\x08\x01\x06\x07', b'\x00\x03\x00\x0f', b'\x00\x00\x00\x11'][i % 5], 1e-9 * (10 + i)) for i in range(10)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xfc\x3b\x44\x88', 11e-9), (b'\xf6\x8f\x90\x90', 12e-9), (b'\xb6\x3f\xa1\x10', 13e-9), (b'\x84\x43\xed\x8e', 14e-9),
                (None, 15e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_LeftRotator = SIMD_LeftRotator(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_RightRotator() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[bytes | None, float]]], list[tuple[bytes | None, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (b'\xf6\xc7\x42\x21', 5e-9), (None, 15e-9)
                ],
                [
                    ([None, b'\x01\x23\x45\x67', b'\x08\x01\x06\x07', b'\x00\x03\x00\x0f', b'\x00\x00\x00\x11'][i % 5], 1e-9 * (10 + i)) for i in range(10)
                ],
                [
                    ([None, b'\x00', b'\x01', b'\x02', b'\x03'][i % 5], 1e-9 * i) for i in range(20)
                ]
            ],
            [
                (b'\xf3\x3e\x41\x82', 11e-9), (b'\xf6\xe3\x09\x42', 12e-9), (b'\xfe\xd8\x84\x42', 13e-9), (b'\xa1\x10\xfb\x63', 14e-9),
                (None, 15e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_RightRotator = SIMD_RightRotator(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.ports_i[0])
        ti[1].port_o.connect(dev.ports_i[1])
        ti[2].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS
