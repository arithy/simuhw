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

from simuhw import DataWord, Unknown, Source, Drain, Buffer, Inverter, ChannelProbe, Simulator

_EPS: float = 1e-18


_test_data: list[tuple[tuple[int, int], list[list[tuple[DataWord, float]]], dict[type, list[tuple[DataWord, float]]]]] = [
    (
        (1, 1),
        [
            [(b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)]
        ],
        {
            Buffer: [
                (b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)
            ],
            Inverter: [
                (b'\x00', 1e-9), (b'\x01', 3e-9), (Unknown, 4e-9), (b'\x00', 6e-9)
            ]
        }
    ),
    (
        (8, 4),
        [
            [(b'\xfe', 1e-9), (b'\xab', 5e-9), (Unknown, 8e-9), (b'\xcd', 10e-9), (b'\x01', 12e-9)],
            [(b'\x06', 4e-9), (b'\x01', 5e-9), (Unknown, 8e-9), (b'\x1a', 9e-9), (b'\x16', 14e-9)],
            [(b'\xff', 3e-9), (b'\x00', 6e-9), (b'\xff', 7e-9), (Unknown, 8e-9), (b'\x00', 9e-9)],
            [(b'\x0e', 2e-9), (b'\x03', 3e-9), (b'\x0e', 7e-9), (Unknown, 8e-9), (b'\x01', 10e-9)]
        ],
        {
            Buffer: [
                (b'\xfe', 1e-9), (b'\xab', 5e-9), (Unknown, 8e-9), (b'\xcd', 10e-9), (b'\x01', 12e-9)
            ],
            Inverter: [
                (b'\x01', 1e-9), (b'\x54', 5e-9), (Unknown, 8e-9), (b'\x32', 10e-9), (b'\xfe', 12e-9)
            ]
        }
    ),
    (
        (33, 17),
        [
            [(b'\x00\x00\x00\x00\x00', 0e-9), (b'\x01\x55\x55\xaa\xaa', 1e-9 * (1 + i)), (b'\x01\xff\xff\xff\xff', 18e-9)]
            for i in range(17)
        ],
        {
            Buffer: [
                (b'\x00\x00\x00\x00\x00', 0e-9), (b'\x01\x55\x55\xaa\xaa', 1e-9), (b'\x01\xff\xff\xff\xff', 18e-9)
            ],
            Inverter: [
                (b'\x01\xff\xff\xff\xff', 0e-9), (b'\x00\xaa\xaa\x55\x55', 1e-9), (b'\x00\x00\x00\x00\x00', 18e-9)
            ]
        }
    )
]


def test_Buffer() -> None:
    for t in _test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1][0])
        to: Drain = Drain(w)
        dev: Buffer = Buffer(w)
        dev.port_o.connect(to.port_i)
        ti.port_o.connect(dev.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[2][Buffer]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_Inverter() -> None:
    for t in _test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1][0])
        to: Drain = Drain(w)
        dev: Inverter = Inverter(w)
        dev.port_o.connect(to.port_i)
        ti.port_o.connect(dev.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[2][Inverter]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS
