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
    DataWord, Unknown, Source, Drain, Negator, SIMD_Negator,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


def test_Negator() -> None:
    test_data: list[tuple[int, list[tuple[DataWord, float]], list[tuple[DataWord, float]]]] = [
        (
            2,
            [
                (cast(list[DataWord], [
                    b'\x00', b'\x01', b'\x02', b'\x03', Unknown
                ])[i], (1 + i) * 1e-9) for i in range(5)
            ],
            [
                (b'\x00', 1e-9), (b'\x03', 2e-9), (b'\x02', 3e-9), (b'\x01', 4e-9), (Unknown, 5e-9)
            ]
        ),
        (
            8,
            [
                (cast(list[DataWord], [
                    b'\x00', b'\x01', b'\x05', b'\x3a', b'\x1c', b'\x80', b'\xff', Unknown
                ])[i], (1 + i) * 1e-9) for i in range(8)
            ],
            [
                (b'\x00', 1e-9), (b'\xff', 2e-9), (b'\xfb', 3e-9), (b'\xc6', 4e-9), (b'\xe4', 5e-9), (b'\x80', 6e-9), (b'\x01', 7e-9), (Unknown, 8e-9)
            ]
        ),
        (
            33,
            [
                (
                    cast(list[DataWord], [
                        b'\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x01', b'\x00\x00\x08\x00\x00', b'\x01\xb6\xf3\x8c\x29',
                        b'\x00\x02\x00\xe0\x00', b'\x01\x00\x00\x00\x00', b'\x01\xff\xff\xff\xff', Unknown
                    ])[i],
                    (1 + i) * 1e-9
                ) for i in range(8)
            ],
            [
                (b'\x00\x00\x00\x00\x00', 1e-9), (b'\x01\xff\xff\xff\xff', 2e-9), (b'\x01\xff\xf8\x00\x00', 3e-9), (b'\x00\x49\x0c\x73\xd7', 4e-9),
                (b'\x01\xfd\xff\x20\x00', 5e-9), (b'\x01\x00\x00\x00\x00', 6e-9), (b'\x00\x00\x00\x00\x01', 7e-9), (Unknown, 8e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        dev: Negator = Negator(w)
        dev.port_o.connect(to.port_i)
        ti.port_o.connect(dev.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[2]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_SIMD_Negator() -> None:
    test_data: list[tuple[list[int], list[int], list[list[tuple[DataWord, float]]], list[tuple[DataWord, float]]]] = [
        (
            [32, 2],
            [4, 8, 16, 32],
            [
                [
                    (cast(list[DataWord], [
                        b'\x01\x23\xcd\xef', b'\x08\xe1\x86\xff', b'\xff\xff\x86\xe1', b'\xff\x86\xff\xe1', Unknown
                    ])[i], 1e-9 * (1 + i)) for i in range(5)
                ],
                [
                    (cast(list[DataWord], [b'\x00', b'\x01', b'\x02', b'\x03', Unknown])[i % 5], 1e-9 * (1 + i)) for i in range(10)
                ]
            ],
            [
                (b'\x0f\xed\x43\x21', 1e-9), (b'\xf8\x1f\x7a\x01', 2e-9), (b'\x00\x01\x79\x1f', 3e-9), (b'\x00\x79\x00\x1f', 4e-9), (Unknown, 5e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        s: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([w, s], t[2])]
        to: Drain = Drain(w)
        dev: SIMD_Negator = SIMD_Negator(w, t[1])
        dev.port_o.connect(to.port_i)
        ti[0].port_o.connect(dev.port_i)
        ti[1].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS
