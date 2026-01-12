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
from ._base import InputPort, to_signed_int
from ._operator import BinaryOperator, SIMD_BinaryOperator


class Shifter(BinaryOperator, metaclass=ABCMeta):
    """The super class for all barrel shifters."""

    def __init__(self, width: int) -> None:
        """Creates a barrel shifter.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)


class LeftShifter(Shifter):
    """A left barrel shifter."""

    def __init__(self, width: int) -> None:
        """Creates a left barrel shifter.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = v << s if s < self._width else 0
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class RightShifter(Shifter):
    """A right barrel shifter."""

    def __init__(self, width: int) -> None:
        """Creates a right barrel shifter.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = v >> s if s < self._width else 0
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class ArithmeticRightShifter(Shifter):
    """An arithmetic right barrel shifter."""

    def __init__(self, width: int) -> None:
        """Creates an arithmetic right barrel shifter.

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
                v: int = to_signed_int(self._width, int.from_bytes(self._ports_i[0].signal.word))
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = v >> s if s < self._width else 0 if v >= 0 else -1
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class LeftRotator(Shifter):
    """A left barrel rotator."""

    def __init__(self, width: int) -> None:
        """Creates a left barrel rotator.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word) % self._width if self._width > 0 else 0
                o: int = v << s
                self._port_o.post(Signal(((o | (o >> self._width)) & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class RightRotator(Shifter):
    """A right barrel rotator."""

    def __init__(self, width: int) -> None:
        """Creates a right barrel rotator.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word) % self._width if self._width > 0 else 0
                o: int = ((v << self._width) | v) >> s
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_Shifter(SIMD_BinaryOperator, metaclass=ABCMeta):
    """The super class for all SIMD barrel shifters."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD barrel shifter.

        Args:
            width: The total width of words in bits.
            dsize: The selectable word width or widths in bits.

        Raises:
            ValueError: If ``width`` is not divisible by any of ``dsize``.

        """
        super().__init__(width, dsize)


class SIMD_LeftShifter(SIMD_Shifter):
    """A SIMD left barrel shifter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD left barrel shifter.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    r: int = (s >> i) & m
                    o |= (((v >> i) << r if r < w else 0) & m) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_RightShifter(SIMD_Shifter):
    """A SIMD right barrel shifter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD right barrel shifter.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    r: int = (s >> i) & m
                    o |= (((v >> i) & m) >> r if r < w else 0) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_ArithmeticRightShifter(SIMD_Shifter):
    """A SIMD arithmetic right barrel shifter."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD arithmetic right barrel shifter.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = to_signed_int(w, (v >> i) & m)
                    r: int = (s >> i) & m
                    o |= ((u >> r if r < w else 0 if u >= 0 else -1) & m) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_LeftRotator(SIMD_Shifter):
    """A SIMD left barrel rotator."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD left barrel rotator.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    r: int = (s >> i) & m
                    o |= (((((u << w) | u) << (r % w if w > 0 else 0)) >> w) & m) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_RightRotator(SIMD_Shifter):
    """A SIMD right barrel rotator."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD right barrel rotator.

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
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                s: int = int.from_bytes(self._ports_i[1].signal.word)
                o: int = 0
                for i in range(0, self._width, w):
                    u: int = (v >> i) & m
                    r: int = (s >> i) & m
                    o |= ((((u << w) | u) >> (r % w if w > 0 else 0)) & m) << i
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
