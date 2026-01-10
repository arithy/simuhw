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

from functools import reduce
import math

from simuhw import DataWord, Source, Drain, ChannelProbe, Simulator
import simuhw.fp as hwf

from .skipif import skipif_unavailable
from . import skipif as sf

_EPS: float = 1e-18

_float_data: list[float] = [
    -math.inf,
    -math.nan,
    -2.5,
    -1.0,
    -0.0,
    0.0,
    1.0,
    2.5,
    math.nan,
    math.inf
]
_float_data_count: int = len(_float_data)

_except_data: dict[int, list[int]] = {}
if hwf.is_available():
    _except_data = {
        hwf.ExceptionFlag.INEXACT: [2, 7]
    }


@skipif_unavailable
def test_FPToIntegerRounder() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.MIN)
    sf.set_exception_flags(0)
    test_i: list[tuple[hwf.Float, list[int], list[list[tuple[DataWord, float]]]]] = [
        (
            hwf.Float16,
            [16, 1, 3, 5],
            [
                [
                    (hwf.Float16.from_float(_float_data[i]).to_bytes(), 1e-9 * (1 + i))
                    for i in range(_float_data_count)
                ],
                [
                    (hwf.TininessMode.AFTER_ROUNDING.to_bytes(1), 0e-9)
                ],
                [
                    (hwf.RoundingMode.MIN.to_bytes(1), 0e-9)
                ],
                [
                    (b'\x00', 0e-9)
                ]
            ]
        ),
        (
            hwf.Float32,
            [32, 1, 3, 5],
            [
                [
                    (hwf.Float32.from_float(_float_data[i]).to_bytes(), 1e-9 * (1 + i))
                    for i in range(_float_data_count)
                ],
                [
                    (hwf.TininessMode.AFTER_ROUNDING.to_bytes(1), 0e-9)
                ],
                [
                    (hwf.RoundingMode.MIN.to_bytes(1), 0e-9)
                ],
                [
                    (b'\x00', 0e-9)
                ]
            ]
        ),
        (
            hwf.Float64,
            [64, 1, 3, 5],
            [
                [
                    (hwf.Float64.from_float(_float_data[i]).to_bytes(), 1e-9 * (1 + i))
                    for i in range(_float_data_count)
                ],
                [
                    (hwf.TininessMode.AFTER_ROUNDING.to_bytes(1), 0e-9)
                ],
                [
                    (hwf.RoundingMode.MIN.to_bytes(1), 0e-9)
                ],
                [
                    (b'\x00', 0e-9)
                ]
            ]
        ),
        (
            hwf.Float128,
            [128, 1, 3, 5],
            [
                [
                    (hwf.Float128.from_float(_float_data[i]).to_bytes(), 1e-9 * (1 + i))
                    for i in range(_float_data_count)
                ],
                [
                    (hwf.TininessMode.AFTER_ROUNDING.to_bytes(1), 0e-9)
                ],
                [
                    (hwf.RoundingMode.MIN.to_bytes(1), 0e-9)
                ],
                [
                    (b'\x00', 0e-9)
                ]
            ]
        )
    ]
    test_t: list[list[list[tuple[DataWord, float]]]] = [
        [
            [
                (
                    hwf.Float16.from_float(_float_data[i]).round_to_int().to_bytes(),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ],
            [
                (
                    reduce(lambda x, y: x | y, (e for e in _except_data if i in _except_data[e]), 0).to_bytes(1),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ]
        ],
        [
            [
                (
                    hwf.Float32.from_float(_float_data[i]).round_to_int().to_bytes(),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ],
            [
                (
                    reduce(lambda x, y: x | y, (e for e in _except_data if i in _except_data[e]), 0).to_bytes(1),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ]
        ],
        [
            [
                (
                    hwf.Float64.from_float(_float_data[i]).round_to_int().to_bytes(),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ],
            [
                (
                    reduce(lambda x, y: x | y, (e for e in _except_data if i in _except_data[e]), 0).to_bytes(1),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ]
        ],
        [
            [
                (
                    hwf.Float128.from_float(_float_data[i]).round_to_int().to_bytes(),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ],
            [
                (
                    reduce(lambda x, y: x | y, (e for e in _except_data if i in _except_data[e]), 0).to_bytes(1),
                    1e-9 * (1 + i)
                )
                for i in range(_float_data_count)
            ]
        ]
    ]
    test_o: list[list[list[tuple[DataWord, float]]]] = [
        [
            [
                *(
                    s[i]
                    for i in range(len(s))
                    if i < 1 or s[i - 1][0] != s[i][0]
                )
            ]
            for s in t
        ]
        for t in test_t
    ]
    for t, s in zip(test_i, test_o):
        f: hwf.Float = t[0]
        w: int = f.size()
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('fe', hwf.FPToIntegerRounder.width_fe)]
        ti: list[Source] = [Source(u, d) for u, d in zip(t[1], t[2])]
        to: list[Drain] = [Drain(w), Drain(hwf.FPToIntegerRounder.width_fe)]
        dev: hwf.FPToIntegerRounder = hwf.FPToIntegerRounder(f)
        for i, u in enumerate([dev.port_o, dev.port_fe_o]):
            u.connect(to[i].port_i)
            u.add_probe(po[i])
        for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
            ti[i].port_o.connect(v)
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, s):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPToIntegerRounder() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.MIN)
    sf.set_exception_flags(0)
    test_i: list[tuple[list[int], list[hwf.Float], list[list[tuple[DataWord, float]]]]] = [
        (
            [256, 2, 1, 3, 5],
            [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128],
            [
                [
                    *(
                        (
                            b''.join((
                                hwf.Float16.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()
                                for j in range(256 // 16)
                            )),
                            1e-9 * (1 + i)
                        )
                        for i in range(_float_data_count)
                    ),
                    *(
                        (
                            b''.join((
                                hwf.Float32.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()
                                for j in range(256 // 32)
                            )),
                            1e-9 * (1 + i)
                        )
                        for i in range(_float_data_count, _float_data_count * 2)
                    ),
                    *(
                        (
                            b''.join((
                                hwf.Float64.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()
                                for j in range(256 // 64)
                            )),
                            1e-9 * (1 + i)
                        )
                        for i in range(_float_data_count * 2, _float_data_count * 3)
                    ),
                    *(
                        (
                            b''.join((
                                hwf.Float128.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()
                                for j in range(256 // 128)
                            )),
                            1e-9 * (1 + i)
                        )
                        for i in range(_float_data_count * 3, _float_data_count * 4)
                    )
                ],
                [
                    (b'\x00', 1e-9 * (1 + _float_data_count * 0)),
                    (b'\x01', 1e-9 * (1 + _float_data_count * 1)),
                    (b'\x02', 1e-9 * (1 + _float_data_count * 2)),
                    (b'\x03', 1e-9 * (1 + _float_data_count * 3))
                ],
                [
                    (hwf.TininessMode.AFTER_ROUNDING.to_bytes(1), 0e-9)
                ],
                [
                    (hwf.RoundingMode.MIN.to_bytes(1), 0e-9)
                ],
                [
                    (b'\x00', 0e-9)
                ]
            ]
        )
    ]
    test_t: list[list[list[tuple[DataWord, float]]]] = [
        [
            [
                *(
                    (
                        b''.join((
                            hwf.Float16.from_float(_float_data[(i + j) % _float_data_count]).round_to_int().to_bytes()
                            for j in range(256 // 16)
                        )),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count)
                ),
                *(
                    (
                        b''.join((
                            hwf.Float32.from_float(_float_data[(i + j) % _float_data_count]).round_to_int().to_bytes()
                            for j in range(256 // 32)
                        )),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count, _float_data_count * 2)
                ),
                *(
                    (
                        b''.join((
                            hwf.Float64.from_float(_float_data[(i + j) % _float_data_count]).round_to_int().to_bytes()
                            for j in range(256 // 64)
                        )),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count * 2, _float_data_count * 3)
                ),
                *(
                    (
                        b''.join((
                            hwf.Float128.from_float(_float_data[(i + j) % _float_data_count]).round_to_int().to_bytes()
                            for j in range(256 // 128)
                        )),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count * 3, _float_data_count * 4)
                )
            ],
            [
                *(
                    (
                        reduce(lambda x, y: x | y, (
                            e for e in _except_data if any((
                                (i + j) % _float_data_count in _except_data[e]
                                for j in range(256 // 16)
                            ))
                        ), 0).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count)
                ),
                *(
                    (
                        reduce(lambda x, y: x | y, (
                            e for e in _except_data if any((
                                (i + j) % _float_data_count in _except_data[e]
                                for j in range(256 // 32)
                            ))
                        ), 0).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count, _float_data_count * 2)
                ),
                *(
                    (
                        reduce(lambda x, y: x | y, (
                            e for e in _except_data if any((
                                (i + j) % _float_data_count in _except_data[e]
                                for j in range(256 // 64)
                            ))
                        ), 0).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count * 2, _float_data_count * 3)
                ),
                *(
                    (
                        reduce(lambda x, y: x | y, (
                            e for e in _except_data if any((
                                (i + j) % _float_data_count in _except_data[e]
                                for j in range(256 // 128)
                            ))
                        ), 0).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(_float_data_count * 3, _float_data_count * 4)
                )
            ]
        ]
    ]
    test_o: list[list[list[tuple[DataWord, float]]]] = [
        [
            [
                *(
                    s[i]
                    for i in range(len(s))
                    if i < 1 or s[i - 1][0] != s[i][0]
                )
            ]
            for s in t
        ]
        for t in test_t
    ]
    for t, s in zip(test_i, test_o):
        w: int = t[0][0]
        e: int = t[0][-1]
        po: list[ChannelProbe] = [ChannelProbe('out', w), ChannelProbe('fe', e)]
        ti: list[Source] = [Source(u, d) for u, d in zip(t[0], t[2])]
        to: list[Drain] = [Drain(w), Drain(e)]
        dev: hwf.SIMD_FPToIntegerRounder = hwf.SIMD_FPToIntegerRounder(w, t[1])
        for i, u in enumerate([dev.port_o, dev.port_fe_o]):
            u.connect(to[i].port_i)
            u.add_probe(po[i])
        for i, v in enumerate([*dev.ports_i, dev.port_s, dev.port_ft, dev.port_fr, dev.port_fe_i]):
            ti[i].port_o.connect(v)
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for p, r in zip(po, s):
            assert len(p.data) == len(r)
            for o, q in zip(p.data, r):
                assert o[0] == q[0]
                assert abs(o[1] - q[1]) <= _EPS
