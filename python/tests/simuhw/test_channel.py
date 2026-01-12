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

from simuhw import Word, Unknown, Source, Drain, Channel, ChannelProbe, Simulator

_EPS: float = 1e-18


def test_Channel() -> None:
    test_data: list[tuple[tuple[int, float, float], list[tuple[Word, float]], list[tuple[Word, float]]]] = [
        (
            (1, 2e-9, 1 / 3e-9),
            [
                (b'\x01', 1e-9), (b'\x00', 4e-9), (Unknown, 7e-9), (b'\x01', 10e-9), (b'\x00', 11e-9), (b'\x01', 12e-9),
                (b'\x00', 15e-9), (b'\x00', 16e-9), (b'\x01', 17e-9), (b'\x00', 24e-9)

            ],
            [
                (b'\x01', 6e-9), (b'\x00', 9e-9), (Unknown, 12e-9), (b'\x01', 15e-9), (Unknown, 16e-9),
                (b'\x00', 20e-9), (Unknown, 22e-9), (b'\x01', 25e-9), (b'\x00', 29e-9)
            ]
        ),
        (
            (9, 2e-9, 9 / 3e-9),
            [
                (b'\x01\xf1', 1e-9), (b'\x01\xf2', 4e-9), (Unknown, 7e-9), (b'\x01\xf3', 10e-9), (b'\x01\xf4', 11e-9), (b'\x01\xf5', 12e-9),
                (b'\x01\xf6', 15e-9), (b'\x01\xf6', 16e-9), (b'\x01\xf7', 17e-9), (b'\x01\xf8', 24e-9)
            ],
            [
                (b'\x01\xf1', 6e-9), (b'\x01\xf2', 9e-9), (Unknown, 12e-9), (b'\x01\xf3', 15e-9), (Unknown, 16e-9),
                (b'\x01\xf6', 20e-9), (Unknown, 22e-9), (b'\x01\xf7', 25e-9), (b'\x01\xf8', 29e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: Source = Source(w, t[1])
        to: Drain = Drain(w)
        dev: Channel = Channel(w, latency=t[0][1], throughput=t[0][2])
        dev.port_o.connect(to.port_i)
        ti.port_o.connect(dev.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([ti, to, dev])
        sim.start(show_time=True)
        r: list[tuple[Word, float]] = t[2]
        assert len(po) == len(r)
        for o, q in zip(po, r):
            assert o.word == q[0]
            assert abs(o.time - q[1]) <= _EPS
