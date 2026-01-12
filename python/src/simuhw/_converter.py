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

from ._type import Unknown, Signal
from ._base import InputPort, to_signed_int
from ._operator import UnaryOperator, SIMD_UnaryOperator


class IntegerConverter(UnaryOperator):
    """An integer converter.

    This device converts the unsigned binary integer to that with different bit size.

    """

    def __init__(self, width_i: int, width_o: int) -> None:
        """Creates an integer converter.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.

        """
        super().__init__(width_i, width_o)

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
                o: int = int.from_bytes(self._ports_i[0].signal.word)
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SignedIntegerConverter(IntegerConverter):
    """A signed integer converter.

    This device converts the signed binary integer to that with different bit size.

    """

    def __init__(self, width_i: int, width_o: int) -> None:
        """Creates a signed integer converter.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.

        """
        super().__init__(width_i, width_o)

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
                o: int = to_signed_int(self._width_i, int.from_bytes(self._ports_i[0].signal.word))
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_IntegerConverter(SIMD_UnaryOperator):
    """A SIMD integer converter.

    This device converts the respective unsigned binary integers to those with different bit size simultaneously.

    """

    def __init__(self, multi: int, dsize_i: int, dsize_o: int) -> None:
        """Creates a SIMD integer converter.

        Args:
            multi: The number of SIMD elements.
            dsize_i: The input word width in bits.
            dsize_o: The output word width in bits.

        """
        super().__init__(dsize_i * multi, dsize_i, dsize_o * multi)

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
                m: int = (1 << min(self._dsize_i[0], self._dsize_o[0])) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i, j in zip(
                    range(0, self._width_i, self._dsize_i[0]),
                    range(0, self._width_o, self._dsize_o[0])
                ):
                    o |= ((v >> i) & m) << j
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_SignedIntegerConverter(SIMD_IntegerConverter):
    """A SIMD signed integer converter.

    This device converts the respective signed binary integers to those with different bit size simultaneously.

    """

    def __init__(self, multi: int, dsize_i: int, dsize_o: int) -> None:
        """Creates a SIMD signed integer converter.

        Args:
            multi: The number of SIMD elements.
            dsize_i: The input word width in bits.
            dsize_o: The output word width in bits.

        """
        super().__init__(multi, dsize_i, dsize_o)

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
                m: int = (1 << self._dsize_i[0]) - 1
                n: int = (1 << self._dsize_o[0]) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i, j in zip(
                    range(0, self._width_i, self._dsize_i[0]),
                    range(0, self._width_o, self._dsize_o[0])
                ):
                    o |= (to_signed_int(self._dsize_i[0], (v >> i) & m) & n) << j
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)
