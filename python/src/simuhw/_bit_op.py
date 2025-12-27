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

from abc import ABCMeta
from collections.abc import Iterable
import math

from ._base import InputPort
from ._gate import UnaryGate


def _reverse_bits(width: int, bits: int) -> int:
    r: int = 0
    for _ in range(width):
        r = (r << 1) | (bits & 1)
        bits >>= 1
    return r


class BitOperator(UnaryGate, metaclass=ABCMeta):
    """The super class for all bit operators."""

    def __init__(self, width: int) -> None:
        """Creates a bit operator.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)


class PopulationCounter(BitOperator):
    """A bit population counter."""

    def __init__(self, width: int) -> None:
        """Creates a bit population counter.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            if self._ports_i[0].data[0] is None:
                self._port_o.post((None, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].data[0])
                self._port_o.post((v.bit_count().to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class LeadingZeroCounter(BitOperator):
    """A leading bit-0 counter."""

    def __init__(self, width: int) -> None:
        """Creates a leading bit-0 counter.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            if self._ports_i[0].data[0] is None:
                self._port_o.post((None, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].data[0])
                self._port_o.post(((self._width - v.bit_length()).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class TrailingZeroCounter(BitOperator):
    """A trailing bit-0 counter."""

    def __init__(self, width: int) -> None:
        """Creates a trailing bit-0 counter.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            if self._ports_i[0].data[0] is None:
                self._port_o.post((None, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].data[0])
                self._port_o.post((((v & -v).bit_length() - 1 if v > 0 else self._width).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class BitReverser(BitOperator):
    """A bit reverser."""

    def __init__(self, width: int) -> None:
        """Creates a bit reverser.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            if self._ports_i[0].data[0] is None:
                self._port_o.post((None, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].data[0])
                self._port_o.post((_reverse_bits(self._width, v).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class SIMD_BitOperator(UnaryGate, metaclass=ABCMeta):
    """The super class for all SIMD bit operators."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD bit operator.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width)
        self._dsize: tuple[int, ...] = tuple(dsize) if isinstance(dsize, Iterable) else (dsize,)
        """The selectable data word widths in bits."""
        if len(self._dsize) == 0 or any((w <= 0 or width % w != 0 for w in self._dsize)):
            raise ValueError('inconsistent data word widths')
        self._port_s: InputPort = InputPort(math.ceil(math.log2(len(self._dsize))))
        """The input port to select the data word width."""

    @property
    def dsize(self) -> tuple[int, ...]:
        """The selectable data word widths in bits."""
        return self._dsize

    @property
    def port_s(self) -> InputPort:
        """The input port to select the data word width."""
        return self._port_s

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_s.reset()


class SIMD_PopulationCounter(SIMD_BitOperator):
    """A SIMD bit population counter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD bit population counter.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if (
                self._ports_i[0].data[0] is None or self._port_s.data[0] is None or
                int.from_bytes(self._port_s.data[0]) >= len(self._dsize)
            ):
                self._port_o.post((None, self._time))
            else:
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].data[0])
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= u.bit_count() << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_LeadingZeroCounter(SIMD_BitOperator):
    """A SIMD leading bit-0 counter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD leading bit-0 counter.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if (
                self._ports_i[0].data[0] is None or self._port_s.data[0] is None or
                int.from_bytes(self._port_s.data[0]) >= len(self._dsize)
            ):
                self._port_o.post((None, self._time))
            else:
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].data[0])
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= (w - u.bit_length()) << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_TrailingZeroCounter(SIMD_BitOperator):
    """A SIMD trailing bit-0 counter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD trailing bit-0 counter.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if (
                self._ports_i[0].data[0] is None or self._port_s.data[0] is None or
                int.from_bytes(self._port_s.data[0]) >= len(self._dsize)
            ):
                self._port_o.post((None, self._time))
            else:
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].data[0])
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= ((u & -u).bit_length() - 1 if u > 0 else w) << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_BitReverser(SIMD_BitOperator):
    """A SIMD bit reverser."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD bit reverser.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if (
                self._ports_i[0].data[0] is None or self._port_s.data[0] is None or
                int.from_bytes(self._port_s.data[0]) >= len(self._dsize)
            ):
                self._port_o.post((None, self._time))
            else:
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].data[0])
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= _reverse_bits(w, u) << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
