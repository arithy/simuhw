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
    BufferGate, NOTGate, ANDGate, ORGate, XORGate, NANDGate, NORGate, XNORGate,
    ChannelProbe, Simulator
)


_test_data: list[tuple[tuple[int, int], list[list[tuple[bytes | None, float]]], dict[type, list[tuple[bytes | None, float]]]]] = [
    (
        (1, 1),
        [
            [(b'\x01', 1e-9), (b'\x00', 3e-9), (None, 4e-9), (b'\x01', 6e-9)]
        ],
        {
            BufferGate: [
                (b'\x01', 1e-9), (b'\x00', 3e-9), (None, 4e-9), (b'\x01', 6e-9)
            ],
            NOTGate: [
                (b'\x00', 1e-9), (b'\x01', 3e-9), (None, 4e-9), (b'\x00', 6e-9)
            ],
            ANDGate: [
                (b'\x01', 1e-9), (b'\x00', 3e-9), (None, 4e-9), (b'\x01', 6e-9)
            ],
            ORGate: [
                (b'\x01', 1e-9), (b'\x00', 3e-9), (None, 4e-9), (b'\x01', 6e-9)
            ],
            XORGate: [
                (b'\x01', 1e-9), (b'\x00', 3e-9), (None, 4e-9), (b'\x01', 6e-9)
            ],
            NANDGate: [
                (b'\x00', 1e-9), (b'\x01', 3e-9), (None, 4e-9), (b'\x00', 6e-9)
            ],
            NORGate: [
                (b'\x00', 1e-9), (b'\x01', 3e-9), (None, 4e-9), (b'\x00', 6e-9)
            ],
            XNORGate: [
                (b'\x00', 1e-9), (b'\x01', 3e-9), (None, 4e-9), (b'\x00', 6e-9)
            ]
        }
    ),
    (
        (8, 4),
        [
            [(b'\xfe', 1e-9), (b'\xab', 5e-9), (None, 8e-9), (b'\xcd', 10e-9), (b'\x01', 12e-9)],
            [(b'\x06', 4e-9), (b'\x01', 5e-9), (None, 8e-9), (b'\x1a', 9e-9), (b'\x16', 14e-9)],
            [(b'\xff', 3e-9), (b'\x00', 6e-9), (b'\xff', 7e-9), (None, 8e-9), (b'\x00', 9e-9)],
            [(b'\x0e', 2e-9), (b'\x03', 3e-9), (b'\x0e', 7e-9), (None, 8e-9), (b'\x01', 10e-9)]
        ],
        {
            BufferGate: [
                (b'\xfe', 1e-9), (b'\xab', 5e-9), (None, 8e-9), (b'\xcd', 10e-9), (b'\x01', 12e-9)
            ],
            NOTGate: [
                (b'\x01', 1e-9), (b'\x54', 5e-9), (None, 8e-9), (b'\x32', 10e-9), (b'\xfe', 12e-9)
            ],
            ANDGate: [
                (b'\x02', 4e-9), (b'\x01', 5e-9), (b'\x00', 6e-9), (None, 8e-9), (b'\x00', 10e-9)
            ],
            ORGate: [
                (b'\xff', 4e-9), (b'\xab', 6e-9), (b'\xff', 7e-9), (None, 8e-9),
                (b'\xdf', 10e-9), (b'\x1b', 12e-9), (b'\x17', 14e-9)
            ],
            XORGate: [
                (b'\x04', 4e-9), (b'\x56', 5e-9), (b'\xa9', 6e-9), (b'\x5b', 7e-9), (None, 8e-9),
                (b'\xd6', 10e-9), (b'\x1a', 12e-9), (b'\x16', 14e-9)
            ],
            NANDGate: [
                (b'\xfd', 4e-9), (b'\xfe', 5e-9), (b'\xff', 6e-9), (None, 8e-9), (b'\xff', 10e-9)
            ],
            NORGate: [
                (b'\x00', 4e-9), (b'\x54', 6e-9), (b'\x00', 7e-9), (None, 8e-9),
                (b'\x20', 10e-9), (b'\xe4', 12e-9), (b'\xe8', 14e-9)
            ],
            XNORGate: [
                (b'\xfb', 4e-9), (b'\xa9', 5e-9), (b'\x56', 6e-9), (b'\xa4', 7e-9), (None, 8e-9),
                (b'\x29', 10e-9), (b'\xe5', 12e-9), (b'\xe9', 14e-9)
            ]
        }
    )
]


def test_BufferGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1][0])
        to: Drain = Drain(w)
        gt: BufferGate = BufferGate(w)
        gt.port_o.connect(to.port_i)
        ti.port_o.connect(gt.port_i)
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][BufferGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_NOTGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1][0])
        to: Drain = Drain(w)
        gt: NOTGate = NOTGate(w)
        gt.port_o.connect(to.port_i)
        ti.port_o.connect(gt.port_i)
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][NOTGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_ANDGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        n: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        gt: ANDGate = ANDGate(w, ninputs=n)
        gt.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(gt.ports_i[i])
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][ANDGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_ORGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        n: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        gt: ORGate = ORGate(w, ninputs=n)
        gt.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(gt.ports_i[i])
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][ORGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_XORGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        n: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        gt: XORGate = XORGate(w, ninputs=n)
        gt.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(gt.ports_i[i])
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][XORGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_NANDGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        n: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        gt: NANDGate = NANDGate(w, ninputs=n)
        gt.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(gt.ports_i[i])
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][NANDGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_NORGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        n: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        gt: NORGate = NORGate(w, ninputs=n)
        gt.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(gt.ports_i[i])
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][NORGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]


def test_XNORGate() -> None:
    for t in _test_data:
        w: int = t[0][0]
        n: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(w, d) for d in t[1]]
        to: Drain = Drain(w)
        gt: XNORGate = XNORGate(w, ninputs=n)
        gt.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(gt.ports_i[i])
        gt.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, gt])
        sim.start(show_time=True)
        r: list[tuple[bytes | None, float]] = t[2][XNORGate]
        assert len(po.data) == len(r)
        for io, o in enumerate(po.data):
            assert o[0] == r[io][0]
            assert o[1] == r[io][1]
