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

from simuhw import Drain, Clock, ChannelProbe, Simulator


def test_Clock() -> None:
    EPS: float = 1e-6
    period: float = 4e-9
    duration: float = 20e-9 * (1.0 + EPS)
    for p in [0.0, 1e-9, 2e-9, 3e-9]:
        w: int = 1
        po: ChannelProbe = ChannelProbe('out', w)
        to: Drain = Drain(w)
        dev: Clock = Clock(period, phase=p)
        dev.port_o.connect(to.port_i)
        dev.port_o.add_probe(po)
        sim: Simulator = Simulator([to, dev])
        sim.start(show_time=True, duration=duration)
        if p < period * 0.5:
            assert len(po.data) == (duration - p) // (period * 0.5) + 1
            for io, o in enumerate(po.data):
                assert o[0] == ((io + 1) & 1).to_bytes(1)
                assert o[1] == p + period * 0.5 * io
        else:
            assert len(po.data) == (duration - p) // (period * 0.5) + 2
            for io, o in enumerate(po.data):
                assert o[0] == (io & 1).to_bytes(1)
                assert o[1] == p + period * 0.5 * (io - 1)
