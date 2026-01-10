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

from ._word import Unknown
from ._base import InputPort, OutputPort
from ._operator import BinaryOperator, SIMD_BinaryOperator


class Subtractor(BinaryOperator):
    """A subtractor.

    This device calculates a subtraction of two binary integers.
    It has no borrow input and no borrow output.

    """

    def __init__(self, width: int) -> None:
        """Creates a subtractor.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.data[0], bytes) for p in ports_i)):
                self._port_o.post((Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].data[0], bytes)
                assert isinstance(self._ports_i[1].data[0], bytes)
                o: int = int.from_bytes(self._ports_i[0].data[0]) - int.from_bytes(self._ports_i[1].data[0])
                self._port_o.post(((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class HalfSubtractor(Subtractor):
    """A half subtractor.

    This device calculates a subtraction of two binary integers.
    It has borrow output, but has no borrow input.

    """

    def __init__(self, width: int) -> None:
        """Creates a half subtractor.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)
        self._port_co: OutputPort = OutputPort(1)
        """The borrow output port."""

    @property
    def port_co(self) -> OutputPort:
        """The borrow output port."""
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
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.data[0], bytes) for p in ports_i)):
                self._port_o.post((Unknown, self._time))
                self._port_co.post((Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].data[0], bytes)
                assert isinstance(self._ports_i[1].data[0], bytes)
                o: int = int.from_bytes(self._ports_i[0].data[0]) - int.from_bytes(self._ports_i[1].data[0])
                self._port_o.post(((o & self._mask).to_bytes(self._nbytes), self._time))
                self._port_co.post((((o >> self._width) & 1).to_bytes(1), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class FullSubtractor(HalfSubtractor):
    """A full subtractor.

    This device calculates a subtraction of two binary integers.
    It has borrow input and borrow output.

    """

    def __init__(self, width: int) -> None:
        """Creates a full subtractor.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)
        self._port_ci: InputPort = InputPort(1)
        """The borrow input port."""

    @property
    def port_ci(self) -> InputPort:
        """The borrow input port."""
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
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_ci]
        if self._update_time_and_check_inputs(time, ports_i):
            if any((not isinstance(p.data[0], bytes) for p in ports_i)):
                self._port_o.post((Unknown, self._time))
                self._port_co.post((Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].data[0], bytes)
                assert isinstance(self._ports_i[1].data[0], bytes)
                assert isinstance(self._port_ci.data[0], bytes)
                o: int = (
                    int.from_bytes(self._ports_i[0].data[0]) -
                    int.from_bytes(self._ports_i[1].data[0]) -
                    int.from_bytes(self._port_ci.data[0])
                )
                self._port_o.post(((o & self._mask).to_bytes(self._nbytes), self._time))
                self._port_co.post((((o >> self._width) & 1).to_bytes(1), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_Subtractor(SIMD_BinaryOperator):
    """A SIMD subtractor.

    This device calculates respective subtractions of multiple pairs of binary integers simultaneously.

    """

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD subtractor.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If ``width`` is not divisible by any of ``dsize``.

        """
        super().__init__(width, dsize)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if (
                any((not isinstance(p.data[0], bytes) for p in ports_i)) or
                int.from_bytes(cast(bytes, self._port_s.data[0])) >= len(self._dsize)
            ):
                self._port_o.post((Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].data[0], bytes)
                assert isinstance(self._ports_i[1].data[0], bytes)
                assert isinstance(self._port_s.data[0], bytes)
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v0: int = int.from_bytes(self._ports_i[0].data[0])
                v1: int = int.from_bytes(self._ports_i[1].data[0])
                o: int = 0
                for i in range(0, self._width, w):
                    o |= (((v0 >> i) - (v1 >> i)) & m) << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
