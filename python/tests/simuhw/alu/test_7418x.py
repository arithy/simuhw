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

from collections.abc import Callable
from functools import reduce

from simuhw import Word, Source, Drain, ChannelProbe, Simulator
from simuhw.alu import ArithmeticLogicUnit74181

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
        sim.start(max_iter=None, show_time=True)
        for ro, a in zip(po, t[2]):
            rp: list[tuple[Word, float]] = [a[i] for i in range(len(a)) if i == 0 or a[i][0] != a[i - 1][0]]
            assert len(ro) == len(rp)
            for ru, rv in zip(ro, rp):
                assert ru.word == rv[0]
                assert abs(ru.time - rv[1]) <= _EPS
