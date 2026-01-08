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

from simuhw import Source, Drain, ChannelProbe, Simulator
import simuhw.fp as hwf

from .skipif import skipif_unavailable
from . import skipif as sf

_EPS: float = 1e-18

_int_data: list[int] = [
    -(1 << 64),
    -2,
    -1,
    0,
    1,
    2,
    (1 << 64)
]
_int_data_count: int = len(_int_data)

_float_data: list[float] = [
    -math.inf,
    -math.nan,
    -1.7e20,
    -1.3,
    -0.0,
    0.0,
    1.3,
    1.7e20,
    math.nan,
    math.inf
]
_float_data_count: int = len(_float_data)


def _to_signed_int(nbits: int, value: int) -> int:
    return value if nbits <= 0 or (value >> (nbits - 1)) & 1 == 0 else -((~value + 1) & ((1 << nbits) - 1))


@skipif_unavailable
def test_FPToIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    for fi in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wo in [7, 33]:
            print(f'fi: {fi}, wo: {wo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(fi.from_float(v).to_bytes() for v in _float_data),  # type: ignore[attr-defined]
                            None
                        ])
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
                ],
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                (fi.from_float(v).to_ui64(hwf.RoundingMode.MIN).to_int() & ((1 << wo) - 1)).to_bytes((wo + 7) >> 3)  # type: ignore[attr-defined]
                                for v in _float_data
                            ),
                            None
                        ])
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                e.to_bytes(1) for e in [
                                    hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID,
                                    hwf.ExceptionFlag.INVALID, 0, 0, hwf.ExceptionFlag.INEXACT,
                                    hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID
                                ]
                            ),
                            None
                        ])
                    ]
                ]
            )
            wi: int = fi.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo), Drain(5)]
            dev: hwf.FPToIntegerConverter = hwf.FPToIntegerConverter(fi, wo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_FPFromIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    for fo in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wi in [7, 33]:
            print(f'wi: {wi}, fo: {fo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *((abs(v) & ((1 << wi) - 1)).to_bytes((wi + 7) >> 3) for v in _int_data),
                            None
                        ])
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
                ],
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                fo.from_ui64(sf.UInt64.from_int(abs(v) & ((1 << wi) - 1))).to_bytes()  # type: ignore[attr-defined]
                                for v in _int_data
                            ),
                            None
                        ])
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(b'\x00' for _ in _int_data),
                            None
                        ])
                    ]
                ]
            )
            wo: int = fo.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo), Drain(5)]
            dev: hwf.FPFromIntegerConverter = hwf.FPFromIntegerConverter(wi, fo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_FPToSignedIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    for fi in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wo in [7, 33]:
            print(f'fi: {fi}, wo: {wo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(fi.from_float(v).to_bytes() for v in _float_data),  # type: ignore[attr-defined]
                            None
                        ])
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
                ],
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                (fi.from_float(v).to_i64(hwf.RoundingMode.MIN).to_int() & ((1 << wo) - 1)).to_bytes((wo + 7) >> 3)  # type: ignore[attr-defined]
                                for v in _float_data
                            ),
                            None
                        ])
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                e.to_bytes(1) for e in [
                                    hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID,
                                    hwf.ExceptionFlag.INEXACT, 0, 0, hwf.ExceptionFlag.INEXACT,
                                    hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID
                                ]
                            ),
                            None
                        ])
                    ]
                ]
            )
            wi: int = fi.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo), Drain(5)]
            dev: hwf.FPToSignedIntegerConverter = hwf.FPToSignedIntegerConverter(fi, wo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_FPFromSignedIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    for fo in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wi in [7, 33]:
            print(f'wi: {wi}, fo: {fo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *((v & ((1 << wi) - 1)).to_bytes((wi + 7) >> 3) for v in _int_data),
                            None
                        ])
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
                ],
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                fo.from_i64(sf.Int64.from_int(_to_signed_int(wi, v & ((1 << wi) - 1)))).to_bytes()  # type: ignore[attr-defined]
                                for v in _int_data
                            ),
                            None
                        ])
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(b'\x00' for _ in _int_data),
                            None
                        ])
                    ]
                ]
            )
            wo: int = fo.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo), Drain(5)]
            dev: hwf.FPFromSignedIntegerConverter = hwf.FPFromSignedIntegerConverter(wi, fo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_FPConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.MIN)
    sf.set_exception_flags(0)
    for ii, fi in enumerate([hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]):
        for fo in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
            print(f'fi: {fi}, fo: {fo}')
            be: bool = (fo.size() >= fi.size() or fo.size() >= 64)  # type: ignore[attr-defined]
            bo: bool = (fo.size() <= 16)  # type: ignore[attr-defined]
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(fi.from_float(v).to_bytes() for v in _float_data),  # type: ignore[attr-defined]
                            None
                        ])
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
                ],
                [
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *([fo.from_f16, fo.from_f32, fo.from_f64, fo.from_f128][ii](fi.from_float(v)).to_bytes() for v in _float_data),  # type: ignore[attr-defined]
                            None
                        ])
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(
                                e.to_bytes(1) for e in [
                                    0, 0,
                                    0 if be else hwf.ExceptionFlag.INEXACT | (hwf.ExceptionFlag.OVERFLOW if bo else 0),
                                    0 if be else hwf.ExceptionFlag.INEXACT,
                                    0, 0,
                                    0 if be else hwf.ExceptionFlag.INEXACT,
                                    0 if be else hwf.ExceptionFlag.INEXACT | (hwf.ExceptionFlag.OVERFLOW if bo else 0),
                                    0, 0
                                ]
                            ),
                            None
                        ])
                    ]
                ]
            )
            wi: int = fi.size()  # type: ignore[attr-defined]
            wo: int = fo.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo), Drain(5)]
            dev: hwf.FPConverter = hwf.FPConverter(fi, fo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPToIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    m: int = 4
    for fi in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wo in [7, 33]:
            print(f'fi: {fi}, wo: {wo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        *(
                            (
                                b''.join((
                                    fi.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()  # type: ignore[attr-defined]
                                    for j in range(m)
                                )),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
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
                ],
                [
                    [
                        *(
                            (
                                reduce(lambda x, y: (x << wo) | y, (
                                    (
                                        fi.from_float(_float_data[(i + j) % _float_data_count])  # type: ignore[attr-defined]
                                        .to_ui64(hwf.RoundingMode.MIN).to_int() & ((1 << wo) - 1)
                                    )
                                    for j in range(m)
                                ), 0).to_bytes((wo * m + 7) >> 3),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
                    ],
                    [
                        *(
                            (
                                reduce(lambda x, y: x | y, (
                                    [
                                        hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID,
                                        hwf.ExceptionFlag.INVALID, 0, 0, hwf.ExceptionFlag.INEXACT,
                                        hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID
                                    ][(i + j) % _float_data_count]
                                    for j in range(m)
                                ), 0).to_bytes(1),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
                    ]
                ]
            )
            wi: int = fi.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo * m), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi * m, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo * m), Drain(5)]
            dev: hwf.SIMD_FPToIntegerConverter = hwf.SIMD_FPToIntegerConverter(m, fi, wo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPFromIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    m: int = 4
    for fo in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wi in [7, 33]:
            print(f'wi: {wi}, fo: {fo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        *(
                            (
                                reduce(lambda x, y: (x << wi) | y, (
                                    abs(_int_data[(i + j) % _int_data_count]) & ((1 << wi) - 1)
                                    for j in range(m)
                                ), 0).to_bytes((wi * m + 7) >> 3),
                                (1 + i) * 1e-9
                            )
                            for i in range(_int_data_count)
                        ),
                        (None, (1 + _int_data_count) * 1e-9)
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
                ],
                [
                    [
                        *(
                            (
                                b''.join((
                                    fo.from_ui64(  # type: ignore[attr-defined]
                                        sf.UInt64.from_int(abs(_int_data[(i + j) % _int_data_count]) & ((1 << wi) - 1))
                                    ).to_bytes()
                                    for j in range(m)
                                )),
                                (1 + i) * 1e-9
                            )
                            for i in range(_int_data_count)
                        ),
                        (None, (1 + _int_data_count) * 1e-9)
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(b'\x00' for _ in _int_data),
                            None
                        ])
                    ]
                ]
            )
            wo: int = fo.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo * m), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi * m, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo * m), Drain(5)]
            dev: hwf.SIMD_FPFromIntegerConverter = hwf.SIMD_FPFromIntegerConverter(m, wi, fo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPToSignedIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    m: int = 4
    for fi in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wo in [7, 33]:
            print(f'fi: {fi}, wo: {wo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        *(
                            (
                                b''.join((
                                    fi.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()  # type: ignore[attr-defined]
                                    for j in range(m)
                                )),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
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
                ],
                [
                    [
                        *(
                            (
                                reduce(lambda x, y: (x << wo) | y, (
                                    (
                                        fi.from_float(_float_data[(i + j) % _float_data_count])  # type: ignore[attr-defined]
                                        .to_i64(hwf.RoundingMode.MIN).to_int() & ((1 << wo) - 1)
                                    )
                                    for j in range(m)
                                ), 0).to_bytes((wo * m + 7) >> 3),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
                    ],
                    [
                        *(
                            (
                                reduce(lambda x, y: x | y, (
                                    [
                                        hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID,
                                        hwf.ExceptionFlag.INEXACT, 0, 0, hwf.ExceptionFlag.INEXACT,
                                        hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID, hwf.ExceptionFlag.INVALID
                                    ][(i + j) % _float_data_count]
                                    for j in range(m)
                                ), 0).to_bytes(1),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
                    ]
                ]
            )
            wi: int = fi.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo * m), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi * m, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo * m), Drain(5)]
            dev: hwf.SIMD_FPToSignedIntegerConverter = hwf.SIMD_FPToSignedIntegerConverter(m, fi, wo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPFromSignedIntegerConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.NEAR_EVEN)
    sf.set_exception_flags(0)
    m: int = 4
    for fo in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
        for wi in [7, 33]:
            print(f'wi: {wi}, fo: {fo}')
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        *(
                            (
                                reduce(lambda x, y: (x << wi) | y, (
                                    _int_data[(i + j) % _int_data_count] & ((1 << wi) - 1)
                                    for j in range(m)
                                ), 0).to_bytes((wi * m + 7) >> 3),
                                (1 + i) * 1e-9
                            )
                            for i in range(_int_data_count)
                        ),
                        (None, (1 + _int_data_count) * 1e-9)
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
                ],
                [
                    [
                        *(
                            (
                                b''.join((
                                    fo.from_i64(  # type: ignore[attr-defined]
                                        sf.Int64.from_int(_to_signed_int(wi, _int_data[(i + j) % _int_data_count] & ((1 << wi) - 1)))
                                    ).to_bytes()
                                    for j in range(m)
                                )),
                                (1 + i) * 1e-9
                            )
                            for i in range(_int_data_count)
                        ),
                        (None, (1 + _int_data_count) * 1e-9)
                    ],
                    [
                        (d, (1 + i) * 1e-9) for i, d in enumerate([
                            *(b'\x00' for _ in _int_data),
                            None
                        ])
                    ]
                ]
            )
            wo: int = fo.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo * m), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi * m, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo * m), Drain(5)]
            dev: hwf.SIMD_FPFromSignedIntegerConverter = hwf.SIMD_FPFromSignedIntegerConverter(m, wi, fo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPConverter() -> None:
    sf.set_tininess_mode(hwf.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(hwf.RoundingMode.MIN)
    sf.set_exception_flags(0)
    m: int = 4
    for ii, fi in enumerate([hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]):
        for fo in [hwf.Float16, hwf.Float32, hwf.Float64, hwf.Float128]:
            print(f'fi: {fi}, fo: {fo}')
            be: bool = (fo.size() >= fi.size() or fo.size() >= 64)  # type: ignore[attr-defined]
            bo: bool = (fo.size() <= 16)  # type: ignore[attr-defined]
            t: tuple[list[list[tuple[bytes | None, float]]], list[list[tuple[bytes | None, float]]]] = (
                [
                    [
                        *(
                            (
                                b''.join((
                                    fi.from_float(_float_data[(i + j) % _float_data_count]).to_bytes()  # type: ignore[attr-defined]
                                    for j in range(m)
                                )),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
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
                ],
                [
                    [
                        *(
                            (
                                b''.join((
                                    [fo.from_f16, fo.from_f32, fo.from_f64, fo.from_f128][ii](  # type: ignore[attr-defined]
                                        fi.from_float(_float_data[(i + j) % _float_data_count])  # type: ignore[attr-defined]
                                    ).to_bytes()
                                    for j in range(m)
                                )),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
                    ],
                    [
                        *(
                            (
                                reduce(lambda x, y: x | y, (
                                    [
                                        0, 0,
                                        0 if be else hwf.ExceptionFlag.INEXACT | (hwf.ExceptionFlag.OVERFLOW if bo else 0),
                                        0 if be else hwf.ExceptionFlag.INEXACT,
                                        0, 0,
                                        0 if be else hwf.ExceptionFlag.INEXACT,
                                        0 if be else hwf.ExceptionFlag.INEXACT | (hwf.ExceptionFlag.OVERFLOW if bo else 0),
                                        0, 0
                                    ][(i + j) % _float_data_count]
                                    for j in range(m)
                                ), 0).to_bytes(1),
                                (1 + i) * 1e-9
                            )
                            for i in range(_float_data_count)
                        ),
                        (None, (1 + _float_data_count) * 1e-9)
                    ]
                ]
            )
            wi: int = fi.size()  # type: ignore[attr-defined]
            wo: int = fo.size()  # type: ignore[attr-defined]
            po: list[ChannelProbe] = [ChannelProbe('out', wo * m), ChannelProbe('fe', 5)]
            ti: list[Source] = [Source(u, d) for u, d in zip([wi * m, 1, 3, 5], t[0])]
            to: list[Drain] = [Drain(wo * m), Drain(5)]
            dev: hwf.SIMD_FPConverter = hwf.SIMD_FPConverter(m, fi, fo)  # type: ignore[arg-type]
            for i, u in enumerate([dev.port_o, dev.port_fe_o]):
                u.connect(to[i].port_i)
                u.add_probe(po[i])
            for i, v in enumerate([*dev.ports_i, dev.port_ft, dev.port_fr, dev.port_fe_i]):
                ti[i].port_o.connect(v)
            sim: Simulator = Simulator([*ti, *to, dev])
            sim.start(show_time=True)
            for p, r in zip(po, [[o[i] for i in range(len(o)) if i == 0 or o[i][0] != o[i - 1][0]] for o in t[1]]):
                assert len(p.data) == len(r)
                for o, q in zip(p.data, r):
                    assert o[0] == q[0]
                    assert abs(o[1] - q[1]) <= _EPS
