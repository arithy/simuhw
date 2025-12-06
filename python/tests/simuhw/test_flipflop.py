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

from simuhw import Source, Drain, DFlipFlop, ChannelProbe, Simulator


def test_DFlipFlop() -> None:
    test_data: list[tuple[tuple[int, bool], list[tuple[bytes | None, float]], list[tuple[bytes | None, float]], list[tuple[bytes | None, float]]]] = [
        (
            (8, False),
            [(b'\x01', 3e-9), (b'\x00', 6e-9), (None, 9e-9), (b'\x00', 12e-9), (b'\x01', 15e-9), (b'\x00', 18e-9), (b'\x01', 21e-9)],
            [
                (b'\xc1', 1e-9), (b'\xc2', 2e-9),
                (b'\xc3', 4e-9), (b'\xc4', 5e-9),
                (b'\xc5', 7e-9), (b'\xc6', 8e-9),
                (b'\xc7', 10e-9), (b'\xc8', 11e-9),
                (b'\xc9', 13e-9), (b'\xca', 14e-9),
                (b'\xcb', 16e-9), (b'\xcc', 17e-9),
                (b'\xcd', 19e-9), (b'\xce', 20e-9),
                (b'\xcf', 22e-9), (b'\xd1', 23e-9)
            ],
            [
                (b'\xca', 15e-9), (b'\xce', 21e-9)
            ]
        ),
        (
            (8, True),
            [(b'\x00', 3e-9), (b'\x01', 6e-9), (None, 9e-9), (b'\x01', 12e-9), (b'\x00', 15e-9), (b'\x01', 18e-9), (b'\x00', 21e-9)],
            [
                (b'\xc1', 1e-9), (b'\xc2', 2e-9),
                (b'\xc3', 4e-9), (b'\xc4', 5e-9),
                (b'\xc5', 7e-9), (b'\xc6', 8e-9),
                (b'\xc7', 10e-9), (b'\xc8', 11e-9),
                (b'\xc9', 13e-9), (b'\xca', 14e-9),
                (b'\xcb', 16e-9), (b'\xcc', 17e-9),
                (b'\xcd', 19e-9), (b'\xce', 20e-9),
                (b'\xcf', 22e-9), (b'\xd1', 23e-9)
            ],
            [
                (b'\xca', 15e-9), (b'\xce', 21e-9)
            ]
        )
    ]
    for t in test_data:
        w: int = t[0][0]
        po: ChannelProbe = ChannelProbe('out', w)
        ti: list[Source] = [Source(1, t[1]), Source(w, t[2])]
        to: Drain = Drain(w)
        ff: DFlipFlop = DFlipFlop(w, neg_edged=t[0][1])
        ti[0].port_o.connect(ff.port_c)
        ti[1].port_o.connect(ff.port_i)
        ff.port_o.connect(to.port_i)
        ff.port_o.add_probe(po)
        sim: Simulator = Simulator(ti + [to, ff])
        sim.start(show_time=True)
        assert len(po.data) == len(t[3])
        for io, o in enumerate(po.data):
            assert o[0] == t[3][io][0]
            assert o[1] == t[3][io][1]
