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

from simuhw import (
    DataWord, HighZ, Unknown, Source, Drain,
    DataCombiner, DataSplitter, Multiplexer, Demultiplexer, DataRetainingDemultiplexer, Distributor,
    ChannelProbe, Simulator
)

_EPS: float = 1e-18


def test_DataCombiner() -> None:
    test_data: list[tuple[list[int], list[list[tuple[DataWord, float]]], list[tuple[DataWord, float]]]] = [
        (
            [1],
            [
                [(b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)]
            ],
            [(b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)]
        ),
        (
            [8, 3, 17, 4],
            [
                [(b'\xfe', 1e-9), (b'\x01', 5e-9), (b'\xfe', 10e-9), (Unknown, 11e-9), (b'\x01', 12e-9)],
                [(b'\x06', 4e-9), (b'\x01', 5e-9), (b'\x06', 14e-9)],
                [(b'\x01\xff\xfe', 3e-9), (b'\x00\x00\x01', 6e-9), (b'\x01\xff\xfe', 7e-9), (b'\x00\x00\x01', 9e-9)],
                [(b'\x0e', 2e-9), (b'\x01', 3e-9), (b'\x0e', 7e-9), (b'\x01', 10e-9)]
            ],
            [
                (b'\xfe\xdf\xff\xe1', 4e-9), (b'\x01\x3f\xff\xe1', 5e-9), (b'\x01\x20\x00\x11', 6e-9), (b'\x01\x3f\xff\xee', 7e-9),
                (b'\x01\x20\x00\x1e', 9e-9), (b'\xfe\x20\x00\x11', 10e-9), (Unknown, 11e-9), (b'\x01\x20\x00\x11', 12e-9), (b'\x01\xc0\x00\x11', 14e-9)
            ]
        )
    ]
    for t in test_data:
        po: ChannelProbe = ChannelProbe('out', sum(t[0]))
        ti: list[Source] = [Source(t[0][i], t[1][i]) for i in range(len(t[0]))]
        to: Drain = Drain(sum(t[0]))
        dev: DataCombiner = DataCombiner(t[0])
        dev.port_o.connect(to.port_i)
        for i in range(len(t[0])):
            ti[i].port_o.connect(dev.ports_i[i])
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[2]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_DataSplitter() -> None:
    test_data: list[tuple[list[int], list[tuple[DataWord, float]], list[list[tuple[DataWord, float]]]]] = [
        (
            [1],
            [(b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)],
            [
                [(b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)]
            ]
        ),
        (
            [8, 3, 17, 4],
            [
                (b'\xfe\xdf\xff\xe1', 4e-9), (b'\x01\x3f\xff\xe1', 5e-9), (b'\x01\x20\x00\x11', 6e-9), (b'\x01\x3f\xff\xee', 7e-9),
                (b'\x01\x20\x00\x1e', 9e-9), (b'\xfe\x20\x00\x11', 10e-9), (Unknown, 11e-9), (b'\x01\x20\x00\x11', 12e-9), (b'\x01\xc0\x00\x11', 14e-9)
            ],
            [
                [
                    (b'\xfe', 4e-9), (b'\x01', 5e-9), (b'\xfe', 10e-9), (Unknown, 11e-9), (b'\x01', 12e-9)
                ],
                [
                    (b'\x06', 4e-9), (b'\x01', 5e-9), (Unknown, 11e-9), (b'\x01', 12e-9), (b'\x06', 14e-9)
                ],
                [
                    (b'\x01\xff\xfe', 4e-9), (b'\x00\x00\x01', 6e-9), (b'\x01\xff\xfe', 7e-9),
                    (b'\x00\x00\x01', 9e-9), (Unknown, 11e-9), (b'\x00\x00\x01', 12e-9)
                ],
                [
                    (b'\x01', 4e-9), (b'\x0e', 7e-9), (b'\x01', 10e-9), (Unknown, 11e-9), (b'\x01', 12e-9)
                ]
            ]
        )
    ]
    for t in test_data:
        po: list[ChannelProbe] = [ChannelProbe(f'out{i}', t[0][i]) for i in range(len(t[0]))]
        ti: Source = Source(sum(t[0]), t[1])
        to: list[Drain] = [Drain(t[0][i]) for i in range(len(t[0]))]
        dev: DataSplitter = DataSplitter(t[0])
        ti.port_o.connect(dev.port_i)
        for i in range(len(t[0])):
            dev.ports_o[i].connect(to[i].port_i)
            dev.ports_o[i].add_probe(po[i])
        sim: Simulator = Simulator([ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[2]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_Multiplexer() -> None:
    test_data: list[tuple[int, list[list[tuple[DataWord, float]]], list[tuple[DataWord, float]], list[tuple[DataWord, float]]]] = [
        (
            1,
            [
                [(b'\x01', 1e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9)]
            ],
            [(b'\x01', 2e-9), (Unknown, 5e-9), (b'\x01', 6e-9), (b'\x00', 7e-9)],
            [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 6e-9), (Unknown, 7e-9)]
        ),
        (
            8,
            [
                [(b'\xfe', 1e-9), (b'\xf1', 5e-9), (b'\xfe', 10e-9), (Unknown, 11e-9), (b'\xf1', 12e-9)],
                [(b'\x06', 4e-9), (b'\x01', 5e-9), (b'\x06', 14e-9)],
                [(b'\x41', 3e-9), (b'\x40', 6e-9), (b'\x41', 7e-9), (b'\x40', 9e-9)],
                [(b'\x1e', 2e-9), (b'\x11', 3e-9), (b'\x1e', 7e-9), (b'\x11', 10e-9)]
            ],
            [
                (b'\x01', 2e-9), (Unknown, 6e-9), (b'\x08', 8e-9), (b'\x04', 9e-9), (b'\x00', 13e-9), (b'\x02', 14e-9)
            ],
            [
                (b'\xfe', 2e-9), (b'\xf1', 5e-9), (Unknown, 6e-9), (b'\x1e', 8e-9), (b'\x40', 9e-9), (Unknown, 13e-9), (b'\x06', 14e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        n: int = len(t[1])
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([*([w] * n), n], [*t[1], t[2]])]
        to: Drain = Drain(w)
        dev: Multiplexer = Multiplexer(w, n)
        dev.port_o.connect(to.port_i)
        for i in range(n):
            ti[i].port_o.connect(dev.ports_i[i])
        ti[n].port_o.connect(dev.port_s)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS


def test_Demultiplexer() -> None:
    test_data: list[tuple[tuple[int, DataWord], list[tuple[DataWord, float]], list[tuple[DataWord, float]], list[list[tuple[DataWord, float]]]]] = [
        (
            (1, b'\x01'),
            [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9), (b'\x00', 9e-9), (Unknown, 10e-9), (b'\x01', 11e-9)],
            [(b'\x01', 1e-9), (Unknown, 6e-9), (b'\x01', 8e-9), (b'\x00', 9e-9)],
            [
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 5e-9), (Unknown, 6e-9), (b'\x01', 9e-9)]
            ]
        ),
        (
            (8, b'\xcd'),
            [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9), (Unknown, 10e-9), (b'\xa1', 11e-9), (b'\x8b', 12e-9)],
            [(b'\x01', 1e-9), (Unknown, 4e-9), (b'\x08', 6e-9), (b'\x04', 7e-9), (b'\x03', 8e-9), (b'\x00', 9e-9), (b'\x0a', 12e-9)],
            [
                [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xcd', 6e-9), (b'\xd2', 8e-9), (b'\xcd', 9e-9)],
                [(b'\xcd', 1e-9), (Unknown, 4e-9), (b'\xcd', 6e-9), (b'\xd2', 8e-9), (b'\xcd', 9e-9), (b'\x8b', 12e-9)],
                [(b'\xcd', 1e-9), (Unknown, 4e-9), (b'\xcd', 6e-9), (b'\xd2', 7e-9), (b'\xcd', 8e-9)],
                [(b'\xcd', 1e-9), (Unknown, 4e-9), (b'\xd2', 6e-9), (b'\xcd', 7e-9), (b'\x8b', 12e-9)]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        d: DataWord = t[0][1]
        n: int = len(t[3])
        po: list[ChannelProbe] = [ChannelProbe(f'out{i}', w) for i in range(n)]
        ti: list[Source] = [Source(w, t[1]), Source(n, t[2])]
        to: list[Drain] = [Drain(w) for _ in range(n)]
        dev: Demultiplexer = Demultiplexer(w, n, deselected=d)
        ti[0].port_o.connect(dev.port_i)
        ti[1].port_o.connect(dev.port_s)
        for i in range(n):
            dev.ports_o[i].connect(to[i].port_i)
            dev.ports_o[i].add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[3]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_DataRetainingDemultiplexer() -> None:
    test_data: list[tuple[int, list[tuple[DataWord, float]], list[tuple[DataWord, float]], list[list[tuple[DataWord, float]]]]] = [
        (
            1,
            [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9), (b'\x00', 8e-9), (Unknown, 10e-9), (b'\x01', 11e-9)],
            [(b'\x01', 1e-9), (Unknown, 6e-9), (b'\x01', 8e-9), (b'\x00', 9e-9)],
            [
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 5e-9), (Unknown, 6e-9), (b'\x00', 8e-9)]
            ]
        ),
        (
            8,
            [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9), (Unknown, 10e-9), (b'\xa1', 11e-9), (b'\x8b', 12e-9)],
            [(b'\x01', 1e-9), (Unknown, 4e-9), (b'\x08', 6e-9), (b'\x04', 7e-9), (b'\x03', 8e-9), (b'\x00', 9e-9), (b'\x0a', 12e-9)],
            [
                [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xd2', 8e-9)],
                [(b'\xd2', 8e-9), (b'\x8b', 12e-9)],
                [(b'\xd2', 7e-9)],
                [(b'\xd2', 6e-9), (b'\x8b', 12e-9)]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        n: int = len(t[3])
        po: list[ChannelProbe] = [ChannelProbe(f'out{i}', w) for i in range(n)]
        ti: list[Source] = [Source(w, t[1]), Source(n, t[2])]
        to: list[Drain] = [Drain(w) for _ in range(n)]
        dev: DataRetainingDemultiplexer = DataRetainingDemultiplexer(w, n)
        ti[0].port_o.connect(dev.port_i)
        ti[1].port_o.connect(dev.port_s)
        for i in range(n):
            dev.ports_o[i].connect(to[i].port_i)
            dev.ports_o[i].add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[3]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_Distributor() -> None:
    test_data: list[tuple[int, list[tuple[DataWord, float]], list[list[tuple[DataWord, float]]]]] = [
        (
            1,
            [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9), (b'\x00', 9e-9)],
            [
                [(b'\x01', 2e-9), (b'\x00', 3e-9), (Unknown, 4e-9), (b'\x01', 5e-9), (b'\x00', 6e-9), (Unknown, 7e-9), (b'\x00', 9e-9)]
            ]
        ),
        (
            8,
            [
                (b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9)
            ],
            [
                [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9)],
                [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9)],
                [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9)],
                [(b'\xf1', 2e-9), (Unknown, 3e-9), (b'\xfe', 5e-9), (b'\xd2', 6e-9), (b'\x1e', 9e-9)]
            ]
        )
    ]
    for t in test_data:  # dangling input case
        n: int = len(t[2])
        po: list[ChannelProbe] = [ChannelProbe(f'out{i}', t[0]) for i in range(n)]
        to: list[Drain] = [Drain(t[0]) for _ in range(n)]
        dev: Distributor = Distributor(t[0], n)
        for i in range(n):
            dev.ports_o[i].connect(to[i].port_i)
            dev.ports_o[i].add_probe(po[i])
        sim: Simulator = Simulator([*to, dev])
        sim.start(show_time=True)
        for p in po:
            assert len(p.data) == 1
            assert p.data[0][0] == HighZ
            assert p.data[0][1] == 0.0
    for t in test_data:
        n: int = len(t[2])  # type: ignore[no-redef]
        po: list[ChannelProbe] = [ChannelProbe(f'out{i}', t[0]) for i in range(n)]  # type: ignore[no-redef]
        ti: Source = Source(t[0], t[1])
        to: list[Drain] = [Drain(t[0]) for _ in range(n)]  # type: ignore[no-redef]
        dev: Distributor = Distributor(t[0], n)  # type: ignore[no-redef]
        ti.port_o.connect(dev.port_i)
        for i in range(n):
            dev.ports_o[i].connect(to[i].port_i)
            dev.ports_o[i].add_probe(po[i])
        sim: Simulator = Simulator([ti, *to, dev])  # type: ignore[no-redef]
        sim.start(show_time=True)
        for p, r in zip(po, t[2]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS
