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

from .._type import Unknown, Signal
from .._base import InputPort
from ._operator import Float, FPUnaryOperator, SIMD_FPUnaryOperator


class FPNegator(FPUnaryOperator):
    """A floating-point negator.

    This device negates the floating-point value.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, dtype: Float) -> None:
        """Creates a floating-point negator.

        Args:
            dtype: The floating-point type.

        """
        super().__init__(dtype)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_ft, self._port_fr, self._port_fe_i]
        if self._update_time_and_check_inputs(time, ports_i):
            self.apply_states()
            if any((not isinstance(p.signal.word, bytes) for p in [*self._ports_i, self._port_ft, self._port_fr])):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                self._port_o.post(Signal(self._dtype.from_bytes(self._ports_i[0].signal.word).neg().to_bytes(), self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_FPNegator(SIMD_FPUnaryOperator):
    """A SIMD floating-point negator.

    This device negates the respective sign of multiple floating-point values simultaneously.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, width: int, dtype: Float | Iterable[Float]) -> None:
        """Creates a SIMD floating-point negator.

        Args:
            width: The total width of words in bits.
            dtype: The selectable floating-point type or types.

        Raises:
            ValueError: If ``width`` is not divisible by any of ``dtype`` sizes.

        """
        super().__init__(width, dtype)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s, self._port_ft, self._port_fr, self._port_fe_i]
        if self._update_time_and_check_inputs(time, ports_i):
            self.apply_states()
            if (
                any((not isinstance(p.signal.word, bytes) for p in [*self._ports_i, self._port_s, self._port_ft, self._port_fr])) or
                int.from_bytes(cast(bytes, self._port_s.signal.word)) >= len(self._dsize)
            ):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                assert isinstance(self._ports_i[0].signal.word, bytes)
                assert isinstance(self._port_s.signal.word, bytes)
                s: int = int.from_bytes(self._port_s.signal.word)
                w: int = self._dtype[s].size()
                m: int = (1 << w) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: bytes = b''
                for i in range(0, self._width, w):
                    u: bytes = ((v >> i) & m).to_bytes(w >> 3)
                    o = self._dtype[s].from_bytes(u).neg().to_bytes() + o
                self._port_o.post(Signal(o, self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
