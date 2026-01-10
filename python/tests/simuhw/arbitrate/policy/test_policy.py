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

from random import Random

from simuhw import DataWord, Unknown
from simuhw.arbitrate.policy import (
    ArbitrationPolicy,
    RandomArbitrationPolicy, RoundRobinArbitrationPolicy,
    IndexOrderArbitrationPolicy, DataOrderArbitrationPolicy, TimeOrderArbitrationPolicy
)


def test_RandomArbitrationPolicy() -> None:
    n: int = 5
    s: int = 1000
    p: ArbitrationPolicy = RandomArbitrationPolicy(rng=Random(0))
    h: list[int] = [0 for _ in range(n)]
    for _ in range(s):
        h[p.select([(Unknown, 0.0) for _ in range(n)])] += 1
    for i in range(n):
        assert h[i] > (s // n) * 0.8
        assert h[i] < (s // n) * 1.2


def test_RoundRobinArbitrationPolicy() -> None:
    n: int = 5
    s: int = 1000
    p: ArbitrationPolicy = RoundRobinArbitrationPolicy(initial=2)
    for i in range(s):
        assert p.select([(Unknown, 0.0) for _ in range(n)]) == (2 + i) % n


def test_IndexOrderArbitrationPolicy() -> None:
    n: int = 5
    s: int = 1000
    for b in [True, False]:
        p: ArbitrationPolicy = IndexOrderArbitrationPolicy(select_min=b)
        i: int = 0 if b else n - 1
        for _ in range(s):
            assert p.select([(Unknown, 0.0) for _ in range(n)]) == i


def test_DataOrderArbitrationPolicy() -> None:
    test_data: list[tuple[list[tuple[DataWord, float]], list[list[int]]]] = [
        ([(b'\x10', 0.0)], [[0, 0], [0, 0]]),
        ([(b'\x20', 0.0), (b'\x10', 0.0)], [[1, 0], [1, 0]]),
        ([(b'\x20', 0.0), (b'\x30', 0.0), (b'\x00', 0.0), (b'\x40', 0.0), (b'\x10', 0.0)], [[2, 3], [2, 3]]),
        ([(b'\x20', 0.0), (b'\x40', 0.0), (b'\x20', 0.0), (b'\x40', 0.0), (b'\x20', 0.0)], [[4, 3], [4, 3]]),
        ([(Unknown, 0.0)], [[0, 0], [0, 0]]),
        ([(b'\x20', 0.0), (Unknown, 0.0)], [[1, 1], [0, 0]]),
        ([(b'\x20', 0.0), (Unknown, 0.0), (Unknown, 0.0), (b'\x40', 0.0), (b'\x10', 0.0)], [[2, 2], [4, 3]]),
        ([(Unknown, 0.0), (b'\x40', 0.0), (Unknown, 0.0), (b'\x40', 0.0), (Unknown, 0.0)], [[4, 4], [3, 3]]),
        ([(Unknown, 0.0), (Unknown, 0.0), (Unknown, 0.0), (Unknown, 0.0), (Unknown, 0.0)], [[4, 4], [4, 4]])
    ]
    for i, a in enumerate([[Unknown], []]):
        for j, b in enumerate([True, False]):
            p: ArbitrationPolicy = DataOrderArbitrationPolicy(
                select_min=b, priority=a, when_same=IndexOrderArbitrationPolicy(select_min=False)
            )
            for t in test_data:
                assert p.select(t[0]) == t[1][i][j]


def test_TimeOrderArbitrationPolicy() -> None:
    test_data: list[tuple[list[tuple[DataWord, float]], list[int]]] = [
        ([(Unknown, 1.0)], [0, 0]),
        ([(Unknown, 2.0), (Unknown, 1.0)], [1, 0]),
        ([(Unknown, 2.0), (Unknown, 3.0), (Unknown, 0.0), (Unknown, 4.0), (Unknown, 1.0)], [2, 3]),
        ([(Unknown, 2.0), (Unknown, 4.0), (Unknown, 2.0), (Unknown, 4.0), (Unknown, 2.0)], [4, 3])
    ]
    for i, b in enumerate([True, False]):
        p: ArbitrationPolicy = TimeOrderArbitrationPolicy(
            select_min=b, when_same=IndexOrderArbitrationPolicy(select_min=False)
        )
        for t in test_data:
            assert p.select(t[0]) == t[1][i]
