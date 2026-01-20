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
from functools import reduce

from .._type import Unknown, Signal
from .._base import InputPort, OutputPort, Device


class LookAheadCarryGenerator74182(Device):
    """A look-ahead carry generator 74182 with arbitrary target slice ALUs.

    This device behaves like the logic IC 74182 with no timing delay and
    with arbitrary target slice ALUs.

    **Truth Tables:**

    Below is the tables when ``ntargets`` is 4.

    .. code-block:: text

        +-----------------------------------------+-------+
        |                 Inputs                  |Output |
        +-----+-----+-----+-----+-----+-----+-----+-------+
        | g3  | g2  | g1  | g0  | p3  | p2  | p1  |   g   |
        +-----+-----+-----+-----+-----+-----+-----+-------+
        |  L  |  X  |  X  |  X  |  X  |  X  |  X  |   L   |
        |  X  |  L  |  X  |  X  |  L  |  X  |  X  |   L   |
        |  X  |  X  |  L  |  X  |  L  |  L  |  X  |   L   |
        |  X  |  X  |  X  |  L  |  L  |  L  |  L  |   L   |
        |         all other combinations          |   H   |
        +-----------------------------------------+-------+

        +-----------------------+-------+
        |        Inputs         |Output |
        +-----+-----+-----+-----+-------+
        | p3  | p2  | p1  | p0  |   p   |
        +-----+-----+-----+-----+-------+
        |  L  |  L  |  L  |  L  |   L   |
        | all other combinations|   H   |
        +-----------------------+-------+

        +-----------------+-------+
        |     Inputs      |Output |
        +-----+-----+-----+-------+
        | g0  | p0  | ci  |  co0  |
        +-----+-----+-----+-------+
        |  L  |  X  |  X  |   H   |
        |  X  |  L  |  H  |   H   |
        | all other comb. |   L   |
        +-----------------+-------+

        +-----------------------------+-------+
        |           Inputs            |Output |
        +-----+-----+-----+-----+-----+-------+
        | g1  | g0  | p1  | p0  | ci  |  co1  |
        +-----+-----+-----+-----+-----+-------+
        |  L  |  X  |  X  |  X  |  X  |   H   |
        |  X  |  L  |  L  |  X  |  X  |   H   |
        |  X  |  X  |  L  |  L  |  H  |   H   |
        |   all other combinations    |   L   |
        +-----------------------------+-------+

        +-----------------------------------------+-------+
        |                 Inputs                  |Output |
        +-----+-----+-----+-----+-----+-----+-----+-------+
        | g2  | g1  | g0  | p2  | p1  | p0  | ci  |  co2  |
        +-----+-----+-----+-----+-----+-----+-----+-------+
        |  L  |  X  |  X  |  X  |  X  |  X  |  X  |   H   |
        |  X  |  L  |  X  |  L  |  X  |  X  |  X  |   H   |
        |  X  |  X  |  L  |  L  |  L  |  X  |  X  |   H   |
        |  X  |  X  |  X  |  L  |  L  |  L  |  H  |   H   |
        |         all other combinations          |   L   |
        +-----------------------------------------+-------+

    """

    def __init__(self, ntargets: int) -> None:
        """Creates a look-ahead carry generator 74182 with arbitrary target slice ALUs.

        Args:
            ntargets: The number of the target slice ALUs.

        """
        super().__init__()
        self._ntargets: int = ntargets
        """The number of the target slice ALUs."""
        self._port_ci: InputPort = InputPort(1)
        """The carry input port."""
        self._ports_gi: tuple[InputPort, ...] = tuple(InputPort(1) for _ in range(ntargets))
        """The carry generation input ports."""
        self._ports_pi: tuple[InputPort, ...] = tuple(InputPort(1) for _ in range(ntargets))
        """The carry propagation input ports."""
        self._ports_co: tuple[OutputPort, ...] = tuple(OutputPort(1) for _ in range(ntargets - 1))
        """The carry output ports."""
        self._port_go: OutputPort = OutputPort(1)
        """The carry generation output port."""
        self._port_po: OutputPort = OutputPort(1)
        """The carry propagation output port."""

    @property
    def ntargets(self) -> int:
        """The number of the target slice ALUs."""
        return self._ntargets

    @property
    def port_ci(self) -> InputPort:
        """The carry input port.

        The width is 1 bit.

        """
        return self._port_ci

    @property
    def ports_gi(self) -> tuple[InputPort, ...]:
        """The carry generation input ports.

        The number of the ports is ``ntargets``.
        Each width is 1 bit.

        """
        return self._ports_gi

    @property
    def ports_pi(self) -> tuple[InputPort, ...]:
        """The carry propagation input ports.

        The number of the ports is ``ntargets``.
        Each width is 1 bit.

        """
        return self._ports_pi

    @property
    def ports_co(self) -> tuple[OutputPort, ...]:
        """The carry output ports.

        The number of the ports is ``ntargets - 1``.
        Each width is 1 bit.

        """
        return self._ports_co

    @property
    def port_go(self) -> OutputPort:
        """The carry generation output port.

        The width is 1 bit.

        """
        return self._port_go

    @property
    def port_po(self) -> OutputPort:
        """The carry propagation output port.

        The width is 1 bit.

        """
        return self._port_po

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in [self._port_ci, *self._ports_gi, *self._ports_pi]:
            p.reset()
        for q in [*self._ports_co, self._port_go, self._port_po]:
            q.reset()

    @staticmethod
    def _f_and(x: int | None, y: int | None) -> int | None:
        return (x & y) if isinstance(x, int) and isinstance(y, int) else None

    @staticmethod
    def _f_or(x: int | None, y: int | None) -> int | None:
        return (x | y) if isinstance(x, int) and isinstance(y, int) else None

    @staticmethod
    def _f_xor(x: int | None, y: int | None) -> int | None:
        return (x ^ y) if isinstance(x, int) and isinstance(y, int) else None

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_ci, *self._ports_gi, *self._ports_pi]
        if self._update_time_and_check_inputs(time, ports_i):
            n: int = self._ntargets
            ci: int | None = int.from_bytes(self._port_ci.signal.word) if isinstance(self._port_ci.signal.word, bytes) else None
            pi: list[int | None] = [
                (int.from_bytes(p.signal.word) if isinstance(p.signal.word, bytes) else None)
                for p in self._ports_pi
            ]
            gi: list[int | None] = [
                (int.from_bytes(p.signal.word) if isinstance(p.signal.word, bytes) else None)
                for p in self._ports_gi
            ]
            a0: list[int | None] = [reduce(self._f_and, gi[i:n], pi[i]) for i in range(1, n)]
            a1: int | None = reduce(self._f_and, gi, cast(int | None, 1))
            go: int | None = reduce(self._f_or, a0, a1)
            po: int | None = reduce(self._f_or, pi, cast(int | None, 0))
            self._port_go.post(Signal(go.to_bytes(1) if go is not None else Unknown, self._time))
            self._port_po.post(Signal(po.to_bytes(1) if po is not None else Unknown, self._time))
            for k, q in enumerate(self._ports_co):
                b0: list[int | None] = [reduce(self._f_and, gi[i:k + 1], pi[i]) for i in range(k + 1)]
                b1: int | None = reduce(self._f_and, gi[:k + 1], self._f_xor(ci, 1))
                co: int | None = self._f_xor(reduce(self._f_or, b0, b1), 1)
                q.post(Signal(co.to_bytes(1) if co is not None else Unknown, self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
