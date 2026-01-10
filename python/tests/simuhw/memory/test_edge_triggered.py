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
from collections.abc import Callable

from simuhw import DataWord, Unknown, Source, Drain, ChannelProbe, MemoryProbe, Simulator
from simuhw.memory import EdgeTriggeredMemory
from simuhw.memory.model import MockMemorizingModel, RealMemorizingModel

_EPS: float = 1e-18


def test_EdgeTriggeredMemory_Mock() -> None:
    test_data: list[tuple[tuple[int, int, Callable[[DataWord], DataWord], bool, bytes], list[list[tuple[DataWord, float]]]]] = [
        (
            (8, 4, lambda x: Unknown if not isinstance(x, bytes) else (int.from_bytes(x) + 0xf0).to_bytes(1), False, b'\x0c'),
            [
                [(cast(list[DataWord], [Unknown, b'\x00', b'\x01', b'\x00'])[i % 4], 1e-9 * (2 * i + 1)) for i in range(36 * 2)],
                [(cast(list[DataWord], [b'\x01', b'\x00'])[(i // 36) % 2], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 36)],
                [(cast(list[DataWord], [Unknown, b'\x0c', b'\x02'])[(i // 12) % 3], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 12)],
                [(Unknown if i % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i)) for i in range(36 * 2)],
                [
                    (Unknown, 1e-9 * (2 * i)) if i % 36 == 0 else
                    (Unknown if i % 4 == 0 else cast(list[DataWord], [Unknown, b'\xfc', b'\xf2'])[(i // 12) % 3], 1e-9 * (2 * i + 1))
                    for i in [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70]
                ],
                [
                    (b'\xfc', 1e-9 * (2 * i if i == 0 else 2 * i + 1))
                    for i in [0, 14, 18, 22]
                ]
            ]
        ),
        (
            (8, 4, lambda x: Unknown if not isinstance(x, bytes) else (int.from_bytes(x) + 0xf0).to_bytes(1), True, b'\x0c'),
            [
                [(cast(list[DataWord], [Unknown, b'\x01', b'\x00', b'\x01'])[i % 4], 1e-9 * (2 * i + 1)) for i in range(36 * 2)],
                [(cast(list[DataWord], [b'\x01', b'\x00'])[(i // 36) % 2], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 36)],
                [(cast(list[DataWord], [Unknown, b'\x0c', b'\x02'])[(i // 12) % 3], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 12)],
                [(Unknown if i % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i)) for i in range(36 * 2)],
                [
                    (Unknown, 1e-9 * (2 * i)) if i % 36 == 0 else
                    (Unknown if i % 4 == 0 else cast(list[DataWord], [Unknown, b'\xfc', b'\xf2'])[(i // 12) % 3], 1e-9 * (2 * i + 1))
                    for i in [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70]
                ],
                [
                    (b'\xfc', 1e-9 * (2 * i if i == 0 else 2 * i + 1))
                    for i in [0, 14, 18, 22]
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        a: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        pm: MemoryProbe = MemoryProbe('mem', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([1, 1, a, w], t[1])]
        to: Drain = Drain(w)
        dev: EdgeTriggeredMemory = EdgeTriggeredMemory(w, a, model=MockMemorizingModel(t[0][2]), neg_edged=t[0][3])
        ti[0].port_o.connect(dev.port_c)
        ti[1].port_o.connect(dev.port_e)
        ti[2].port_o.connect(dev.port_a)
        ti[3].port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        dev.add_probe(pm, t[0][4])
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        for p, r in zip([po, pm], t[1][4:6]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_EdgeTriggeredMemory_Real() -> None:
    test_data: list[tuple[tuple[int, int, bytes, bool, bytes], list[list[tuple[DataWord, float]]]]] = [
        (
            (8, 4, b'\xa5', False, b'\x0c'),
            [
                [(cast(list[DataWord], [Unknown, b'\x00', b'\x01', b'\x00'])[i % 4], 1e-9 * (2 * i + 1)) for i in range(36 * 2)],
                [(cast(list[DataWord], [b'\x01', b'\x00'])[(i // 36) % 2], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 36)],
                [(cast(list[DataWord], [Unknown, b'\x0c', b'\x02'])[(i // 12) % 3], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 12)],
                [(Unknown if i % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i)) for i in range(36 * 2)],
                [
                    (Unknown, 1e-9 * (2 * i)) if i % 36 == 0 else
                    (Unknown if i % 4 == 0 or (i // 12) % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i + 1)) if i >= 0 else
                    (Unknown if ~i % 4 == 0 or (~i // 12) % 3 == 0 else (0xa0 + [0, 22, 34][(~i // 12) % 3]).to_bytes(1), 1e-9 * (2 * ~i + 1))
                    for i in [14, 16, 22, 24, 26, 28, 34, 36, ~50, 52, ~54, 56, ~58, 60, ~62, 64, ~66, 68, ~70]
                ],
                [
                    (b'\xa5', 0e-9),
                    *(
                        (Unknown if i % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i + 1))
                        for i in [14, 18, 22]
                    )
                ]
            ]
        ),
        (
            (8, 4, b'\xa5', True, b'\x0c'),
            [
                [(cast(list[DataWord], [Unknown, b'\x01', b'\x00', b'\x01'])[i % 4], 1e-9 * (2 * i + 1)) for i in range(36 * 2)],
                [(cast(list[DataWord], [b'\x01', b'\x00'])[(i // 36) % 2], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 36)],
                [(cast(list[DataWord], [Unknown, b'\x0c', b'\x02'])[(i // 12) % 3], 1e-9 * (2 * i)) for i in range(0, 36 * 2, 12)],
                [(Unknown if i % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i)) for i in range(36 * 2)],
                [
                    (Unknown, 1e-9 * (2 * i)) if i % 36 == 0 else
                    (Unknown if i % 4 == 0 or (i // 12) % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i + 1)) if i >= 0 else
                    (Unknown if ~i % 4 == 0 or (~i // 12) % 3 == 0 else (0xa0 + [0, 22, 34][(~i // 12) % 3]).to_bytes(1), 1e-9 * (2 * ~i + 1))
                    for i in [14, 16, 22, 24, 26, 28, 34, 36, ~50, 52, ~54, 56, ~58, 60, ~62, 64, ~66, 68, ~70]
                ],
                [
                    (b'\xa5', 0e-9),
                    *(
                        (Unknown if i % 3 == 0 else (0xa0 + i).to_bytes(1), 1e-9 * (2 * i + 1))
                        for i in [14, 18, 22]
                    )
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        a: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', w)
        pm: MemoryProbe = MemoryProbe('mem', w)
        ti: list[Source] = [Source(u, d) for u, d in zip([1, 1, a, w], t[1])]
        to: Drain = Drain(w)
        dev: EdgeTriggeredMemory = EdgeTriggeredMemory(w, a, model=RealMemorizingModel(t[0][2]), neg_edged=t[0][3])
        ti[0].port_o.connect(dev.port_c)
        ti[1].port_o.connect(dev.port_e)
        ti[2].port_o.connect(dev.port_a)
        ti[3].port_o.connect(dev.port_i)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        dev.add_probe(pm, t[0][4])
        sim: Simulator = Simulator([*ti, to, dev])
        sim.start(show_time=True)
        for p, r in zip([po, pm], t[1][4:6]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS
