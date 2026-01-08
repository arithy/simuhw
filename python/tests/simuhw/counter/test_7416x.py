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

import math

from simuhw import Source, Drain, ChannelProbe, Simulator
from simuhw.counter import SynchronousBinaryCounter74161, SynchronousBinaryCounter74163

_EPS: float = 1e-18

_UNIT: float = 1e-9
_S_QCYCLE: int = 1
_S_HCYCLE: int = _S_QCYCLE * 2
_S_CYCLE: int = _S_HCYCLE * 2

_S_START: int = 2
_S_CLR_0_L: int = _S_START + _S_CYCLE + _S_QCYCLE
_S_CLR_0_H: int = _S_CLR_0_L + _S_CYCLE
_S_LOAD_L: int = _S_CLR_0_H + _S_CYCLE * 4
_S_LOAD_H: int = _S_LOAD_L + _S_CYCLE
_S_ENP_L: int = _S_LOAD_H + _S_CYCLE * 4
_S_ENT_L: int = _S_ENP_L + _S_CYCLE
_S_ENP_H: int = _S_ENT_L + _S_CYCLE
_S_ENT_H: int = _S_ENP_H + _S_CYCLE
_S_CLR_1_L: int = _S_ENT_H + _S_CYCLE * 4
_S_CLR_1_H: int = _S_CLR_1_L + _S_CYCLE
_S_END: int = _S_CLR_1_H + _S_CYCLE * 4


def test_SynchronousBinaryCounter74161() -> None:
    test_data: list[tuple[int, list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]]] = [
        (
            1,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\x01', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * _S_CLR_1_L),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 4)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        ),
        (
            4,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\x0e', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x0e', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\x0f', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x02', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x03', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x04', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x05', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x06', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * _S_CLR_1_L),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        ),
        (
            8,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\xfe', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\xfe', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\xff', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x02', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x03', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x04', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x05', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x06', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * _S_CLR_1_L),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        ),
        (
            33,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\x01\xff\xff\xff\xfe', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00\x00\x00\x00\x00', _UNIT * _S_CLR_0_L),
                    (b'\x00\x00\x00\x00\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x02', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x03', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x04', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01\xff\xff\xff\xfe', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\x01\xff\xff\xff\xff', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x02', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00\x00\x00\x00\x03', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x04', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x05', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x06', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00\x00\x00\x00\x00', _UNIT * _S_CLR_1_L),
                    (b'\x00\x00\x00\x00\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x02', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x03', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x04', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * _S_CLR_0_L),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('carry', 1)]
        ti: list[Source] = [Source(u, d) for u, d in zip([1, 1, 1, 1, 1, w], t[1])]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SynchronousBinaryCounter74161 = SynchronousBinaryCounter74161(w)
        dev.port_q.connect(to[0].port_i)
        dev.port_co.connect(to[1].port_i)
        ti[0].port_o.connect(dev.port_ck)
        ti[1].port_o.connect(dev.port_clr)
        ti[2].port_o.connect(dev.port_enp)
        ti[3].port_o.connect(dev.port_ent)
        ti[4].port_o.connect(dev.port_load)
        ti[5].port_o.connect(dev.port_d)
        dev.port_q.add_probe(po[0])
        dev.port_co.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[2]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


def test_SynchronousBinaryCounter74163() -> None:
    test_data: list[tuple[int, list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]]] = [
        (
            1,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\x01', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_CLR_1_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 4)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        ),
        (
            4,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\x0e', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x0e', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\x0f', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x02', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x03', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x04', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x05', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x06', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_CLR_1_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        ),
        (
            8,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\xfe', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\xfe', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\xff', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x02', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x03', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x04', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x05', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x06', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00', _UNIT * (_S_CLR_1_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x02', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x03', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x04', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        ),
        (
            33,
            [
                [  # ck
                    ([b'\x00', b'\x01'][i % 2], _UNIT * (_S_START + _S_HCYCLE * i))
                    for i in range(math.ceil((_S_END - _S_START) / _S_HCYCLE))
                ],
                [  # clr
                    (b'\x00', _UNIT * _S_CLR_0_L), (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_CLR_1_L), (b'\x01', _UNIT * _S_CLR_1_H)
                ],
                [  # enp
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENP_L), (b'\x01', _UNIT * _S_ENP_H)
                ],
                [  # ent
                    (b'\x01', _UNIT * _S_CLR_0_H), (b'\x00', _UNIT * _S_ENT_L), (b'\x01', _UNIT * _S_ENT_H)
                ],
                [  # load
                    (b'\x01', _UNIT * _S_CLR_0_H),
                    (b'\x00', _UNIT * _S_LOAD_L), (b'\x01', _UNIT * _S_LOAD_H)
                ],
                [  # d
                    (b'\x01\xff\xff\xff\xfe', _UNIT * _S_LOAD_L), (None, _UNIT * _S_LOAD_H)
                ]
            ],
            [
                [  # q
                    (b'\x00\x00\x00\x00\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x00\x00\x00\x00\x01', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x02', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x03', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x04', _UNIT * (_S_CLR_0_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x01\xff\xff\xff\xfe', _UNIT * (_S_LOAD_L + _S_QCYCLE)),
                    (b'\x01\xff\xff\xff\xff', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x00', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x01', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x02', _UNIT * (_S_LOAD_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00\x00\x00\x00\x03', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x04', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x05', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x06', _UNIT * (_S_ENT_H + _S_QCYCLE + _S_CYCLE * 3)),
                    (b'\x00\x00\x00\x00\x00', _UNIT * (_S_CLR_1_L + _S_QCYCLE)),
                    (b'\x00\x00\x00\x00\x01', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 0)),
                    (b'\x00\x00\x00\x00\x02', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 1)),
                    (b'\x00\x00\x00\x00\x03', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00\x00\x00\x00\x04', _UNIT * (_S_CLR_1_H + _S_QCYCLE + _S_CYCLE * 3))
                ],
                [  # co
                    (b'\x00', _UNIT * (_S_CLR_0_L + _S_QCYCLE)),
                    (b'\x01', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 2)),
                    (b'\x00', _UNIT * (_S_LOAD_L + _S_QCYCLE + _S_CYCLE * 3))
                ]
            ]
        )
    ]
    for t in test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('carry', 1)]
        ti: list[Source] = [Source(u, d) for u, d in zip([1, 1, 1, 1, 1, w], t[1])]
        to: list[Drain] = [Drain(w), Drain(1)]
        dev: SynchronousBinaryCounter74163 = SynchronousBinaryCounter74163(w)
        dev.port_q.connect(to[0].port_i)
        dev.port_co.connect(to[1].port_i)
        ti[0].port_o.connect(dev.port_ck)
        ti[1].port_o.connect(dev.port_clr)
        ti[2].port_o.connect(dev.port_enp)
        ti[3].port_o.connect(dev.port_ent)
        ti[4].port_o.connect(dev.port_load)
        ti[5].port_o.connect(dev.port_d)
        dev.port_q.add_probe(po[0])
        dev.port_co.add_probe(po[1])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, t[2]):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS
