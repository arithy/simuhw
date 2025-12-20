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

from collections.abc import Callable

from simuhw import Source, Drain, ChannelProbe, MemoryProbe, Simulator
from simuhw.memory import LevelTriggeredMemory
from simuhw.memory.model import MockMemorizingModel, RealMemorizingModel

_EPS: float = 1e-18


def test_LevelTriggeredMemory_Mock() -> None:
    test_data: list[tuple[tuple[int, int, Callable[[bytes | None], bytes | None], bool, bytes], list[list[tuple[bytes | None, float]]]]] = [
        (
            (8, 4, lambda x: None if x is None else (int.from_bytes(x) + 0xf0).to_bytes(1), False, b'\x0c'),
            [
                [([None, b'\x00', b'\x01'][(i // 9) % 3], 1e-9 * i) for i in range(0, 27 * 2, 9)],
                [([None, b'\x0c', b'\x02'][(i // 3) % 3], 1e-9 * i) for i in range(0, 27 * 2, 3)],
                [(None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) for i in range(27 * 2)],
                [
                    (None if (i // 9) % 3 == 0 else [None, b'\xfc', b'\xf2'][(i // 3) % 3], 1e-9 * i)
                    for i in [12, 15, 18, 21, 24, 27, 39, 42, 45, 48, 51]
                ],
                [
                    (b'\xfc', 1e-9 * i)
                    for i in [0, 21, 22, 23, 48, 49, 50]
                ]
            ]
        ),
        (
            (8, 4, lambda x: None if x is None else (int.from_bytes(x) + 0xf0).to_bytes(1), True, b'\x0c'),
            [
                [([None, b'\x01', b'\x00'][(i // 9) % 3], 1e-9 * i) for i in range(0, 27 * 2, 9)],
                [([None, b'\x0c', b'\x02'][(i // 3) % 3], 1e-9 * i) for i in range(0, 27 * 2, 3)],
                [(None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) for i in range(27 * 2)],
                [
                    (None if (i // 9) % 3 == 0 else [None, b'\xfc', b'\xf2'][(i // 3) % 3], 1e-9 * i)
                    for i in [12, 15, 18, 21, 24, 27, 39, 42, 45, 48, 51]
                ],
                [
                    (b'\xfc', 1e-9 * i)
                    for i in [0, 21, 22, 23, 48, 49, 50]
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        a: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        pm: MemoryProbe = MemoryProbe('mem', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([1, a, w], t[1])]
        to: Drain = Drain(w)
        dev: LevelTriggeredMemory = LevelTriggeredMemory(w, a, model=MockMemorizingModel(t[0][2]), neg_leveled=t[0][3])
        ti[0].port_o.connect(dev.port_g)
        ti[1].port_o.connect(dev.port_a)
        ti[2].port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        dev.add_probe(pm, t[0][4])
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        for p, r in zip([po, pm], t[1][3:5]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_LevelTriggeredMemory_Real() -> None:
    test_data: list[tuple[tuple[int, int, bytes, bool, bytes], list[list[tuple[bytes | None, float]]]]] = [
        (
            (8, 4, b'\xa5', False, b'\x0c'),
            [
                [([None, b'\x00', b'\x01'][(i // 9) % 3], 1e-9 * i) for i in range(0, 27 * 2, 9)],
                [([None, b'\x0c', b'\x02'][(i // 3) % 3], 1e-9 * i) for i in range(0, 27 * 2, 3)],
                [(None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) for i in range(27 * 2)],
                [
                    (None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) if i >= 0 else
                    (None if (~i // 3) % 3 == 0 else b'\xa5' if ~i // 27 == 0 else (0xc0 + (~i - 9 - 7)).to_bytes(1), 1e-9 * ~i)
                    for i in [~12, 18, 22, 23, 24, 25, 26, 27, ~39, ~42, 45, 49, 50, 51, 52, 53]
                ],
                [
                    (b'\xa5', 0e-9), *((None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) for i in [21, 22, 23, 48, 49, 50])
                ]
            ]
        ),
        (
            (8, 4, b'\xa5', True, b'\x0c'),
            [
                [([None, b'\x01', b'\x00'][(i // 9) % 3], 1e-9 * i) for i in range(0, 27 * 2, 9)],
                [([None, b'\x0c', b'\x02'][(i // 3) % 3], 1e-9 * i) for i in range(0, 27 * 2, 3)],
                [(None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) for i in range(27 * 2)],
                [
                    (None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) if i >= 0 else
                    (None if (~i // 3) % 3 == 0 else b'\xa5' if ~i // 27 == 0 else (0xc0 + (~i - 9 - 7)).to_bytes(1), 1e-9 * ~i)
                    for i in [~12, 18, 22, 23, 24, 25, 26, 27, ~39, ~42, 45, 49, 50, 51, 52, 53]
                ],
                [
                    (b'\xa5', 0e-9), *((None if i % 3 == 0 else (0xc0 + i).to_bytes(1), 1e-9 * i) for i in [21, 22, 23, 48, 49, 50])
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        a: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        pm: MemoryProbe = MemoryProbe('mem', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([1, a, w], t[1])]
        to: Drain = Drain(w)
        dev: LevelTriggeredMemory = LevelTriggeredMemory(w, a, model=RealMemorizingModel(t[0][2]), neg_leveled=t[0][3])
        ti[0].port_o.connect(dev.port_g)
        ti[1].port_o.connect(dev.port_a)
        ti[2].port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        dev.add_probe(pm, t[0][4])
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        for p, r in zip([po, pm], t[1][3:5]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS
