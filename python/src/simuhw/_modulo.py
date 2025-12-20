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

from collections.abc import Iterable
import math

from ._base import InputPort, OutputPort, to_signed_int
from ._gate import BinaryGate


class Modulo(BinaryGate):
    """A modulo calculator.

    This device calculates a modulo of two unsigned binary integers.

    """

    def __init__(self, width: int) -> None:
        """Creates a modulo calculator.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)
        self._port_e: OutputPort = OutputPort(1)
        """The output port to emit overflow exception."""

    @property
    def port_e(self) -> OutputPort:
        """The output port to emit overflow exception."""
        return self._port_e

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_e.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if self._ports_i[0].data[0] is None or self._ports_i[1].data[0] is None:
                self._port_o.post((None, self._time))
                self._port_e.post((None, self._time))
            else:
                v1: int = int.from_bytes(self._ports_i[1].data[0])
                if v1 == 0:
                    self._port_o.post(((0).to_bytes(self._nbytes), self._time))
                    self._port_e.post((b'\x01', self._time))
                else:
                    o: int = int.from_bytes(self._ports_i[0].data[0]) % v1
                    self._port_o.post(((o & self._mask).to_bytes(self._nbytes), self._time))
                    self._port_e.post((b'\x00' if (o >> self._width) == 0 else b'\x01', self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SignedModulo(Modulo):
    """A signed modulo calculator.

    This device calculates a modulo of two signed binary integers.

    """

    def __init__(self, width: int) -> None:
        """Creates a signed modulo calculator.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width)

    def reset(self) -> None:
        """Resets the states."""
        super().reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if self._ports_i[0].data[0] is None or self._ports_i[1].data[0] is None:
                self._port_o.post((None, self._time))
                self._port_e.post((None, self._time))
            else:
                v1: int = to_signed_int(self._width, int.from_bytes(self._ports_i[1].data[0]))
                if v1 == 0:
                    self._port_o.post(((0).to_bytes(self._nbytes), self._time))
                    self._port_e.post((b'\x01', self._time))
                else:
                    v0: int = to_signed_int(self._width, int.from_bytes(self._ports_i[0].data[0]))
                    o: int = (abs(v0) % abs(v1)) * (1 if v0 >= 0 else -1)
                    self._port_o.post(((o & self._mask).to_bytes(self._nbytes), self._time))
                    self._port_e.post((b'\x00' if self._width <= 0 or (o >> (self._width - 1)) == (0 if o >= 0 else -1) else b'\x01', self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMDModulo(BinaryGate):
    """A SIMD modulo calculator.

    This device calculates respective moduli of multiple pairs of unsigned binary integers simultaneously.

    """

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD modulo calculator.

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
        self._port_e: OutputPort = OutputPort(width // min(self._dsize))
        """The output port to emit overflow exception."""
        self._nbytes_e: int = (self._port_e.width + 7) >> 3
        """The number of bytes required to represent the overflow exceptions."""

    @property
    def dsize(self) -> tuple[int, ...]:
        """The selectable data word widths in bits."""
        return self._dsize

    @property
    def port_s(self) -> InputPort:
        """The input port to select the data word width."""
        return self._port_s

    @property
    def port_e(self) -> OutputPort:
        """The output port to emit overflow exception."""
        return self._port_e

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_s.reset()
        self._port_e.reset()

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
                self._ports_i[0].data[0] is None or self._ports_i[1].data[0] is None or
                self._port_s.data[0] is None or int.from_bytes(self._port_s.data[0]) >= len(self._dsize)
            ):
                self._port_o.post((None, self._time))
                self._port_e.post((None, self._time))
            else:
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v0: int = int.from_bytes(self._ports_i[0].data[0])
                v1: int = int.from_bytes(self._ports_i[1].data[0])
                o: int = 0
                e: int = 0
                for i, j in enumerate(range(0, self._width, w)):
                    w0: int = (v0 >> j) & m
                    w1: int = (v1 >> j) & m
                    if w1 == 0:
                        e |= 1 << i
                    else:
                        r: int = w0 % w1
                        o |= (r & m) << j
                        e |= (0 if (r >> w) == 0 else 1) << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
                self._port_e.post((e.to_bytes(self._nbytes_e), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMDSignedModulo(SIMDModulo):
    """A SIMD signed modulo calculator.

    This device calculates respective moduli of multiple pairs of signed binary integers simultaneously.

    """

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD signed modulo calculator.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize)

    def reset(self) -> None:
        """Resets the states."""
        super().reset()

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
                self._ports_i[0].data[0] is None or self._ports_i[1].data[0] is None or
                self._port_s.data[0] is None or int.from_bytes(self._port_s.data[0]) >= len(self._dsize)
            ):
                self._port_o.post((None, self._time))
                self._port_e.post((None, self._time))
            else:
                w: int = self._dsize[int.from_bytes(self._port_s.data[0])]
                m: int = (1 << w) - 1
                v0: int = int.from_bytes(self._ports_i[0].data[0])
                v1: int = int.from_bytes(self._ports_i[1].data[0])
                o: int = 0
                e: int = 0
                for i, j in enumerate(range(0, self._width, w)):
                    w0: int = to_signed_int(w, (v0 >> j) & m)
                    w1: int = to_signed_int(w, (v1 >> j) & m)
                    if w1 == 0:
                        e |= 1 << i
                    else:
                        r: int = (abs(w0) % abs(w1)) * (1 if w0 >= 0 else -1)
                        o |= (r & m) << j
                        e |= (0 if (r >> (w - 1)) == (0 if r >= 0 else -1) else 1) << i
                self._port_o.post((o.to_bytes(self._nbytes), self._time))
                self._port_e.post((e.to_bytes(self._nbytes_e), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
