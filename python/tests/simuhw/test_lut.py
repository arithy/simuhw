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

import math

from simuhw import DataWord, Source, Drain, LookupTable, ChannelProbe, Simulator

_EPS: float = 1e-18


def test_LookupTable() -> None:
    test_data: list[tuple[tuple[int, int], list[bytes], list[tuple[DataWord, float]], list[tuple[DataWord, float]]]] = [
        (
            (6, 11),
            [
                ((math.ceil(math.sin(i + 3) * (1 << 13))) & ((1 << 11) - 1)).to_bytes((11 + 7) >> 3)
                for i in range(1 << 6)
            ],
            [
                (i.to_bytes((6 + 7) >> 3), 1e-9 * (1 + i))
                for i in range(1 << 6)
            ],
            [
                (((math.ceil(math.sin(i + 3) * (1 << 13))) & ((1 << 11) - 1)).to_bytes((11 + 7) >> 3), 1e-9 * (1 + i))
                for i in range(1 << 6)
            ]
        )
    ]
    for t in test_data:
        wi: int = t[0][0]
        wo: int = t[0][1]
        po: ChannelProbe = ChannelProbe('out', wo)
        ti: Source = Source(wi, t[2])
        to: Drain = Drain(wo)
        dev: LookupTable = LookupTable(wi, wo, t[1])
        dev.port_o.connect(to.port_i)
        ti.port_o.connect(dev.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[DataWord, float]] = t[3]
        assert len(po.data) == len(r)
        for o, q in zip(po.data, r):
            assert o[0] == q[0]
            assert abs(o[1] - q[1]) <= _EPS
