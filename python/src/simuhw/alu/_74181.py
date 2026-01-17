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

from .._type import Unknown, Signal
from .._base import InputPort, OutputPort
from .._operator import BinaryOperator


class ArithmeticLogicUnit74181(BinaryOperator):
    """An arithmetic logic unit 74181 with arbitrary bits.

    This device behaves like the logic IC 74181 with no timing delay and with arbitrary bits.

    **Truth Tables:**

    .. code-block:: text

        [Active-Low Data]  a: first operand, b: second operand, f: result
        +-----------------------+--------------+-----------------------------------------------------+
        |       Selection       |     m = H    |                      m = L                          |
        +-----+-----+-----+-----+--------------+------------------------+----------------------------+
        | s3  | s2  | s1  | s0  |    ci = X    |         ci = L         |           ci = H           |
        +-----+-----+-----+-----+--------------+------------------------+----------------------------+
        |  L  |  L  |  L  |  L  | f =    ~a    | f =  a - 1             | f =  a                     |
        |  L  |  L  |  L  |  H  | f = ~(a & b) | f = (a & b) - 1        | f =  a & b                 |
        |  L  |  L  |  H  |  L  | f =  ~a | b  | f = (a & ~b) - 1       | f =  a & ~b                |
        |  L  |  L  |  H  |  H  | f =     1    | f = -1                 | f =  0                     |
        |  L  |  H  |  L  |  L  | f = ~(a | b) | f =  a + (a | ~b)      | f =  a + (a | ~b) + 1      |
        |  L  |  H  |  L  |  H  | f =    ~b    | f = (a & b) + (a | ~b) | f = (a & b) + (a | ~b) + 1 |
        |  L  |  H  |  H  |  L  | f = ~(a ^ b) | f =  a - b - 1         | f =  a - b                 |
        |  L  |  H  |  H  |  H  | f =   a | ~b | f =  a | ~b            | f = (a | ~b) + 1           |
        |  H  |  L  |  L  |  L  | f =  ~a & b  | f =  a + (a | b)       | f =  a + (a | b) + 1       |
        |  H  |  L  |  L  |  H  | f =   a ^ b  | f =  a + b             | f =  a + b + 1             |
        |  H  |  L  |  H  |  L  | f =     b    | f = (a & ~b) + (a | b) | f = (a & ~b) + (a | b) + 1 |
        |  H  |  L  |  H  |  H  | f =   a | b  | f =  a | b             | f = (a | b) + 1            |
        |  H  |  H  |  L  |  L  | f =     0    | f =  a + a             | f =  a + a + 1             |
        |  H  |  H  |  L  |  H  | f =   a & ~b | f = (a & b) + a        | f = (a & b) + a + 1        |
        |  H  |  H  |  H  |  L  | f =   a & b  | f = (a & ~b) + a       | f = (a & ~b) + a + 1       |
        |  H  |  H  |  H  |  H  | f =     a    | f =  a                 | f =  a + 1                 |
        +-----+-----+-----+-----+--------------+------------------------+----------------------------+

        [Active-High Data]  a: first operand, b: second operand, f: result
        +-----------------------+--------------+-----------------------------------------------------+
        |       Selection       |     m = H    |                      m = L                          |
        +-----+-----+-----+-----+--------------+------------------------+----------------------------+
        | s3  | s2  | s1  | s0  |    ci = X    |         ci = H         |           ci = L           |
        +-----+-----+-----+-----+--------------+------------------------+----------------------------+
        |  L  |  L  |  L  |  L  | f =    ~a    | f =  a                 | f =  a + 1                 |
        |  L  |  L  |  L  |  H  | f = ~(a | b) | f =  a | b             | f = (a | b) + 1            |
        |  L  |  L  |  H  |  L  | f =  ~a & b  | f =  a | ~b            | f = (a | ~b) + 1           |
        |  L  |  L  |  H  |  H  | f =     0    | f = -1                 | f =  0                     |
        |  L  |  H  |  L  |  L  | f = ~(a & b) | f =  a + (a & ~b)      | f =  a + (a & ~b) + 1      |
        |  L  |  H  |  L  |  H  | f =    ~b    | f = (a | b) + (a & ~b) | f = (a | b) + (a & ~b) + 1 |
        |  L  |  H  |  H  |  L  | f =   a ^ b  | f =  a - b - 1         | f =  a - b                 |
        |  L  |  H  |  H  |  H  | f =   a & ~b | f = (a & ~b) - 1       | f =  a & ~b                |
        |  H  |  L  |  L  |  L  | f =  ~a | b  | f =  a + (a & b)       | f =  a + (a & b) + 1       |
        |  H  |  L  |  L  |  H  | f = ~(a ^ b) | f =  a + b             | f =  a + b + 1             |
        |  H  |  L  |  H  |  L  | f =     b    | f = (a | ~b) + (a & b) | f = (a | ~b) + (a & b) + 1 |
        |  H  |  L  |  H  |  H  | f =   a & b  | f = (a & b) - 1        | f =  a & b                 |
        |  H  |  H  |  L  |  L  | f =     1    | f =  a + a             | f =  a + a + 1             |
        |  H  |  H  |  L  |  H  | f =   a | ~b | f = (a | b) + a        | f = (a | b) + a + 1        |
        |  H  |  H  |  H  |  L  | f =   a | b  | f = (a | ~b) + a       | f = (a | ~b) + a + 1       |
        |  H  |  H  |  H  |  H  | f =     a    | f =  a - 1             | f =  a                     |
        +-----+-----+-----+-----+--------------+------------------------+----------------------------+

    """

    def __init__(self, width: int) -> None:
        """Creates an arithmetic logic unit 74181 with arbitrary bits.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)
        self._port_s: InputPort = InputPort(4)
        """The selection port."""
        self._port_m: InputPort = InputPort(1)
        """The mode control port."""
        self._port_ci: InputPort = InputPort(1)
        """The carry input port."""
        self._port_co: OutputPort = OutputPort(1)
        """The carry output port."""
        self._port_po: OutputPort = OutputPort(1)
        """The carry propagation output port."""
        self._port_go: OutputPort = OutputPort(1)
        """The carry generation output port."""
        self._port_cmp: OutputPort = OutputPort(1)
        """The comparator port."""

    @property
    def port_s(self) -> InputPort:
        """The selection port.

        The width is 4 bits.

        """
        return self._port_s

    @property
    def port_m(self) -> InputPort:
        """The mode control port.

        The width is 1 bit.

        """
        return self._port_m

    @property
    def port_ci(self) -> InputPort:
        """The carry input port.

        The width is 1 bit.

        """
        return self._port_ci

    @property
    def port_co(self) -> OutputPort:
        """The carry output port.

        The width is 1 bit.

        """
        return self._port_co

    @property
    def port_po(self) -> OutputPort:
        """The carry propagation output port.

        The width is 1 bit.

        """
        return self._port_po

    @property
    def port_go(self) -> OutputPort:
        """The carry generation output port.

        The width is 1 bit.

        """
        return self._port_go

    @property
    def port_cmp(self) -> OutputPort:
        """The comparator port.

        The width is 1 bit.

        """
        return self._port_cmp

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in [*self._ports_i, self._port_s, self._port_m, self._port_ci]:
            p.reset()
        for q in [self._port_o, self._port_co, self._port_po, self._port_go, self._port_cmp]:
            q.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s, self._port_m, self._port_ci]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.signal.word, bytes) for p in ports_i)):
                for q in [self._port_o, self._port_co, self._port_po, self._port_go, self._port_cmp]:
                    q.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                assert isinstance(self._ports_i[1].signal.word, bytes)
                assert isinstance(self._port_s.signal.word, bytes)
                assert isinstance(self._port_m.signal.word, bytes)
                assert isinstance(self._port_ci.signal.word, bytes)
                w: int = self._width
                k: int = self._mask
                a: int = int.from_bytes(self._ports_i[0].signal.word)
                b: int = int.from_bytes(self._ports_i[1].signal.word)
                s: int = int.from_bytes(self._port_s.signal.word)
                m: int = k * int.from_bytes(self._port_m.signal.word)
                c: int = k * int.from_bytes(self._port_ci.signal.word)
                s0: int = k * (s & 1)
                s1: int = k * ((s >> 1) & 1)
                s2: int = k * ((s >> 2) & 1)
                s3: int = k * (s >> 3)
                a00: int = s0 & b
                a01: int = s1 & (b ^ k)
                a02: int = s2 & (b ^ k) & a
                a03: int = s3 & b & a
                o00: int = (a00 | a01 | a) ^ k
                o01: int = (a02 | a03) ^ k
                x00: int = o00 ^ o01
                a10: list[int] = [reduce(lambda x, y: x & y, ((o01 << i) for i in range(1, j)), (m ^ k) & (o00 << j)) for j in range(1, w)]
                a11: int = reduce(lambda x, y: x & y, ((((o01 ^ k) << i) ^ k) for i in range(1, w)), (m ^ k) & c)
                o10: int = reduce(lambda x, y: x | y, a10, a11) ^ k
                o: int = x00 ^ o10
                a12: int = reduce(lambda x, y: x & y, ((o01 >> i) for i in range(w)), 1)
                a13: int = a12 & (c & 1)
                a14: int = reduce(lambda x, y: x & y, ((((k << w) | o01) >> i) for i in range(1, w)), o00)
                o11: int = reduce(lambda x, y: x | y, ((a14 >> i) for i in range(w)), 0) & 1
                po: int = a12 ^ 1
                go: int = o11 ^ 1
                co: int = a13 | o11
                cmp: int = reduce(lambda x, y: x & y, ((o >> i) for i in range(w)), 1)
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
                self._port_co.post(Signal(co.to_bytes(1), self._time))
                self._port_po.post(Signal(po.to_bytes(1), self._time))
                self._port_go.post(Signal(go.to_bytes(1), self._time))
                self._port_cmp.post(Signal(cmp.to_bytes(1), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
