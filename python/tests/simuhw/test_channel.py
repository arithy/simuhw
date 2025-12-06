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

from simuhw import Source, Drain, Channel, MultiplexChannel, ChannelProbe, Simulator

_EPS: float = 1e-18


def test_Channel() -> None:
    test_data: list[tuple[tuple[int, float, float], list[tuple[bytes | None, float]], list[tuple[bytes | None, float]]]] = [
        (
            (1, 2e-9, 1 / 3e-9),
            [(b'\x01', 1e-9), (b'\x00', 4e-9), (None, 7e-9), (b'\x01', 10e-9), (b'\x00', 11e-9), (b'\x01', 12e-9), (b'\x00', 15e-9), (b'\x00', 16e-9)],
            [(b'\x01', 6e-9), (b'\x00', 9e-9), (None, 12e-9), (b'\x01', 15e-9), (None, 16e-9), (b'\x00', 20e-9)]
        ),
        (
            (8, 2e-9, 8 / 3e-9),
            [(b'\xf1', 1e-9), (b'\xf2', 4e-9), (None, 7e-9), (b'\xf3', 10e-9), (b'\xf4', 11e-9), (b'\xf5', 12e-9), (b'\xf6', 15e-9), (b'\xf6', 16e-9)],
            [(b'\xf1', 6e-9), (b'\xf2', 9e-9), (None, 12e-9), (b'\xf3', 15e-9), (None, 16e-9), (b'\xf6', 20e-9)]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        ch: Channel = Channel(w, latency=t[0][1], throughput=t[0][2])
        ch.port_o.connect(to.port_i)
        ti.port_o.connect(ch.port_i)
        ch.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, ch])
        sim.start(show_time=True)
        assert len(po.data) == len(t[2])
        for io, o in enumerate(po.data):
            assert o[0] == t[2][io][0]
            assert abs(o[1] - t[2][io][1]) <= _EPS


def test_MultiplexChannel() -> None:
    test_data: list[tuple[tuple[int, int, float, float], list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]]] = [
        (
            (1, 1, 2e-9, 1 / 3e-9),
            [
                [(b'\x01', 1e-9), (b'\x00', 4e-9), (None, 7e-9), (b'\x01', 10e-9), (b'\x00', 11e-9), (b'\x01', 12e-9), (b'\x00', 15e-9), (b'\x00', 16e-9)]
            ],
            [
                [(b'\x01', 6e-9), (b'\x00', 9e-9), (None, 12e-9), (b'\x01', 15e-9), (None, 16e-9), (b'\x00', 20e-9)]
            ]
        ),
        (
            (8, 3, 2e-9, 8 / 3e-9),
            [
                [(b'\xf2', 4e-9), (b'\xf4', 11e-9), (b'\xf6', 15e-9), (b'\xf6', 16e-9)],
                [(b'\xf1', 1e-9), (b'\xf5', 12e-9), (b'\xf7', 18e-9)],
                [(b'\xf3', 10e-9), (b'\xf8', 21e-9)]
            ],
            [
                [(b'\xf2', 9e-9), (None, 16e-9), (b'\xf6', 20e-9)],
                [(b'\xf1', 6e-9), (None, 16e-9), (b'\xf7', 23e-9)],
                [(b'\xf3', 15e-9), (None, 16e-9), (b'\xf8', 26e-9)]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        m: int = t[0][1]
        po: list[ChannelProbe] = [ChannelProbe(f'out{i}', w) for i in range(m)]
        ti: list[Source] = [Source(w, t[1][i]) for i in range(m)]
        to: list[Drain] = [Drain(w) for _ in range(m)]
        ch: MultiplexChannel = MultiplexChannel(w, m, latency=t[0][2], throughput=t[0][3])
        for i in range(m):
            ch.ports_o[i].connect(to[i].port_i)
            ti[i].port_o.connect(ch.ports_i[i])
            ch.ports_o[i].add_probe(po[i])
        sim: Simulator = Simulator(ti + to + [ch])
        sim.start(show_time=True)
        for i in range(m):
            assert len(po[i].data) == len(t[2][i])
            for io, o in enumerate(po[i].data):
                assert o[0] == t[2][i][io][0]
                assert abs(o[1] - t[2][i][io][1]) <= _EPS
