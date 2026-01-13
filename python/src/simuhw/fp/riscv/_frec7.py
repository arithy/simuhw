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

import softfloatpy as sf

from ..._type import Unknown, Signal
from ..._base import InputPort
from .._operator import Float, FPUnaryOperator, SIMD_FPUnaryOperator

_frec7_table: list[int] = [  # mantissa[MSB-7:MSB] -> mantissa[MSB-7:MSB]
    127, 125, 123, 121, 119, 117, 116, 114, 112, 110, 109, 107, 105, 104, 102, 100,
    99, 97, 96, 94, 93, 91, 90, 88, 87, 85, 84, 83, 81, 80, 79, 77,
    76, 75, 74, 72, 71, 70, 69, 68, 66, 65, 64, 63, 62, 61, 60, 59,
    58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43,
    42, 41, 40, 40, 39, 38, 37, 36, 35, 35, 34, 33, 32, 31, 31, 30,
    29, 28, 28, 27, 26, 25, 25, 24, 23, 23, 22, 21, 21, 20, 19, 19,
    18, 17, 17, 16, 15, 15, 14, 14, 13, 12, 12, 11, 11, 10, 9, 9,
    8, 8, 7, 7, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0
]


def _frec7_core(bin: bytes, nbits_exp: int, nbits_man: int, bias_exp: int) -> bytes:
    assert nbits_exp >= 0
    assert nbits_man >= 7
    b: int = int.from_bytes(bin)
    s: int = b & (1 << (nbits_exp + nbits_man))
    e: int = (b >> nbits_man) & ((1 << nbits_exp) - 1)
    m: int = b & ((1 << nbits_man) - 1)
    if e == 0:
        if m == 0:  # zero
            sf.set_exception_flags(sf.get_exception_flags() | sf.ExceptionFlag.INFINITE)
            return (s | (((1 << nbits_exp) - 1) << nbits_man)).to_bytes(len(bin))  # infinity
        elif (m >> (nbits_man - 2)) == 0:  # subnormal [case 1/3]
            sf.set_exception_flags(sf.get_exception_flags() | sf.ExceptionFlag.INEXACT | sf.ExceptionFlag.OVERFLOW)
            if sf.get_rounding_mode() in [sf.RoundingMode.MAX if s == 0 else sf.RoundingMode.MIN, sf.RoundingMode.NEAR_EVEN, sf.RoundingMode.NEAR_MAX_MAG]:
                return (s | (((1 << nbits_exp) - 1) << nbits_man)).to_bytes(len(bin))  # infinity
            else:
                return (s | (((1 << nbits_exp) - 2) << nbits_man) | ((1 << nbits_man) - 1)).to_bytes(len(bin))  # maximum magnitude finite value
        elif (m >> (nbits_man - 1)) == 0:  # subnormal [case 2/3]
            e = -1
            m = (m << 2) & ((1 << nbits_man) - 1)
        else:  # subnormal [case 3/3]
            m = (m << 1) & ((1 << nbits_man) - 1)
    elif e == (1 << nbits_exp) - 1:
        if m == 0:  # infinity
            return s.to_bytes(len(bin))  # zero
        else:  # NaN
            if (m >> (nbits_man - 1)) == 0:  # signaling NaN
                sf.set_exception_flags(sf.get_exception_flags() | sf.ExceptionFlag.INVALID)
            return (((1 << (nbits_exp + 1)) - 1) << (nbits_man - 1)).to_bytes(len(bin))  # canonical NaN
    else:  # normal
        pass
    assert (m >> nbits_man) == 0
    e = (bias_exp * 2 - 1) - e
    m = _frec7_table[m >> (nbits_man - 7)] << (nbits_man - 7)
    assert e >= -1 and e <= bias_exp * 2
    assert (m >> nbits_man) == 0
    if e <= 0:  # subnormal
        m = (m | (1 << nbits_man)) >> (1 - e)
        e = 0
    return (s | (e << nbits_man) | m).to_bytes(len(bin))


def frec7(x: sf.Float16 | sf.Float32 | sf.Float64 | sf.Float128) -> sf.Float16 | sf.Float32 | sf.Float64 | sf.Float128:
    if isinstance(x, sf.Float16):
        return sf.Float16.from_bytes(_frec7_core(x.to_bytes(), 5, 10, 15))
    elif isinstance(x, sf.Float32):
        return sf.Float32.from_bytes(_frec7_core(x.to_bytes(), 8, 23, 127))
    elif isinstance(x, sf.Float64):
        return sf.Float64.from_bytes(_frec7_core(x.to_bytes(), 11, 52, 1023))
    elif isinstance(x, sf.Float128):
        return sf.Float128.from_bytes(_frec7_core(x.to_bytes(), 15, 112, 16383))
    else:
        raise ValueError(f'Invalid argument type: {type(x)}')


class FRec7(FPUnaryOperator):
    """A device to estimate a floating-point reciprocal to 7 bits.

    This device is intended to be used for emulation of the RISC-V instruction ``vfrec7``.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, dtype: Float) -> None:
        """Creates a device to estimate a floating-point reciprocal.

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
                self._port_o.post(Signal(frec7(self._dtype.from_bytes(self._ports_i[0].signal.word)).to_bytes(), self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class SIMD_FRec7(SIMD_FPUnaryOperator):
    """A SIMD device to estimate floating-point reciprocals to 7 bits simultaneously.

    This device is intended to be used for emulation of the RISC-V instruction ``vfrec7``.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, width: int, dtype: Float | Iterable[Float]) -> None:
        """Creates a SIMD device to estimate floating-point reciprocals.

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
                    o = frec7(self._dtype[s].from_bytes(u)).to_bytes() + o
                self._port_o.post(Signal(o, self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
