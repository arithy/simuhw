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

from collections.abc import Iterable, Callable
from typing import cast
from functools import reduce
import math

from simuhw import Word, Source, Drain, ChannelProbe, Simulator, SIMD_Operator
from simuhw.alu import FullArithmeticLogicUnit, SIMD_FullArithmeticLogicUnit
from simuhw import fp
from simuhw.fp import riscv
import simuhw as hw

from ..fp.skipif import skipif_unavailable
from ..fp import skipif as sf

_EPS: float = 1e-18


def _is_fp_input_op(op: hw.Operator) -> bool:
    s: str = op.__class__.__name__
    return (
        (s.startswith('FP') and s not in ['FPFromIntegerConverter', 'FPFromSignedIntegerConverter']) or
        (s.startswith('SIMD_FP') and s not in ['SIMD_FPFromIntegerConverter', 'SIMD_FPFromSignedIntegerConverter']) or
        s in ['FRec7', 'FRSqrt7', 'SIMD_FRec7', 'SIMD_FRSqrt7']
    )


def _simd_dsize_count(op: hw.Operator) -> int:
    return len(op.dsize_i) if isinstance(op, SIMD_Operator) else 1


def _simd_word_count(op: hw.Operator, s: int) -> int:
    return op.multi[s] if isinstance(op, SIMD_Operator) else 1


def _simd_selection_by_index(dev: SIMD_FullArithmeticLogicUnit, iop: int, isz: int) -> int:
    return isz % _simd_dsize_count(dev.ops[iop])


def _simd_word_count_by_index(dev: SIMD_FullArithmeticLogicUnit, iop: int, isz: int) -> int:
    op: hw.Operator = dev.ops[iop]
    return _simd_word_count(op, isz % _simd_dsize_count(op))


def _to_signed_int(nbits: int, value: int) -> int:
    return value if nbits <= 0 or (value >> (nbits - 1)) & 1 == 0 else -((~value + 1) & ((1 << nbits) - 1))


def _div(x: int, y: int) -> int:
    return (abs(x) // abs(y)) * (1 if x >= 0 else -1) * (1 if y >= 0 else -1)


def _rem(x: int, y: int) -> int:
    return (abs(x) % abs(y)) * (1 if x >= 0 else -1)


def _cmp(x: int, y: int) -> int:
    return -1 if x < y else 1 if x > y else 0


def _fp_neg(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.neg(t.from_float(x)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_add(t: type, x: float, y: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.add(t.from_float(x), t.from_float(y)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_sub(t: type, x: float, y: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.sub(t.from_float(x), t.from_float(y)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_mul(t: type, x: float, y: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.mul(t.from_float(x), t.from_float(y)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_mul_add(t: type, x: float, y: float, z: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.mul_add(t.from_float(x), t.from_float(y), t.from_float(z)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_div(t: type, x: float, y: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.div(t.from_float(x), t.from_float(y)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_rem(t: type, x: float, y: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.rem(t.from_float(x), t.from_float(y)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_sqrt(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.sqrt(t.from_float(x)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_cmp(t: type, x: float, y: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return (
        -1 if t.lt(t.from_float(x), t.from_float(y)) else   # type: ignore[attr-defined]
        1 if t.lt(t.from_float(y), t.from_float(x)) else 0  # type: ignore[attr-defined]
    ).to_bytes(t.size() >> 3, signed=True)  # type: ignore[attr-defined]


def _fp_round_to_int(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.round_to_int(t.from_float(x), sf.get_rounding_mode()).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_from_ui64(t: type, x: int) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.from_ui64(sf.UInt64.from_int(x)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_from_i64(t: type, x: int) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.from_i64(sf.Int64.from_int(x)).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_to_ui64(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.to_ui64(t.from_float(x), sf.get_rounding_mode()).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_to_i64(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return t.to_i64(t.from_float(x), sf.get_rounding_mode()).to_bytes()  # type: ignore[attr-defined, no-any-return]


def _fp_to_fp(ti: type, to: type, x: float) -> bytes:
    assert ti in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    assert to in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return (  # type: ignore[no-any-return]
        ti.to_f16(ti.from_float(x)) if to.size() == 16 else  # type: ignore[attr-defined]
        ti.to_f32(ti.from_float(x)) if to.size() == 32 else  # type: ignore[attr-defined]
        ti.to_f64(ti.from_float(x)) if to.size() == 64 else  # type: ignore[attr-defined]
        ti.to_f128(ti.from_float(x)) if to.size() == 128 else to.from_float(math.nan)  # type: ignore[attr-defined]
    ).to_bytes()


def _fp_frec7(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return riscv.frec7(t.from_float(x)).to_bytes()  # type: ignore[attr-defined]


def _fp_frsqrt7(t: type, x: float) -> bytes:
    assert t in [fp.Float16, fp.Float32, fp.Float64, fp.Float128]
    return riscv.frsqrt7(t.from_float(x)).to_bytes()  # type: ignore[attr-defined]


def test_FullArithmeticLogicUnit() -> None:
    test_lut: list[bytes] = [
        ((math.ceil(math.sin(i + 3) * (1 << 20))) & ((1 << 16) - 1)).to_bytes((16 + 7) >> 3)
        for i in range(1 << 8)
    ]
    dev: FullArithmeticLogicUnit = FullArithmeticLogicUnit(
        [8, 16, 32, 64, 128],
        add_ops=[hw.LookupTable(8, 16, test_lut)]
    )
    wi: int = dev.width_i
    wo: int = dev.width_o
    ws: int = dev.width_s
    wop: int = dev.width_op
    wft: int = dev.width_ft
    wfr: int = dev.width_fr
    wfe: int = dev.width_fe
    ax: list[int] = [0x83, 0x05, 0x70]
    ay: list[int] = [0xf3, 0x00, 0x03]
    axp: list[int] = [3, 2, 3]  # population count
    axr: list[int] = [8, 3, 7]  # required bit count
    axt: list[int] = [0, 0, 4]  # trailing zeros
    axv: list[int] = [0xc1, 0xa0, 0x0e]  # bit reversal
    m: int = 9 * len(dev.ops)
    t: tuple[list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]] = (
        [
            [  # ports_i[0]
                (ax[i % 3].to_bytes((wi + 7) >> 3), 1e-9 * (1 + i)) for i in range(m)
            ],
            [  # ports_i[1]
                (ay[(i // 3) % 3].to_bytes((wi + 7) >> 3), 1e-9 * (1 + i)) for i in range(m)
            ],
            [  # port_op
                ((i // 9).to_bytes((wop + 7) >> 3), 1e-9 * (1 + i)) for i in range(m)
            ],
            [],  # port_s
            [  # port_ci
                (b'\x01', 0.0)
            ],
            [],  # port_ft
            [],  # port_fr
            []  # port_fe_i
        ],
        [
            [  # port_o
                (
                    cast(Word, [
                        ((
                            x if type(o) is hw.Buffer else
                            (~x) if type(o) is hw.Inverter else
                            (x & y) if type(o) is hw.ANDGate else
                            (x | y) if type(o) is hw.ORGate else
                            (x ^ y) if type(o) is hw.XORGate else
                            (~(x & y)) if type(o) is hw.NANDGate else
                            (~(x | y)) if type(o) is hw.NORGate else
                            (~(x ^ y)) if type(o) is hw.XNORGate else
                            (x << y) if type(o) is hw.LeftShifter else
                            (x >> y) if type(o) is hw.RightShifter else
                            (_to_signed_int(o.width_i, x) >> y) if type(o) is hw.ArithmeticRightShifter else
                            ((x << (y % o.width_o)) | (x >> (o.width_o - y % o.width_o))) if type(o) is hw.LeftRotator else
                            ((x >> (y % o.width_o)) | (x << (o.width_o - y % o.width_o))) if type(o) is hw.RightRotator else
                            axp[i % 3] if type(o) is hw.PopulationCounter else
                            (o.width_i - axr[i % 3]) if type(o) is hw.LeadingZeroCounter else
                            axt[i % 3] if type(o) is hw.TrailingZeroCounter else
                            (axv[i % 3] << (o.width_o - 8)) if type(o) is hw.BitReverser else
                            (-x) if type(o) is hw.Negator else
                            (x + y + 1) if type(o) is hw.FullAdder else
                            (x - y - 1) if type(o) is hw.FullSubtractor else
                            (x * y) if type(o) is hw.Multiplier else
                            (_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) if type(o) is hw.SignedMultiplier else
                            (x // y if y != 0 else 0) if type(o) is hw.Divider else
                            (_div(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedDivider else
                            (x % y if y != 0 else 0) if type(o) is hw.Remainder else
                            (_rem(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedRemainder else
                            _cmp(x, y) if type(o) is hw.Comparator else
                            _cmp(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if type(o) is hw.SignedComparator else
                            x if type(o) is hw.IntegerConverter else
                            _to_signed_int(o.width_i, x) if type(o) is hw.SignedIntegerConverter else
                            int.from_bytes(test_lut[x]) if type(o) is hw.LookupTable else
                            0
                        ) & ((1 << o.width_o) - 1)).to_bytes((dev.width_o + 7) >> 3)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_co
                (
                    cast(Word, [
                        (
                            (0 if ((x + y + 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullAdder else
                            (0 if ((x - y - 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullSubtractor else
                            0
                        ).to_bytes(1)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_e
                (
                    cast(Word, [
                        (
                            (0 if ((x * y) >> o.width_o) == 0 else 1) if type(o) is hw.Multiplier else
                            (0 if ((_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) >> o.width_o) in [0, -1] else 1) if type(o) is hw.SignedMultiplier else
                            (0 if y != 0 else 1) if type(o) is hw.Divider else
                            (0 if y != 0 else 1) if type(o) is hw.SignedDivider else
                            (0 if y != 0 else 1) if type(o) is hw.Remainder else
                            (0 if y != 0 else 1) if type(o) is hw.SignedRemainder else
                            0
                        ).to_bytes(1)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_fe_o
                (b'\x00' if wfe > 0 else b'', 1e-9)
            ]
        ]
    )
    po: list[ChannelProbe] = [ChannelProbe(s, w) for s, w in [('out', wo), ('co', 1), ('e', 1), ('fe', wfe)]]
    ti: list[Source] = [Source(w, d) for w, d in zip([wi, wi, wop, ws, 1, wft, wfr, wfe], t[0])]
    to: list[Drain] = [Drain(w) for w in [wo, 1, 1, wfe]]
    for i, p in enumerate([dev.ports_i[0], dev.ports_i[1], dev.port_op, dev.port_s, dev.port_ci, dev.port_ft, dev.port_fr, dev.port_fe_i]):
        ti[i].port_o.connect(p)
    for i, q in enumerate([dev.port_o, dev.port_co, dev.port_e, dev.port_fe_o]):
        q.connect(to[i].port_i)
        q.add_probe(po[i])
    sim: Simulator = Simulator([*ti, *to, dev])
    sim.start(max_iter=10000, show_time=True)
    for ro, a in zip(po, t[1]):
        rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
        assert len(ro) == len(rp)
        for ru, rv in zip(ro, rp):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


def test_SIMD_FullArithmeticLogicUnit() -> None:

    def gen_simd_data_int_1(o: SIMD_Operator, s: int, f: Callable[[int], int], ax: Iterable[int]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (f(x) for x in ax), 0)

    def gen_simd_data_int_2(o: SIMD_Operator, s: int, f: Callable[[int, int], int], ax: Iterable[int], ay: Iterable[int]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (f(x, y) for x, y in zip(ax, ay)), 0)

    test_lut: list[bytes] = [
        ((math.ceil(math.sin(i + 3) * (1 << 20))) & ((1 << 16) - 1)).to_bytes((16 + 7) >> 3)
        for i in range(1 << 8)
    ]
    dev: SIMD_FullArithmeticLogicUnit = SIMD_FullArithmeticLogicUnit(
        128, [8, 16, 128],
        add_ops=[hw.LookupTable(8, 16, test_lut)]
    )
    wi: int = dev.width_i
    wo: int = dev.width_o
    ws: int = dev.width_s
    wop: int = dev.width_op
    wft: int = dev.width_ft
    wfr: int = dev.width_fr
    wfe: int = dev.width_fe
    ax: list[int] = [0x83, 0x05, 0x70]
    ay: list[int] = [0xf3, 0x00, 0x03]
    axp: list[int] = [3, 2, 3]  # population count
    axr: list[int] = [8, 3, 7]  # required bit count
    axt: list[int] = [0, 0, 4]  # trailing zeros
    axv: list[int] = [0xc1, 0xa0, 0x0e]  # bit reversal
    m: int = 9 * len(dev.ops)
    t: tuple[list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]] = (
        [
            [  # ports_i[0]
                (
                    cast(Word, [
                        ((
                            reduce(lambda a, b: (a << o.dsize_i[s]) | (b & ((1 << o.dsize_i[s]) - 1)), tx, 0) if isinstance(o, SIMD_Operator) else x
                        ) & ((1 << o.width_i) - 1)).to_bytes((dev.width_i + 7) >> 3)
                        for o, s, x, tx in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ax[i % 3], (ax[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # ports_i[1]
                (
                    cast(Word, [
                        ((
                            reduce(lambda a, b: (a << o.dsize_i[s]) | (b & ((1 << o.dsize_i[s]) - 1)), ty, 0) if isinstance(o, SIMD_Operator) else y
                        ) & ((1 << o.width_i) - 1)).to_bytes((dev.width_i + 7) >> 3)
                        for o, s, y, ty in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ay[(i // 3) % 3], (ay[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_op
                ((i // 9).to_bytes((wop + 7) >> 3), 1e-9 * (1 + i)) for i in range(m)
            ],
            [  # port_s
                (
                    (_simd_selection_by_index(dev, i // 9, i // 3)).to_bytes((ws + 7) >> 3),
                    1e-9 * (1 + i)
                ) for i in range(m)
            ],
            [  # port_ci
                (b'\x01', 0.0)
            ],
            [],  # port_ft
            [],  # port_fr
            []  # port_fe_i
        ],
        [
            [  # port_o
                (
                    cast(Word, [
                        ((
                            (
                                gen_simd_data_int_2(o, s, lambda x, y: x << y, tx, ty) if type(o) is hw.SIMD_LeftShifter else
                                gen_simd_data_int_2(o, s, lambda x, y: x >> y, tx, ty) if type(o) is hw.SIMD_RightShifter else
                                gen_simd_data_int_2(o, s, lambda x, y: _to_signed_int(o.dsize_i[s], x) >> y, tx, ty) if type(o) is hw.SIMD_ArithmeticRightShifter else
                                gen_simd_data_int_2(o, s, lambda x, y: (x << (y % o.dsize_o[s])) | (x >> (o.dsize_o[s] - y % o.dsize_o[s])), tx, ty) if type(o) is hw.SIMD_LeftRotator else
                                gen_simd_data_int_2(o, s, lambda x, y: (x >> (y % o.dsize_o[s])) | (x << (o.dsize_o[s] - y % o.dsize_o[s])), tx, ty) if type(o) is hw.SIMD_RightRotator else
                                gen_simd_data_int_1(o, s, lambda p: p, tp) if type(o) is hw.SIMD_PopulationCounter else
                                gen_simd_data_int_1(o, s, lambda r: o.dsize_o[s] - r, tr) if type(o) is hw.SIMD_LeadingZeroCounter else
                                gen_simd_data_int_1(o, s, lambda t: t, tt) if type(o) is hw.SIMD_TrailingZeroCounter else
                                gen_simd_data_int_1(o, s, lambda v: v << (o.dsize_o[s] - 8), tv) if type(o) is hw.SIMD_BitReverser else
                                gen_simd_data_int_1(o, s, lambda x: -x, tx) if type(o) is hw.SIMD_Negator else
                                gen_simd_data_int_2(o, s, lambda x, y: x + y, tx, ty) if type(o) is hw.SIMD_Adder else
                                gen_simd_data_int_2(o, s, lambda x, y: x - y, tx, ty) if type(o) is hw.SIMD_Subtractor else
                                gen_simd_data_int_2(o, s, lambda x, y: x * y, tx, ty) if type(o) is hw.SIMD_Multiplier else
                                gen_simd_data_int_2(o, s, lambda x, y: _to_signed_int(o.dsize_i[s], x) * _to_signed_int(o.dsize_i[s], y), tx, ty) if type(o) is hw.SIMD_SignedMultiplier else
                                gen_simd_data_int_2(o, s, lambda x, y: x // y if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_Divider else
                                gen_simd_data_int_2(o, s, lambda x, y: _div(_to_signed_int(o.dsize_i[s], x), _to_signed_int(o.dsize_i[s], y)) if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_SignedDivider else
                                gen_simd_data_int_2(o, s, lambda x, y: x % y if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_Remainder else
                                gen_simd_data_int_2(o, s, lambda x, y: _rem(_to_signed_int(o.dsize_i[s], x), _to_signed_int(o.dsize_i[s], y)) if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_SignedRemainder else
                                gen_simd_data_int_2(o, s, lambda x, y: _cmp(x, y), tx, ty) if type(o) is hw.SIMD_Comparator else
                                gen_simd_data_int_2(o, s, lambda x, y: _cmp(_to_signed_int(o.dsize_i[s], x), _to_signed_int(o.dsize_i[s], y)), tx, ty) if type(o) is hw.SIMD_SignedComparator else
                                gen_simd_data_int_1(o, s, lambda x: x, tx) if type(o) is hw.SIMD_IntegerConverter else
                                gen_simd_data_int_1(o, s, lambda x: _to_signed_int(o.dsize_i[s], x), tx) if type(o) is hw.SIMD_SignedIntegerConverter else
                                0
                            ) if isinstance(o, SIMD_Operator) else (
                                x if type(o) is hw.Buffer else
                                (~x) if type(o) is hw.Inverter else
                                (x & y) if type(o) is hw.ANDGate else
                                (x | y) if type(o) is hw.ORGate else
                                (x ^ y) if type(o) is hw.XORGate else
                                (~(x & y)) if type(o) is hw.NANDGate else
                                (~(x | y)) if type(o) is hw.NORGate else
                                (~(x ^ y)) if type(o) is hw.XNORGate else
                                (x << y) if type(o) is hw.LeftShifter else
                                (x >> y) if type(o) is hw.RightShifter else
                                (_to_signed_int(o.width_i, x) >> y) if type(o) is hw.ArithmeticRightShifter else
                                ((x << (y % o.width_o)) | (x >> (o.width_o - y % o.width_o))) if type(o) is hw.LeftRotator else
                                ((x >> (y % o.width_o)) | (x << (o.width_o - y % o.width_o))) if type(o) is hw.RightRotator else
                                p if type(o) is hw.PopulationCounter else
                                (o.width_i - r) if type(o) is hw.LeadingZeroCounter else
                                t if type(o) is hw.TrailingZeroCounter else
                                (v << (o.width_o - 8)) if type(o) is hw.BitReverser else
                                (-x) if type(o) is hw.Negator else
                                (x + y + 1) if type(o) is hw.FullAdder else
                                (x - y - 1) if type(o) is hw.FullSubtractor else
                                (x * y) if type(o) is hw.Multiplier else
                                (_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) if type(o) is hw.SignedMultiplier else
                                (x // y if y != 0 else 0) if type(o) is hw.Divider else
                                (_div(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedDivider else
                                (x % y if y != 0 else 0) if type(o) is hw.Remainder else
                                (_rem(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedRemainder else
                                _cmp(x, y) if type(o) is hw.Comparator else
                                _cmp(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if type(o) is hw.SignedComparator else
                                x if type(o) is hw.IntegerConverter else
                                _to_signed_int(o.width_i, x) if type(o) is hw.SignedIntegerConverter else
                                int.from_bytes(test_lut[x]) if type(o) is hw.LookupTable else
                                0
                            )
                        ) & ((1 << o.width_o) - 1)).to_bytes((dev.width_o + 7) >> 3)
                        for o, s, x, tx, y, ty, p, tp, r, tr, t, tt, v, tv in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ax[i % 3], (ax[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ay[(i // 3) % 3], (ay[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axp[i % 3], (axp[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axr[i % 3], (axr[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axt[i % 3], (axt[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axv[i % 3], (axv[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_co
                (
                    cast(Word, [
                        (
                            (0 if ((x + y + 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullAdder else
                            (0 if ((x - y - 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullSubtractor else
                            0
                        ).to_bytes(1)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_e
                (
                    cast(Word, [
                        (
                            reduce(lambda a, b: a | b, (
                                (
                                    (0 if ((x * y) >> o.dsize_o[s]) == 0 else 1) if type(o) is hw.SIMD_Multiplier else
                                    (0 if ((_to_signed_int(o.dsize_i[s], x) * _to_signed_int(o.dsize_i[s], y)) >> o.dsize_o[s]) in [0, -1] else 1) if type(o) is hw.SIMD_SignedMultiplier else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_Divider else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_SignedDivider else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_Remainder else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_SignedRemainder else
                                    0
                                )
                                for x, y in zip(tx, ty)
                            ), 0) if isinstance(o, SIMD_Operator) else (
                                (0 if ((x * y) >> o.width_o) == 0 else 1) if type(o) is hw.Multiplier else
                                (0 if ((_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) >> o.width_o) in [0, -1] else 1) if type(o) is hw.SignedMultiplier else
                                (0 if y != 0 else 1) if type(o) is hw.Divider else
                                (0 if y != 0 else 1) if type(o) is hw.SignedDivider else
                                (0 if y != 0 else 1) if type(o) is hw.Remainder else
                                (0 if y != 0 else 1) if type(o) is hw.SignedRemainder else
                                0
                            )
                        ).to_bytes(1)
                        for o, s, x, tx, y, ty in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ax[i % 3], (ax[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ay[(i // 3) % 3], (ay[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_fe_o
                (b'\x00' if wfe > 0 else b'', 1e-9)
            ]
        ]
    )
    po: list[ChannelProbe] = [ChannelProbe(s, w) for s, w in [('out', wo), ('co', 1), ('e', 1), ('fe', wfe)]]
    ti: list[Source] = [Source(w, d) for w, d in zip([wi, wi, wop, ws, 1, wft, wfr, wfe], t[0])]
    to: list[Drain] = [Drain(w) for w in [wo, 1, 1, wfe]]
    for i, p in enumerate([dev.ports_i[0], dev.ports_i[1], dev.port_op, dev.port_s, dev.port_ci, dev.port_ft, dev.port_fr, dev.port_fe_i]):
        ti[i].port_o.connect(p)
    for i, q in enumerate([dev.port_o, dev.port_co, dev.port_e, dev.port_fe_o]):
        q.connect(to[i].port_i)
        q.add_probe(po[i])
    sim: Simulator = Simulator([*ti, *to, dev])
    sim.start(max_iter=10000, show_time=True)
    for ro, a in zip(po, t[1]):
        rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
        assert len(ro) == len(rp)
        for ru, rv in zip(ro, rp):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


@skipif_unavailable
def test_FPFullArithmeticLogicUnit() -> None:
    test_lut: list[bytes] = [
        ((math.ceil(math.sin(i + 3) * (1 << 20))) & ((1 << 16) - 1)).to_bytes((16 + 7) >> 3)
        for i in range(1 << 8)
    ]
    dev: FullArithmeticLogicUnit = FullArithmeticLogicUnit(
        [8, 16, 64, 128],
        use_int=True, use_fp=True, use_fp_riscv=True,
        add_ops=[hw.LookupTable(8, 16, test_lut)]
    )
    wi: int = dev.width_i
    wo: int = dev.width_o
    ws: int = dev.width_s
    wop: int = dev.width_op
    wft: int = dev.width_ft
    wfr: int = dev.width_fr
    wfe: int = dev.width_fe
    ax: list[int] = [0x83, 0x05, 0x70]
    ay: list[int] = [0xf3, 0x00, 0x03]
    az: list[int] = [0x01, 0x81, 0x04]
    af: list[float] = [-2.0, 5.0, 2.0]
    ag: list[float] = [-4.0, 0.0, 1.0]
    ah: list[float] = [2.0, -3.0, 4.0]
    axp: list[int] = [3, 2, 3]  # population count
    axr: list[int] = [8, 3, 7]  # required bit count
    axt: list[int] = [0, 0, 4]  # trailing zeros
    axv: list[int] = [0xc1, 0xa0, 0x0e]  # bit reversal
    sf.set_tininess_mode(fp.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(fp.RoundingMode.MIN)
    m: int = 9 * len(dev.ops)
    t: tuple[list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]] = (
        [
            [  # ports_i[0]
                (
                    ax[i % 3].to_bytes((wi + 7) >> 3) if not _is_fp_input_op(dev.ops[i // 9]) else
                    b'\x00' * ((wi - 16) // 8) + fp.Float16.from_float(af[i % 3]).to_bytes() if dev.ops[i // 9].width_i == 16 else
                    b'\x00' * ((wi - 32) // 8) + fp.Float32.from_float(af[i % 3]).to_bytes() if dev.ops[i // 9].width_i == 32 else
                    b'\x00' * ((wi - 64) // 8) + fp.Float64.from_float(af[i % 3]).to_bytes() if dev.ops[i // 9].width_i == 64 else
                    fp.Float128.from_float(af[i % 3]).to_bytes() if dev.ops[i // 9].width_i == 128 else
                    b'\x00' * (wi // 8),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # ports_i[1]
                (
                    ay[(i // 3) % 3].to_bytes((wi + 7) >> 3) if not _is_fp_input_op(dev.ops[i // 9]) else
                    b'\x00' * ((wi - 16) // 8) + fp.Float16.from_float(ag[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 16 else
                    b'\x00' * ((wi - 32) // 8) + fp.Float32.from_float(ag[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 32 else
                    b'\x00' * ((wi - 64) // 8) + fp.Float64.from_float(ag[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 64 else
                    fp.Float128.from_float(ag[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 128 else
                    b'\x00' * (wi // 8),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # ports_i[2]
                (
                    az[(i // 3) % 3].to_bytes((wi + 7) >> 3) if not _is_fp_input_op(dev.ops[i // 9]) else
                    b'\x00' * ((wi - 16) // 8) + fp.Float16.from_float(ah[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 16 else
                    b'\x00' * ((wi - 32) // 8) + fp.Float32.from_float(ah[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 32 else
                    b'\x00' * ((wi - 64) // 8) + fp.Float64.from_float(ah[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 64 else
                    fp.Float128.from_float(ah[(i // 3) % 3]).to_bytes() if dev.ops[i // 9].width_i == 128 else
                    b'\x00' * (wi // 8),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_op
                ((i // 9).to_bytes((wop + 7) >> 3), 1e-9 * (1 + i)) for i in range(m)
            ],
            [],  # port_s
            [  # port_ci
                (b'\x01', 0.0)
            ],
            [  # port_ft
                (sf.get_tininess_mode().value.to_bytes(1), 0.0)
            ],
            [  # port_fr
                (sf.get_rounding_mode().value.to_bytes(1), 0.0)
            ],
            [  # port_fe_i
                (b'\x00', 0.0)
            ]
        ],
        [
            [  # port_o
                (
                    cast(Word, [
                        ((
                            x if type(o) is hw.Buffer else
                            (~x) if type(o) is hw.Inverter else
                            (x & y) if type(o) is hw.ANDGate else
                            (x | y) if type(o) is hw.ORGate else
                            (x ^ y) if type(o) is hw.XORGate else
                            (~(x & y)) if type(o) is hw.NANDGate else
                            (~(x | y)) if type(o) is hw.NORGate else
                            (~(x ^ y)) if type(o) is hw.XNORGate else
                            (x << y) if type(o) is hw.LeftShifter else
                            (x >> y) if type(o) is hw.RightShifter else
                            (_to_signed_int(o.width_i, x) >> y) if type(o) is hw.ArithmeticRightShifter else
                            ((x << (y % o.width_o)) | (x >> (o.width_o - y % o.width_o))) if type(o) is hw.LeftRotator else
                            ((x >> (y % o.width_o)) | (x << (o.width_o - y % o.width_o))) if type(o) is hw.RightRotator else
                            axp[i % 3] if type(o) is hw.PopulationCounter else
                            (o.width_i - axr[i % 3]) if type(o) is hw.LeadingZeroCounter else
                            axt[i % 3] if type(o) is hw.TrailingZeroCounter else
                            (axv[i % 3] << (o.width_o - 8)) if type(o) is hw.BitReverser else
                            (-x) if type(o) is hw.Negator else
                            (x + y + 1) if type(o) is hw.FullAdder else
                            (x - y - 1) if type(o) is hw.FullSubtractor else
                            (x * y) if type(o) is hw.Multiplier else
                            (_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) if type(o) is hw.SignedMultiplier else
                            (x // y if y != 0 else 0) if type(o) is hw.Divider else
                            (_div(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedDivider else
                            (x % y if y != 0 else 0) if type(o) is hw.Remainder else
                            (_rem(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedRemainder else
                            _cmp(x, y) if type(o) is hw.Comparator else
                            _cmp(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if type(o) is hw.SignedComparator else
                            x if type(o) is hw.IntegerConverter else
                            _to_signed_int(o.width_i, x) if type(o) is hw.SignedIntegerConverter else
                            int.from_bytes(_fp_neg(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPNegator else
                            int.from_bytes(_fp_add(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPAdder else
                            int.from_bytes(_fp_sub(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPSubtractor else
                            int.from_bytes(_fp_mul(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPMultiplier else
                            int.from_bytes(_fp_mul_add(fp.dsize_to_dtype(o.width_i), f, g, h)) if type(o) is fp.FPMultiplyAdder else
                            int.from_bytes(_fp_div(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPDivider else
                            int.from_bytes(_fp_rem(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPRemainder else
                            int.from_bytes(_fp_sqrt(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPSquareRoot else
                            int.from_bytes(_fp_cmp(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPComparator else
                            0 if type(o) is fp.FPClassifier else
                            int.from_bytes(_fp_round_to_int(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPToIntegerRounder else
                            int.from_bytes(_fp_from_ui64(fp.dsize_to_dtype(o.width_o), x)) if type(o) is fp.FPFromIntegerConverter else
                            int.from_bytes(_fp_from_i64(fp.dsize_to_dtype(o.width_o), _to_signed_int(o.width_i, x))) if type(o) is fp.FPFromSignedIntegerConverter else
                            int.from_bytes(_fp_to_ui64(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPToIntegerConverter else
                            int.from_bytes(_fp_to_i64(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPToSignedIntegerConverter else
                            int.from_bytes(_fp_to_fp(fp.dsize_to_dtype(o.width_i), fp.dsize_to_dtype(o.width_o), f)) if type(o) is fp.FPConverter else
                            int.from_bytes(_fp_frec7(fp.dsize_to_dtype(o.width_i), f)) if type(o) is riscv.FRec7 else
                            int.from_bytes(_fp_frsqrt7(fp.dsize_to_dtype(o.width_i), f)) if type(o) is riscv.FRSqrt7 else
                            int.from_bytes(test_lut[x]) if type(o) is hw.LookupTable else
                            0
                        ) & ((1 << o.width_o) - 1)).to_bytes((dev.width_o + 7) >> 3)
                        for o, x, y, f, g, h in [(
                            dev.ops[i // 9],
                            ax[i % 3], ay[(i // 3) % 3],
                            af[i % 3], ag[(i // 3) % 3], ah[(i // 3) % 3]
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_co
                (
                    cast(Word, [
                        (
                            (0 if ((x + y + 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullAdder else
                            (0 if ((x - y - 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullSubtractor else
                            0
                        ).to_bytes(1)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_e
                (
                    cast(Word, [
                        (
                            (0 if ((x * y) >> o.width_o) == 0 else 1) if type(o) is hw.Multiplier else
                            (0 if ((_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) >> o.width_o) in [0, -1] else 1) if type(o) is hw.SignedMultiplier else
                            (0 if y != 0 else 1) if type(o) is hw.Divider else
                            (0 if y != 0 else 1) if type(o) is hw.SignedDivider else
                            (0 if y != 0 else 1) if type(o) is hw.Remainder else
                            (0 if y != 0 else 1) if type(o) is hw.SignedRemainder else
                            0
                        ).to_bytes(1)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_fe_o
                (
                    cast(Word, [
                        (
                            fp.ExceptionFlag.INFINITE if type(o) is fp.FPDivider and g == 0.0 else
                            fp.ExceptionFlag.INVALID if type(o) is fp.FPRemainder and g == 0.0 else
                            (fp.ExceptionFlag.INVALID if f < 0.0 else fp.ExceptionFlag.INEXACT) if type(o) is fp.FPSquareRoot else
                            fp.ExceptionFlag.INVALID if type(o) is fp.FPToIntegerConverter and f < 0.0 else
                            fp.ExceptionFlag.INVALID if type(o) is riscv.FRSqrt7 and f < 0.0 else
                            0
                        ).to_bytes(1)
                        for o, f, g in [(dev.ops[i // 9], af[i % 3], ag[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ]
        ]
    )
    sf.set_rounding_mode(fp.RoundingMode.MAX)  # set an option different from intended one
    po: list[ChannelProbe] = [ChannelProbe(s, w) for s, w in [('out', wo), ('co', 1), ('e', 1), ('fe', wfe)]]
    ti: list[Source] = [Source(w, d) for w, d in zip([wi, wi, wi, wop, ws, 1, wft, wfr, wfe], t[0])]
    to: list[Drain] = [Drain(w) for w in [wo, 1, 1, wfe]]
    for i, p in enumerate([*dev.ports_i[:3], dev.port_op, dev.port_s, dev.port_ci, dev.port_ft, dev.port_fr, dev.port_fe_i]):
        ti[i].port_o.connect(p)
    for i, q in enumerate([dev.port_o, dev.port_co, dev.port_e, dev.port_fe_o]):
        q.connect(to[i].port_i)
        q.add_probe(po[i])
    sim: Simulator = Simulator([*ti, *to, dev])
    sim.start(max_iter=10000, show_time=True)
    for ro, a in zip(po, t[1]):
        rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
        assert len(ro) == len(rp)
        for ru, rv in zip(ro, rp):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS


@skipif_unavailable
def test_SIMD_FPFullArithmeticLogicUnit() -> None:

    def gen_simd_data_int_1(o: SIMD_Operator, s: int, f: Callable[[int], int], ax: Iterable[int]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (f(x) for x in ax), 0)

    def gen_simd_data_int_2(o: SIMD_Operator, s: int, f: Callable[[int, int], int], ax: Iterable[int], ay: Iterable[int]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (f(x, y) for x, y in zip(ax, ay)), 0)

    def gen_simd_data_fp_1(o: SIMD_Operator, s: int, f: Callable[[float], bytes], ax: Iterable[float]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (int.from_bytes(f(x)) for x in ax), 0)

    def gen_simd_data_fp_2(o: SIMD_Operator, s: int, f: Callable[[float, float], bytes], ax: Iterable[float], ay: Iterable[float]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (int.from_bytes(f(x, y)) for x, y in zip(ax, ay)), 0)

    def gen_simd_data_fp_3(o: SIMD_Operator, s: int, f: Callable[[float, float, float], bytes], ax: Iterable[float], ay: Iterable[float], az: Iterable[float]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (int.from_bytes(f(x, y, z)) for x, y, z in zip(ax, ay, az)), 0)

    def gen_simd_data_int_fp(o: SIMD_Operator, s: int, f: Callable[[int], bytes], ax: Iterable[int]) -> int:
        return reduce(lambda a, b: (a << o.dsize_o[s]) | (b & ((1 << o.dsize_o[s]) - 1)), (int.from_bytes(f(x)) for x in ax), 0)

    test_lut: list[bytes] = [
        ((math.ceil(math.sin(i + 3) * (1 << 20))) & ((1 << 16) - 1)).to_bytes((16 + 7) >> 3)
        for i in range(1 << 8)
    ]
    dev: SIMD_FullArithmeticLogicUnit = SIMD_FullArithmeticLogicUnit(
        128, [8, 32, 128],
        use_int=True, use_fp=True, use_fp_riscv=True,
        add_ops=[hw.LookupTable(8, 16, test_lut)]
    )
    wi: int = dev.width_i
    wo: int = dev.width_o
    ws: int = dev.width_s
    wop: int = dev.width_op
    wft: int = dev.width_ft
    wfr: int = dev.width_fr
    wfe: int = dev.width_fe
    ax: list[int] = [0x83, 0x05, 0x70]
    ay: list[int] = [0xf3, 0x00, 0x03]
    az: list[int] = [0x01, 0x81, 0x04]
    af: list[float] = [-2.0, 5.0, 2.0]
    ag: list[float] = [-4.0, 0.0, 1.0]
    ah: list[float] = [2.0, -3.0, 4.0]
    axp: list[int] = [3, 2, 3]  # population count
    axr: list[int] = [8, 3, 7]  # required bit count
    axt: list[int] = [0, 0, 4]  # trailing zeros
    axv: list[int] = [0xc1, 0xa0, 0x0e]  # bit reversal
    sf.set_tininess_mode(fp.TininessMode.AFTER_ROUNDING)
    sf.set_rounding_mode(fp.RoundingMode.MIN)
    m: int = 9 * len(dev.ops)
    t: tuple[list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]] = (
        [
            [  # ports_i[0]
                (
                    cast(Word, [
                        ((
                            reduce(lambda a, b: (a << o.dsize_i[s]) | (b & ((1 << o.dsize_i[s]) - 1)), (
                                tx if not _is_fp_input_op(o) else [int.from_bytes(fp.dsize_to_dtype(o.dsize_i[s]).from_float(f).to_bytes()) for f in tf]
                            ), 0) if isinstance(o, SIMD_Operator) else (
                                x if not _is_fp_input_op(o) else int.from_bytes(fp.dsize_to_dtype(o.width_i).from_float(f).to_bytes())
                            )
                        ) & ((1 << o.width_i) - 1)).to_bytes((dev.width_i + 7) >> 3)
                        for o, s, x, tx, f, tf in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ax[i % 3], (ax[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            af[i % 3], (af[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # ports_i[1]
                (
                    cast(Word, [
                        ((
                            reduce(lambda a, b: (a << o.dsize_i[s]) | (b & ((1 << o.dsize_i[s]) - 1)), (
                                ty if not _is_fp_input_op(o) else [int.from_bytes(fp.dsize_to_dtype(o.dsize_i[s]).from_float(g).to_bytes()) for g in tg]
                            ), 0) if isinstance(o, SIMD_Operator) else (
                                y if not _is_fp_input_op(o) else int.from_bytes(fp.dsize_to_dtype(o.width_i).from_float(g).to_bytes())
                            )
                        ) & ((1 << o.width_i) - 1)).to_bytes((dev.width_i + 7) >> 3)
                        for o, s, y, ty, g, tg in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ay[(i // 3) % 3], (ay[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ag[(i // 3) % 3], (ag[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # ports_i[2]
                (
                    cast(Word, [
                        ((
                            reduce(lambda a, b: (a << o.dsize_i[s]) | (b & ((1 << o.dsize_i[s]) - 1)), (
                                tz if not _is_fp_input_op(o) else [int.from_bytes(fp.dsize_to_dtype(o.dsize_i[s]).from_float(h).to_bytes()) for h in th]
                            ), 0) if isinstance(o, SIMD_Operator) else (
                                z if not _is_fp_input_op(o) else int.from_bytes(fp.dsize_to_dtype(o.width_i).from_float(h).to_bytes())
                            )
                        ) & ((1 << o.width_i) - 1)).to_bytes((dev.width_i + 7) >> 3)
                        for o, s, z, tz, h, th in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            az[(i // 3) % 3], (az[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ah[(i // 3) % 3], (ah[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_op
                ((i // 9).to_bytes((wop + 7) >> 3), 1e-9 * (1 + i)) for i in range(m)
            ],
            [  # port_s
                (
                    (_simd_selection_by_index(dev, i // 9, i // 3)).to_bytes((ws + 7) >> 3),
                    1e-9 * (1 + i)
                ) for i in range(m)
            ],
            [  # port_ci
                (b'\x01', 0.0)
            ],
            [  # port_ft
                (sf.get_tininess_mode().value.to_bytes(1), 0.0)
            ],
            [  # port_fr
                (sf.get_rounding_mode().value.to_bytes(1), 0.0)
            ],
            [  # port_fe_i
                (b'\x00', 0.0)
            ]
        ],
        [
            [  # port_o
                (
                    cast(Word, [
                        ((
                            (
                                gen_simd_data_int_2(o, s, lambda x, y: x << y, tx, ty) if type(o) is hw.SIMD_LeftShifter else
                                gen_simd_data_int_2(o, s, lambda x, y: x >> y, tx, ty) if type(o) is hw.SIMD_RightShifter else
                                gen_simd_data_int_2(o, s, lambda x, y: _to_signed_int(o.dsize_i[s], x) >> y, tx, ty) if type(o) is hw.SIMD_ArithmeticRightShifter else
                                gen_simd_data_int_2(o, s, lambda x, y: (x << (y % o.dsize_o[s])) | (x >> (o.dsize_o[s] - y % o.dsize_o[s])), tx, ty) if type(o) is hw.SIMD_LeftRotator else
                                gen_simd_data_int_2(o, s, lambda x, y: (x >> (y % o.dsize_o[s])) | (x << (o.dsize_o[s] - y % o.dsize_o[s])), tx, ty) if type(o) is hw.SIMD_RightRotator else
                                gen_simd_data_int_1(o, s, lambda p: p, tp) if type(o) is hw.SIMD_PopulationCounter else
                                gen_simd_data_int_1(o, s, lambda r: o.dsize_o[s] - r, tr) if type(o) is hw.SIMD_LeadingZeroCounter else
                                gen_simd_data_int_1(o, s, lambda t: t, tt) if type(o) is hw.SIMD_TrailingZeroCounter else
                                gen_simd_data_int_1(o, s, lambda v: v << (o.dsize_o[s] - 8), tv) if type(o) is hw.SIMD_BitReverser else
                                gen_simd_data_int_1(o, s, lambda x: -x, tx) if type(o) is hw.SIMD_Negator else
                                gen_simd_data_int_2(o, s, lambda x, y: x + y, tx, ty) if type(o) is hw.SIMD_Adder else
                                gen_simd_data_int_2(o, s, lambda x, y: x - y, tx, ty) if type(o) is hw.SIMD_Subtractor else
                                gen_simd_data_int_2(o, s, lambda x, y: x * y, tx, ty) if type(o) is hw.SIMD_Multiplier else
                                gen_simd_data_int_2(o, s, lambda x, y: _to_signed_int(o.dsize_i[s], x) * _to_signed_int(o.dsize_i[s], y), tx, ty) if type(o) is hw.SIMD_SignedMultiplier else
                                gen_simd_data_int_2(o, s, lambda x, y: x // y if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_Divider else
                                gen_simd_data_int_2(o, s, lambda x, y: _div(_to_signed_int(o.dsize_i[s], x), _to_signed_int(o.dsize_i[s], y)) if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_SignedDivider else
                                gen_simd_data_int_2(o, s, lambda x, y: x % y if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_Remainder else
                                gen_simd_data_int_2(o, s, lambda x, y: _rem(_to_signed_int(o.dsize_i[s], x), _to_signed_int(o.dsize_i[s], y)) if y != 0 else 0, tx, ty) if type(o) is hw.SIMD_SignedRemainder else
                                gen_simd_data_int_2(o, s, lambda x, y: _cmp(x, y), tx, ty) if type(o) is hw.SIMD_Comparator else
                                gen_simd_data_int_2(o, s, lambda x, y: _cmp(_to_signed_int(o.dsize_i[s], x), _to_signed_int(o.dsize_i[s], y)), tx, ty) if type(o) is hw.SIMD_SignedComparator else
                                gen_simd_data_int_1(o, s, lambda x: x, tx) if type(o) is hw.SIMD_IntegerConverter else
                                gen_simd_data_int_1(o, s, lambda x: _to_signed_int(o.dsize_i[s], x), tx) if type(o) is hw.SIMD_SignedIntegerConverter else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_neg(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is fp.SIMD_FPNegator else
                                gen_simd_data_fp_2(o, s, lambda f, g: _fp_add(fp.dsize_to_dtype(o.dsize_i[s]), f, g), tf, tg) if type(o) is fp.SIMD_FPAdder else
                                gen_simd_data_fp_2(o, s, lambda f, g: _fp_sub(fp.dsize_to_dtype(o.dsize_i[s]), f, g), tf, tg) if type(o) is fp.SIMD_FPSubtractor else
                                gen_simd_data_fp_2(o, s, lambda f, g: _fp_mul(fp.dsize_to_dtype(o.dsize_i[s]), f, g), tf, tg) if type(o) is fp.SIMD_FPMultiplier else
                                gen_simd_data_fp_3(o, s, lambda f, g, h: _fp_mul_add(fp.dsize_to_dtype(o.dsize_i[s]), f, g, h), tf, tg, th) if type(o) is fp.SIMD_FPMultiplyAdder else
                                gen_simd_data_fp_2(o, s, lambda f, g: _fp_div(fp.dsize_to_dtype(o.dsize_i[s]), f, g), tf, tg) if type(o) is fp.SIMD_FPDivider else
                                gen_simd_data_fp_2(o, s, lambda f, g: _fp_rem(fp.dsize_to_dtype(o.dsize_i[s]), f, g), tf, tg) if type(o) is fp.SIMD_FPRemainder else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_sqrt(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is fp.SIMD_FPSquareRoot else
                                gen_simd_data_fp_2(o, s, lambda f, g: _fp_cmp(fp.dsize_to_dtype(o.dsize_i[s]), f, g), tf, tg) if type(o) is fp.SIMD_FPComparator else
                                0 if type(o) is fp.SIMD_FPClassifier else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_round_to_int(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is fp.SIMD_FPToIntegerRounder else
                                gen_simd_data_int_fp(o, s, lambda x: _fp_from_ui64(fp.dsize_to_dtype(o.dsize_o[s]), x), tx) if type(o) is fp.SIMD_FPFromIntegerConverter else
                                gen_simd_data_int_fp(o, s, lambda x: _fp_from_i64(fp.dsize_to_dtype(o.dsize_o[s]), _to_signed_int(o.dsize_i[s], x)), tx) if type(o) is fp.SIMD_FPFromSignedIntegerConverter else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_to_ui64(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is fp.SIMD_FPToIntegerConverter else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_to_i64(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is fp.SIMD_FPToSignedIntegerConverter else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_to_fp(fp.dsize_to_dtype(o.dsize_i[s]), fp.dsize_to_dtype(o.dsize_o[s]), f), tf) if type(o) is fp.SIMD_FPConverter else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_frec7(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is riscv.SIMD_FRec7 else
                                gen_simd_data_fp_1(o, s, lambda f: _fp_frsqrt7(fp.dsize_to_dtype(o.dsize_i[s]), f), tf) if type(o) is riscv.SIMD_FRSqrt7 else
                                0
                            ) if isinstance(o, SIMD_Operator) else (
                                x if type(o) is hw.Buffer else
                                (~x) if type(o) is hw.Inverter else
                                (x & y) if type(o) is hw.ANDGate else
                                (x | y) if type(o) is hw.ORGate else
                                (x ^ y) if type(o) is hw.XORGate else
                                (~(x & y)) if type(o) is hw.NANDGate else
                                (~(x | y)) if type(o) is hw.NORGate else
                                (~(x ^ y)) if type(o) is hw.XNORGate else
                                (x << y) if type(o) is hw.LeftShifter else
                                (x >> y) if type(o) is hw.RightShifter else
                                (_to_signed_int(o.width_i, x) >> y) if type(o) is hw.ArithmeticRightShifter else
                                ((x << (y % o.width_o)) | (x >> (o.width_o - y % o.width_o))) if type(o) is hw.LeftRotator else
                                ((x >> (y % o.width_o)) | (x << (o.width_o - y % o.width_o))) if type(o) is hw.RightRotator else
                                p if type(o) is hw.PopulationCounter else
                                (o.width_i - r) if type(o) is hw.LeadingZeroCounter else
                                t if type(o) is hw.TrailingZeroCounter else
                                (v << (o.width_o - 8)) if type(o) is hw.BitReverser else
                                (-x) if type(o) is hw.Negator else
                                (x + y + 1) if type(o) is hw.FullAdder else
                                (x - y - 1) if type(o) is hw.FullSubtractor else
                                (x * y) if type(o) is hw.Multiplier else
                                (_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) if type(o) is hw.SignedMultiplier else
                                (x // y if y != 0 else 0) if type(o) is hw.Divider else
                                (_div(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedDivider else
                                (x % y if y != 0 else 0) if type(o) is hw.Remainder else
                                (_rem(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if y != 0 else 0) if type(o) is hw.SignedRemainder else
                                _cmp(x, y) if type(o) is hw.Comparator else
                                _cmp(_to_signed_int(o.width_i, x), _to_signed_int(o.width_i, y)) if type(o) is hw.SignedComparator else
                                x if type(o) is hw.IntegerConverter else
                                _to_signed_int(o.width_i, x) if type(o) is hw.SignedIntegerConverter else
                                int.from_bytes(_fp_neg(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPNegator else
                                int.from_bytes(_fp_add(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPAdder else
                                int.from_bytes(_fp_sub(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPSubtractor else
                                int.from_bytes(_fp_mul(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPMultiplier else
                                int.from_bytes(_fp_mul_add(fp.dsize_to_dtype(o.width_i), f, g, h)) if type(o) is fp.FPMultiplyAdder else
                                int.from_bytes(_fp_div(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPDivider else
                                int.from_bytes(_fp_rem(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPRemainder else
                                int.from_bytes(_fp_sqrt(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPSquareRoot else
                                int.from_bytes(_fp_cmp(fp.dsize_to_dtype(o.width_i), f, g)) if type(o) is fp.FPComparator else
                                0 if type(o) is fp.FPClassifier else
                                int.from_bytes(_fp_round_to_int(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPToIntegerRounder else
                                int.from_bytes(_fp_from_ui64(fp.dsize_to_dtype(o.width_o), x)) if type(o) is fp.FPFromIntegerConverter else
                                int.from_bytes(_fp_from_i64(fp.dsize_to_dtype(o.width_o), _to_signed_int(o.width_i, x))) if type(o) is fp.FPFromSignedIntegerConverter else
                                int.from_bytes(_fp_to_ui64(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPToIntegerConverter else
                                int.from_bytes(_fp_to_i64(fp.dsize_to_dtype(o.width_i), f)) if type(o) is fp.FPToSignedIntegerConverter else
                                int.from_bytes(_fp_to_fp(fp.dsize_to_dtype(o.width_i), fp.dsize_to_dtype(o.width_o), f)) if type(o) is fp.FPConverter else
                                int.from_bytes(_fp_frec7(fp.dsize_to_dtype(o.width_i), f)) if type(o) is riscv.FRec7 else
                                int.from_bytes(_fp_frsqrt7(fp.dsize_to_dtype(o.width_i), f)) if type(o) is riscv.FRSqrt7 else
                                int.from_bytes(test_lut[x]) if type(o) is hw.LookupTable else
                                0
                            )
                        ) & ((1 << o.width_o) - 1)).to_bytes((dev.width_o + 7) >> 3)
                        for o, s, x, tx, y, ty, p, tp, r, tr, t, tt, v, tv, f, tf, g, tg, h, th in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ax[i % 3], (ax[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ay[(i // 3) % 3], (ay[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axp[i % 3], (axp[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axr[i % 3], (axr[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axt[i % 3], (axt[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            axv[i % 3], (axv[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            af[i % 3], (af[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ag[(i // 3) % 3], (ag[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ah[(i // 3) % 3], (ah[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_co
                (
                    cast(Word, [
                        (
                            (0 if ((x + y + 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullAdder else
                            (0 if ((x - y - 1) >> o.width_o) == 0 else 1) if type(o) is hw.FullSubtractor else
                            0
                        ).to_bytes(1)
                        for o, x, y in [(dev.ops[i // 9], ax[i % 3], ay[(i // 3) % 3])]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_e
                (
                    cast(Word, [
                        (
                            reduce(lambda a, b: a | b, (
                                (
                                    (0 if ((x * y) >> o.dsize_o[s]) == 0 else 1) if type(o) is hw.SIMD_Multiplier else
                                    (0 if ((_to_signed_int(o.dsize_i[s], x) * _to_signed_int(o.dsize_i[s], y)) >> o.dsize_o[s]) in [0, -1] else 1) if type(o) is hw.SIMD_SignedMultiplier else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_Divider else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_SignedDivider else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_Remainder else
                                    (0 if y != 0 else 1) if type(o) is hw.SIMD_SignedRemainder else
                                    0
                                )
                                for x, y in zip(tx, ty)
                            ), 0) if isinstance(o, SIMD_Operator) else (
                                (0 if ((x * y) >> o.width_o) == 0 else 1) if type(o) is hw.Multiplier else
                                (0 if ((_to_signed_int(o.width_i, x) * _to_signed_int(o.width_i, y)) >> o.width_o) in [0, -1] else 1) if type(o) is hw.SignedMultiplier else
                                (0 if y != 0 else 1) if type(o) is hw.Divider else
                                (0 if y != 0 else 1) if type(o) is hw.SignedDivider else
                                (0 if y != 0 else 1) if type(o) is hw.Remainder else
                                (0 if y != 0 else 1) if type(o) is hw.SignedRemainder else
                                0
                            )
                        ).to_bytes(1)
                        for o, s, x, tx, y, ty in [(
                            dev.ops[i // 9], _simd_selection_by_index(dev, i // 9, i // 3),
                            ax[i % 3], (ax[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ay[(i // 3) % 3], (ay[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ],
            [  # port_fe_o
                (
                    cast(Word, [
                        (
                            reduce(lambda a, b: a | b, (
                                (
                                    fp.ExceptionFlag.INFINITE if type(o) is fp.SIMD_FPDivider and g == 0.0 else
                                    fp.ExceptionFlag.INVALID if type(o) is fp.SIMD_FPRemainder and g == 0.0 else
                                    (fp.ExceptionFlag.INVALID if f < 0.0 else fp.ExceptionFlag.INEXACT) if type(o) is fp.SIMD_FPSquareRoot else
                                    fp.ExceptionFlag.INVALID if type(o) is fp.SIMD_FPToIntegerConverter and f < 0.0 else
                                    fp.ExceptionFlag.INVALID if type(o) is riscv.SIMD_FRSqrt7 and f < 0.0 else
                                    0
                                )
                                for f, g in zip(tf, tg)
                            ), 0) if isinstance(o, SIMD_Operator) else (
                                fp.ExceptionFlag.INFINITE if type(o) is fp.FPDivider and g == 0.0 else
                                fp.ExceptionFlag.INVALID if type(o) is fp.FPRemainder and g == 0.0 else
                                (fp.ExceptionFlag.INVALID if f < 0.0 else fp.ExceptionFlag.INEXACT) if type(o) is fp.FPSquareRoot else
                                fp.ExceptionFlag.INVALID if type(o) is fp.FPToIntegerConverter and f < 0.0 else
                                fp.ExceptionFlag.INVALID if type(o) is riscv.FRSqrt7 and f < 0.0 else
                                0
                            )
                        ).to_bytes(1)
                        for o, f, tf, g, tg in [(
                            dev.ops[i // 9],
                            af[i % 3], (af[(i + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3))),
                            ag[(i // 3) % 3], (ag[((i // 3) + j) % 3] for j in range(_simd_word_count_by_index(dev, i // 9, i // 3)))
                        )]
                    ][0]),
                    1e-9 * (1 + i)
                )
                for i in range(m)
            ]
        ]
    )
    sf.set_rounding_mode(fp.RoundingMode.MAX)  # set an option different from intended one
    po: list[ChannelProbe] = [ChannelProbe(s, w) for s, w in [('out', wo), ('co', 1), ('e', 1), ('fe', wfe)]]
    ti: list[Source] = [Source(w, d) for w, d in zip([wi, wi, wi, wop, ws, 1, wft, wfr, wfe], t[0])]
    to: list[Drain] = [Drain(w) for w in [wo, 1, 1, wfe]]
    for i, p in enumerate([*dev.ports_i[:3], dev.port_op, dev.port_s, dev.port_ci, dev.port_ft, dev.port_fr, dev.port_fe_i]):
        ti[i].port_o.connect(p)
    for i, q in enumerate([dev.port_o, dev.port_co, dev.port_e, dev.port_fe_o]):
        q.connect(to[i].port_i)
        q.add_probe(po[i])
    sim: Simulator = Simulator([*ti, *to, dev])
    sim.start(max_iter=10000, show_time=True)
    for ro, a in zip(po, t[1]):
        rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
        assert len(ro) == len(rp)
        for ru, rv in zip(ro, rp):
            assert ru.word == rv[0]
            assert abs(ru.time - rv[1]) <= _EPS
