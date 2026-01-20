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
from functools import reduce
import math

from simuhw import Word, Source, Drain, ChannelProbe, Simulator, Distributor, WordSplitter, WordCombiner
from simuhw.alu import ArithmeticLogicUnit74181, LookAheadCarryGenerator74182

_EPS: float = 1e-18


def test_ArithmeticLogicUnit74181() -> None:

    def f_nbytes(w: int) -> int:
        return (w + 7) >> 3

    def f_mask(w: int) -> int:
        return (1 << w) - 1

    def f_step(w: int) -> int:
        return 1 << (w + w + 6)

    def f_i0(w: int, i: int) -> int:
        return i & f_mask(w)

    def f_i1(w: int, i: int) -> int:
        return (i >> w) & f_mask(w)

    def f_s(w: int, i: int) -> int:
        return (i >> (w + w)) & 0x0f

    def f_s0(w: int, i: int) -> int:
        return (i >> (w + w)) & 1

    def f_s1(w: int, i: int) -> int:
        return (i >> (w + w + 1)) & 1

    def f_s2(w: int, i: int) -> int:
        return (i >> (w + w + 2)) & 1

    def f_s3(w: int, i: int) -> int:
        return (i >> (w + w + 3)) & 1

    def f_m(w: int, i: int) -> int:
        return (i >> (w + w + 4)) & 1

    def f_ci(w: int, i: int) -> int:
        return (i >> (w + w + 5)) & 1

    f: list[list[Callable[[int, int], int]]] = [
        [  # port_m == 1
            lambda a, b: ~a,
            lambda a, b: ~(a | b),
            lambda a, b: ~a & b,
            lambda a, b: 0,
            lambda a, b: ~(a & b),
            lambda a, b: ~b,
            lambda a, b: a ^ b,
            lambda a, b: a & ~b,
            lambda a, b: ~a | b,
            lambda a, b: ~(a ^ b),
            lambda a, b: b,
            lambda a, b: a & b,
            lambda a, b: -1,
            lambda a, b: a | ~b,
            lambda a, b: a | b,
            lambda a, b: a
        ],
        [  # port_m == 0, port_ci == 0
            lambda a, b: a + 1,
            lambda a, b: (a | b) + 1,
            lambda a, b: (a | ~b) + 1,
            lambda a, b: 0,
            lambda a, b: a + (a & ~b) + 1,
            lambda a, b: (a | b) + (a & ~b) + 1,
            lambda a, b: a - b,
            lambda a, b: a & ~b,
            lambda a, b: a + (a & b) + 1,
            lambda a, b: a + b + 1,
            lambda a, b: (a | ~b) + (a & b) + 1,
            lambda a, b: a & b,
            lambda a, b: a + a + 1,
            lambda a, b: (a | b) + a + 1,
            lambda a, b: (a | ~b) + a + 1,
            lambda a, b: a
        ],
        [  # port_m == 0, port_ci == 1
            lambda a, b: a,
            lambda a, b: a | b,
            lambda a, b: a | ~b,
            lambda a, b: -1,
            lambda a, b: a + (a & ~b),
            lambda a, b: (a | b) + (a & ~b),
            lambda a, b: a - b - 1,
            lambda a, b: (a & ~b) - 1,
            lambda a, b: a + (a & b),
            lambda a, b: a + b,
            lambda a, b: (a | ~b) + (a & b),
            lambda a, b: (a & b) - 1,
            lambda a, b: a + a,
            lambda a, b: (a | b) + a,
            lambda a, b: (a | ~b) + a,
            lambda a, b: a - 1
        ]
    ]
    test_data: list[tuple[int, list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]]] = [
        (
            w,
            [
                [  # ports_i[0]
                    (f_i0(w, i).to_bytes(f_nbytes(w)), 1e-9 * (1 + i))
                    for i in range(f_step(w))
                ],
                [  # ports_i[1]
                    (f_i1(w, i).to_bytes(f_nbytes(w)), 1e-9 * (1 + i))
                    for i in range(f_step(w))
                ],
                [  # port_s
                    (f_s(w, i).to_bytes(1), 1e-9 * (1 + i))
                    for i in range(f_step(w))
                ],
                [  # port_m
                    (f_m(w, i).to_bytes(1), 1e-9 * (1 + i))
                    for i in range(f_step(w))
                ],
                [  # port_ci
                    (f_ci(w, i).to_bytes(1), 1e-9 * (1 + i))
                    for i in range(f_step(w))
                ]
            ],
            [
                [  # port_o
                    (
                        (f[0 if f_m(w, i) == 1 else 1 + f_ci(w, i)][f_s(w, i)](f_i0(w, i), f_i1(w, i)) & f_mask(w)).to_bytes(f_nbytes(w)),
                        1e-9 * (1 + i)
                    )
                    for i in range(f_step(w))
                ],
                [  # port_co
                    (
                        ((~f[1 + f_ci(w, i)][f_s(w, i)](f_i0(w, i), f_i1(w, i)) >> w) & 1).to_bytes(1)  # in the case of addition
                        if f_s(w, i) == 9 else
                        (~(
                            [
                                reduce(lambda x, y: x & y, ((a01 >> j) for j in range(w)), 1)
                                for a01 in [
                                    [
                                        reduce(lambda x, y: x | y, ((o1 >> j) for j in range(1, w)), o0)
                                        for o0, o1 in [(
                                            a | (b & (f_s0(w, i) * f_mask(w))) | (~b & (f_s1(w, i) * f_mask(w))),
                                            (a & ~b & (f_s2(w, i) * f_mask(w))) | (a & b & (f_s3(w, i) * f_mask(w)))
                                        )]
                                    ][0]
                                    for a, b in [(f_i0(w, i), f_i1(w, i))]
                                ]
                            ][0] &
                            [
                                [
                                    reduce(lambda x, y: x | y, ((o1 >> j) for j in range(w)), ~f_ci(w, i) & 1) & 1
                                    for o1 in [(a & ~b & (f_s2(w, i) * f_mask(w))) | (a & b & (f_s3(w, i) * f_mask(w)))]
                                ][0]
                                for a, b in [(f_i0(w, i), f_i1(w, i))]
                            ][0]
                        ) & 1).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(f_step(w))
                ],
                [  # port_po
                    (
                        [
                            [
                                reduce(lambda x, y: x | y, ((o1 >> j) for j in range(w)), 0) & 1
                                for o1 in [(a & ~b & (f_s2(w, i) * f_mask(w))) | (a & b & (f_s3(w, i) * f_mask(w)))]
                            ][0]
                            for a, b in [(f_i0(w, i), f_i1(w, i))]
                        ][0].to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(f_step(w))
                ],
                [  # port_go
                    (
                        [
                            reduce(lambda x, y: x & y, ((a01 >> j) for j in range(w)), 1)
                            for a01 in [
                                [
                                    reduce(lambda x, y: x | y, ((o1 >> j) for j in range(1, w)), o0)
                                    for o0, o1 in [(
                                        a | (b & (f_s0(w, i) * f_mask(w))) | (~b & (f_s1(w, i) * f_mask(w))),
                                        (a & ~b & (f_s2(w, i) * f_mask(w))) | (a & b & (f_s3(w, i) * f_mask(w)))
                                    )]
                                ][0]
                                for a, b in [(f_i0(w, i), f_i1(w, i))]
                            ]
                        ][0].to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(f_step(w))
                ],
                [  # port_cmp
                    (
                        b'\x01' if (f[0 if f_m(w, i) == 1 else 1 + f_ci(w, i)][f_s(w, i)](
                            f_i0(w, i), f_i1(w, i)
                        ) & f_mask(w)) == f_mask(w) else b'\x00',
                        1e-9 * (1 + i)
                    )
                    for i in range(f_step(w))
                ]
            ]
        )
        for w in [1, 2, 3, 4, 5]
    ]
    for t in test_data:
        w: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe(s, w) for s, w in [('out', w), ('co', 1), ('p', 1), ('g', 1), ('cmp', 1)]]
        ti: list[Source] = [Source(w, d) for w, d in zip([w, w, 4, 1, 1], t[1])]
        to: list[Drain] = [Drain(w) for w in [w, 1, 1, 1, 1]]
        dev: ArithmeticLogicUnit74181 = ArithmeticLogicUnit74181(w)
        for i, p in enumerate([*dev.ports_i, dev.port_s, dev.port_m, dev.port_ci]):
            ti[i].port_o.connect(p)
        for i, q in enumerate([dev.port_o, dev.port_co, dev.port_po, dev.port_go, dev.port_cmp]):
            q.connect(to[i].port_i)
            q.add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for ro, a in zip(po, t[2]):
            rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS


def test_LookAheadCarryGenerator74182() -> None:
    test_data: list[tuple[int, list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]]] = [
        (
            n,
            [
                [  # port_ci
                    ((i & 1).to_bytes(1), 1e-9 * (1 + i))
                    for i in range(1 << (1 + n + n))
                ],
                *(  # ports_gi
                    cast(list[tuple[Word, float]], [
                        (((i >> (1 + j)) & 1).to_bytes(1), 1e-9 * (1 + i))
                        for i in range(1 << (1 + n + n))
                    ])
                    for j in range(n)
                ),
                *(  # ports_pi
                    cast(list[tuple[Word, float]], [
                        (((i >> (1 + n + j)) & 1).to_bytes(1), 1e-9 * (1 + i))
                        for i in range(1 << (1 + n + n))
                    ])
                    for j in range(n)
                )
            ],
            [
                *(  # ports_co
                    cast(list[tuple[Word, float]], [
                        (
                            (reduce(lambda x, y: x & y, (
                                reduce(lambda x, y: x | y, (((i >> (1 + n + k)) & 1) for k in range(l + 1, j)), ((i >> (1 + l)) & 1))
                                for l in range(j)
                            ), reduce(lambda x, y: x | y, (((i >> (1 + n + k)) & 1) for k in range(j)), (i & 1) ^ 1)) ^ 1).to_bytes(1),
                            1e-9 * (1 + i)
                        )
                        for i in range(1 << (1 + n + n))
                    ])
                    for j in range(1, n)
                ),
                [  # port_go
                    (
                        reduce(lambda x, y: x & y, (
                            reduce(lambda x, y: x | y, (((i >> (1 + n + k)) & 1) for k in range(j + 1, n)), ((i >> (1 + j)) & 1))
                            for j in range(n)
                        ), 1).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(1 << (1 + n + n))
                ],
                [  # port_po
                    (
                        reduce(lambda x, y: x | y, (((i >> (1 + n + j)) & 1) for j in range(n)), 0).to_bytes(1),
                        1e-9 * (1 + i)
                    )
                    for i in range(1 << (1 + n + n))
                ]
            ]
        )
        for n in [1, 2, 4, 7]
    ]
    for t in test_data:
        n: int = t[0]
        po: list[ChannelProbe] = [ChannelProbe(s, w) for s, w in [*((f'co{i}', 1) for i in range(0, n - 1)), ('go', 1), ('po', 1)]]
        ti: list[Source] = [Source(1, d) for d in t[1]]
        to: list[Drain] = [Drain(1) for _ in range(n + 1)]
        dev: LookAheadCarryGenerator74182 = LookAheadCarryGenerator74182(n)
        for i, p in enumerate([dev.port_ci, *dev.ports_gi, *dev.ports_pi]):
            ti[i].port_o.connect(p)
        for i, q in enumerate([*dev.ports_co, dev.port_go, dev.port_po]):
            q.connect(to[i].port_i)
            q.add_probe(po[i])
        sim: Simulator = Simulator([*ti, *to, dev])
        sim.start(show_time=True)
        for ro, a in zip(po, t[2]):
            rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS


def test_ArithmeticLogicUnit74181_With74182() -> None:
    num_bits: int = 16
    num_bytes: int = (num_bits + 7) >> 3
    mask: int = (1 << num_bits) - 1
    values: list[int] = sorted([*set(
        (k & mask)
        for j in range(num_bits + 1)
        for k in range((1 << j) - 2, (1 << j) + 3)
    )])
    num_values: int = len(values)
    test_data: list[tuple[list[int], list[list[tuple[Word, float]]], list[list[tuple[Word, float]]]]] = [
        (
            conf,
            [
                [
                    (values[i % num_values].to_bytes(num_bytes), 1e-9 * (1 + i))
                    for i in range(num_values * num_values)
                ],
                [
                    (values[i // num_values].to_bytes(num_bytes), 1e-9 * (1 + i))
                    for i in range(num_values * num_values)
                ]
            ],
            [
                [
                    (((values[i % num_values] + values[i // num_values]) & mask).to_bytes(num_bytes), 1e-9 * (1 + i))
                    for i in range(num_values * num_values)
                ]
            ]
        )
        for conf in [
            [16], [8, 2], [4, 4], [4, 2, 2], [2, 8], [2, 4, 2], [2, 2, 4], [2, 2, 2, 2]
        ]
    ]
    for t in test_data:
        if math.prod(t[0]) != num_bits:
            raise RuntimeError()
        po: list[ChannelProbe] = [ChannelProbe('out', num_bits)]
        ti: list[Source] = [Source(num_bits, d) for d in t[1]]
        ts: Source = Source(4, [(b'\x09', 0.0)])
        tm: Source = Source(1, [(b'\x00', 0.0)])
        tc: Source = Source(1, [(b'\x01', 0.0)])
        to: list[Drain] = [Drain(num_bits)]
        tg: Drain = Drain(1)
        tp: Drain = Drain(1)
        td: list[Drain] = [Drain(1) for _ in range(num_bits // t[0][0])]
        tr: list[Drain] = [Drain(1) for _ in range(num_bits // t[0][0])]
        alu: list[ArithmeticLogicUnit74181] = [ArithmeticLogicUnit74181(t[0][0]) for _ in range(num_bits // t[0][0])]
        lcg: list[list[LookAheadCarryGenerator74182]] = [
            [],
            *(
                [LookAheadCarryGenerator74182(t[0][il]) for _ in range(num_bits // math.prod(t[0][:il + 1]))]
                for il in range(1, len(t[0]))
            )
        ]
        spl: list[WordSplitter] = [WordSplitter([t[0][0]] * len(alu)) for _ in range(2)]
        cmb: WordCombiner = WordCombiner([t[0][0]] * len(alu))
        dst_s: Distributor = Distributor(4, len(alu))
        dst_m: Distributor = Distributor(1, len(alu))
        dst_c: list[list[list[Distributor]]] = [
            [], [],
            *(
                [
                    [Distributor(1, il) for _ in range(t[0][il] - 1)]
                    for _ in range(num_bits // math.prod(t[0][:il + 1]))
                ] if il < len(t[0]) else [
                    [Distributor(1, il)]
                ]
                for il in range(2, len(t[0]) + 1)
            )
        ]
        for i in range(2):
            ti[i].port_o.connect(spl[i].port_i)
            for q, u in zip(reversed(spl[i].ports_o), alu, strict=True):
                q.connect(u.ports_i[i])
        ts.port_o.connect(dst_s.port_i)
        for q, u in zip(dst_s.ports_o, alu, strict=True):
            q.connect(u.port_s)
        tm.port_o.connect(dst_m.port_i)
        for q, u in zip(dst_m.ports_o, alu, strict=True):
            q.connect(u.port_m)
        for d, u in zip(td, alu, strict=True):
            u.port_co.connect(d.port_i)
        for d, u in zip(tr, alu, strict=True):
            u.port_cmp.connect(d.port_i)
        for p, u in zip(reversed(cmb.ports_i), alu, strict=True):
            u.port_o.connect(p)
        cmb.port_o.connect(to[0].port_i)
        cmb.port_o.add_probe(po[0])
        for i, k in enumerate(range(0, num_bits, t[0][0])):
            for il in range(len(t[0]) - 1, -1, -1):
                n: int = math.prod(t[0][:il + 1])
                if k % n == 0:
                    m: int = math.prod(t[0][:il + 2])
                    ic: int = k // m
                    iq: int = 0
                    if il + 1 >= len(t[0]):
                        q = tc.port_o
                    else:
                        iq = (k // n) % t[0][il + 1] - 1
                        if iq < 0:
                            raise RuntimeError()
                        q = lcg[il + 1][ic].ports_co[iq]
                    if q.connected:
                        raise RuntimeError()
                    if il + 1 >= 2:
                        p = dst_c[il + 1][ic][iq].port_i
                        if p.connected:
                            raise RuntimeError()
                        q.connect(p)
                    for q, p in zip(
                        dst_c[il + 1][ic][iq].ports_o if il + 1 >= 2 else [q],
                        [(alu[i].port_ci if jl == 0 else lcg[jl][k // math.prod(t[0][:jl + 1])].port_ci) for jl in range(il + 1)],
                        strict=True
                    ):
                        if q.connected:
                            raise RuntimeError()
                        if p.connected:
                            raise RuntimeError()
                        q.connect(p)
                    break
        for il in range(len(t[0])):
            for q, p in zip(
                [q for d in alu for q in [d.port_go, d.port_po]] if il == 0 else [q for d in lcg[il] for q in [d.port_go, d.port_po]],
                [p for p in [tg.port_i, tp.port_i]] if il + 1 >= len(t[0]) else [p for d in lcg[il + 1] for i in range(d.ntargets) for p in [d.ports_gi[i], d.ports_pi[i]]],
                strict=True
            ):
                if q.connected:
                    raise RuntimeError()
                if p.connected:
                    raise RuntimeError()
                q.connect(p)
        if any((not d.port_o.connected for d in [*ti, ts, tm, tc])):
            raise RuntimeError()
        if any((not d.port_i.connected for d in [*to, tg, tp, *td, *tr])):
            raise RuntimeError()
        if any((not p.connected for d in alu for p in [*d.ports_i, d.port_s, d.port_m, d.port_ci])):
            raise RuntimeError()
        if any((not q.connected for d in alu for q in [d.port_o, d.port_co, d.port_go, d.port_po, d.port_cmp])):
            raise RuntimeError()
        if any((not p.connected for e in lcg for d in e for p in [d.port_ci, *d.ports_gi, *d.ports_pi])):
            raise RuntimeError()
        if any((not q.connected for e in lcg for d in e for q in [*d.ports_co, d.port_go, d.port_po])):
            raise RuntimeError()
        if any((not d.port_i.connected for d in spl)):
            raise RuntimeError()
        if any((not q.connected for d in spl for q in d.ports_o)):
            raise RuntimeError()
        if any((not p.connected for p in cmb.ports_i)):
            raise RuntimeError()
        if not cmb.port_o.connected:
            raise RuntimeError()
        if not dst_s.port_i.connected:
            raise RuntimeError()
        if any((not q.connected for q in dst_s.ports_o)):
            raise RuntimeError()
        if not dst_m.port_i.connected:
            raise RuntimeError()
        if any((not q.connected for q in dst_m.ports_o)):
            raise RuntimeError()
        if any((not d.port_i.connected for f in dst_c for e in f for d in e)):
            raise RuntimeError()
        if any((not q.connected for f in dst_c for e in f for d in e for q in d.ports_o)):
            raise RuntimeError()
        sim: Simulator = Simulator([
            *ti, ts, tm, tc, *to, tg, tp, *td, *tr,
            *alu, *(d for e in lcg for d in e), *spl,
            cmb, dst_s, dst_m, *(d for f in dst_c for e in f for d in e)
        ])
        sim.start(show_time=True)
        for ro, a in zip(po, t[2]):
            rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS
