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
from abc import ABCMeta
from collections.abc import Iterable

from ._type import Unknown, Signal
from ._base import InputPort
from ._operator import UnaryOperator, SIMD_UnaryOperator


def _reverse_bits(width: int, bits: int) -> int:
    r: int = 0
    for _ in range(width):
        r = (r << 1) | (bits & 1)
        bits >>= 1
    return r


class BitOperator(UnaryOperator, metaclass=ABCMeta):
    """The super class for all bit operators."""

    def __init__(self, width: int) -> None:
        """Creates a bit operator.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)


class PopulationCounter(BitOperator):
    """A bit population counter."""

    def __init__(self, width: int) -> None:
        """Creates a bit population counter.

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
        if self._update_time_and_check_inputs(time, self._ports_i):
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                self._port_o.post(Signal(v.bit_count().to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class LeadingZeroCounter(BitOperator):
    """A leading bit-0 counter."""

    def __init__(self, width: int) -> None:
        """Creates a leading bit-0 counter.

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
        if self._update_time_and_check_inputs(time, self._ports_i):
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                self._port_o.post(Signal((self._width - v.bit_length()).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class TrailingZeroCounter(BitOperator):
    """A trailing bit-0 counter."""

    def __init__(self, width: int) -> None:
        """Creates a trailing bit-0 counter.

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
        if self._update_time_and_check_inputs(time, self._ports_i):
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                self._port_o.post(Signal(((v & -v).bit_length() - 1 if v > 0 else self._width).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class BitReverser(BitOperator):
    """A bit reverser."""

    def __init__(self, width: int) -> None:
        """Creates a bit reverser.

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
        if self._update_time_and_check_inputs(time, self._ports_i):
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                self._port_o.post(Signal(_reverse_bits(self._width, v).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_BitOperator(SIMD_UnaryOperator, metaclass=ABCMeta):
    """The super class for all SIMD bit operators."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD bit operator.

        Args:
            width: The total width of words in bits.
            dsize: The selectable word width or widths in bits.

        Raises:
            ValueError: If ``width`` is not divisible by any of ``dsize``.

        """
        super().__init__(width, dsize)


class SIMD_PopulationCounter(SIMD_BitOperator):
    """A SIMD bit population counter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD bit population counter.

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
                assert isinstance(self._port_s.signal.word, bytes)
                w: int = self._dsize[int.from_bytes(self._port_s.signal.word)]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= u.bit_count() << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_LeadingZeroCounter(SIMD_BitOperator):
    """A SIMD leading bit-0 counter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD leading bit-0 counter.

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
                assert isinstance(self._port_s.signal.word, bytes)
                w: int = self._dsize[int.from_bytes(self._port_s.signal.word)]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= (w - u.bit_length()) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_TrailingZeroCounter(SIMD_BitOperator):
    """A SIMD trailing bit-0 counter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD trailing bit-0 counter.

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
                assert isinstance(self._port_s.signal.word, bytes)
                w: int = self._dsize[int.from_bytes(self._port_s.signal.word)]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= ((u & -u).bit_length() - 1 if u > 0 else w) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_BitReverser(SIMD_BitOperator):
    """A SIMD bit reverser."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD bit reverser.

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
                assert isinstance(self._port_s.signal.word, bytes)
                w: int = self._dsize[int.from_bytes(self._port_s.signal.word)]
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    o |= _reverse_bits(w, u) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
