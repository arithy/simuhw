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
from collections.abc import Iterable

from ._type import Unknown, Signal
from ._base import InputPort, OutputPort
from ._operator import BinaryOperator, SIMD_BinaryOperator


class Adder(BinaryOperator):
    """An adder.

    This device calculates an addition of two binary integers.
    It has no carry input and no carry output.

    """

    def __init__(self, width: int) -> None:
        """Creates an adder.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.signal.word, bytes) for p in ports_i)):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                assert isinstance(self._ports_i[1].signal.word, bytes)
                o: int = int.from_bytes(self._ports_i[0].signal.word) + int.from_bytes(self._ports_i[1].signal.word)
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class HalfAdder(Adder):
    """A half adder.

    This device calculates an addition of two binary integers.
    It has carry output, but has no carry input.

    """

    def __init__(self, width: int) -> None:
        """Creates a half adder.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)
        self._port_co: OutputPort = OutputPort(1)
        """The carry output port."""

    @property
    def port_co(self) -> OutputPort:
        """The carry output port.

        The width is 1 bit.

        """
        return self._port_co

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_co.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.signal.word, bytes) for p in ports_i)):
                self._port_o.post(Signal(Unknown, self._time))
                self._port_co.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                assert isinstance(self._ports_i[1].signal.word, bytes)
                o: int = int.from_bytes(self._ports_i[0].signal.word) + int.from_bytes(self._ports_i[1].signal.word)
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
                self._port_co.post(Signal(((o >> self._width) & 1).to_bytes(1), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class FullAdder(HalfAdder):
    """A full adder.

    This device calculates an addition of two binary integers.
    It has carry input and carry output.

    """

    def __init__(self, width: int) -> None:
        """Creates a full adder.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)
        self._port_ci: InputPort = InputPort(1)
        """The carry input port."""

    @property
    def port_ci(self) -> InputPort:
        """The carry input port.

        The width is 1 bit.

        """
        return self._port_ci

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_ci.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_ci]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.signal.word, bytes) for p in ports_i)):
                self._port_o.post(Signal(Unknown, self._time))
                self._port_co.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                assert isinstance(self._ports_i[1].signal.word, bytes)
                assert isinstance(self._port_ci.signal.word, bytes)
                o: int = (
                    int.from_bytes(self._ports_i[0].signal.word) +
                    int.from_bytes(self._ports_i[1].signal.word) +
                    int.from_bytes(self._port_ci.signal.word)
                )
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
                self._port_co.post(Signal(((o >> self._width) & 1).to_bytes(1), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_Adder(SIMD_BinaryOperator):
    """A SIMD adder.

    This device calculates respective additions of multiple pairs of binary integers simultaneously.

    """

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD adder.

        Args:
            width: The total width of words in bits.
            dsize: The selectable word width or widths in bits.

        Raises:
            ValueError: If ``width`` is not divisible by any of ``dsize``.

        """
        super().__init__(width, dsize)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if (
                any((not isinstance(p.signal.word, bytes) for p in ports_i)) or
                int.from_bytes(cast(bytes, self._port_s.signal.word)) >= len(self._dsize)
            ):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                assert isinstance(self._ports_i[1].signal.word, bytes)
                assert isinstance(self._port_s.signal.word, bytes)
                w: int = self._dsize[int.from_bytes(self._port_s.signal.word)]
                m: int = (1 << w) - 1
                v0: int = int.from_bytes(self._ports_i[0].signal.word)
                v1: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    o |= (((v0 >> i) + (v1 >> i)) & m) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
