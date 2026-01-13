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

import softfloatpy as sf

from .._type import Unknown, Signal
from .._base import InputPort, to_signed_int
from .._operator import UnaryOperator, SIMD_UnaryOperator
from ._operator import Float, Float16, Float32, Float64, Float128, FPState


class FPToIntegerConverter(UnaryOperator, FPState):
    """A floating-point to integer converter.

    This device converts the floating-point to an unsigned integer.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    _max_width: int = 64
    """The maximum supported integer width in bits."""

    @classmethod
    def max_width(cls) -> int:
        """The maximum supported integer width in bits.

        Currently, it is 64.

        """
        return cls._max_width

    def __init__(self, dtype_i: Float, width_o: int) -> None:
        """Creates a floating-point to integer converter.

        Args:
            dtype_i: The input floating-point type.
            width_o: The output word width in bits.
                     Must be less than or equal to the value of :func:`FPToIntegerConverter.max_width()`.

        Raises:
            ValueError: If ``width_o`` is greater than the value of :func:`FPToIntegerConverter.max_width()`.

        """
        if width_o > FPToIntegerConverter.max_width():
            raise ValueError(f'output word width greater than {FPToIntegerConverter.max_width()}')
        super().__init__(dtype_i.size(), width_o)
        FPState.__init__(self)
        self._dtype_i: Float = dtype_i
        """The input floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                o: int = self._dtype_i.from_bytes(self._ports_i[0].signal.word).to_ui64().to_int()
                e: int = sf.get_exception_flags()
                if (
                    (e & (sf.ExceptionFlag.OVERFLOW | sf.ExceptionFlag.INFINITE | sf.ExceptionFlag.INVALID)) == 0 and
                    o >= (1 << self._width_o)
                ):
                    sf.set_exception_flags(e | sf.ExceptionFlag.INVALID)
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class FPFromIntegerConverter(UnaryOperator, FPState):
    """A integer to floating-point converter.

    This device converts the unsigned integer to a floating-point.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, width_i: int, dtype_o: Float) -> None:
        """Creates a integer to floating-point converter.

        Args:
            width_i: The input word width in bits.
            dtype_o: The output floating-point type.

        """
        super().__init__(width_i, dtype_o.size())
        FPState.__init__(self)
        self._dtype_o: Float = dtype_o
        """The output floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                self._port_o.post(Signal(
                    self._dtype_o.from_ui64(sf.UInt64.from_int(int.from_bytes(self._ports_i[0].signal.word))).to_bytes(),
                    self._time
                ))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class FPToSignedIntegerConverter(FPToIntegerConverter):
    """A floating-point to signed-integer converter.

    This device converts the floating-point to a signed integer.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, dtype_i: Float, width_o: int) -> None:
        """Creates a floating-point to signed-integer converter.

        Args:
            dtype_i: The input floating-point type.
            width_o: The output word width in bits.
                     Must be less than or equal to the value of :func:`FPToIntegerConverter.max_width()`.

        Raises:
            ValueError: If ``width_o`` is greater than the value of :func:`FPToIntegerConverter.max_width()`.

        """
        super().__init__(dtype_i, width_o)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                o: int = self._dtype_i.from_bytes(self._ports_i[0].signal.word).to_i64().to_int()
                e: int = sf.get_exception_flags()
                l: int = (1 << self._width_o) >> 1
                if (
                    (e & (sf.ExceptionFlag.OVERFLOW | sf.ExceptionFlag.INFINITE | sf.ExceptionFlag.INVALID)) == 0 and
                    (o >= l or o < -l)
                ):
                    sf.set_exception_flags(e | sf.ExceptionFlag.INVALID)
                self._port_o.post(Signal((o & self._mask).to_bytes(self._nbytes), self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class FPFromSignedIntegerConverter(FPFromIntegerConverter):
    """A signed-integer to floating-point converter.

    This device converts the signed integer to a floating-point.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, width_i: int, dtype_o: Float) -> None:
        """Creates a signed-integer to floating-point converter.

        Args:
            width_i: The input word width in bits.
            dtype_o: The output floating-point type.

        """
        super().__init__(width_i, dtype_o)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                self._port_o.post(Signal(
                    self._dtype_o.from_i64(sf.Int64.from_int(
                        to_signed_int(self._width_i, int.from_bytes(self._ports_i[0].signal.word))
                    )).to_bytes(),
                    self._time
                ))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class FPConverter(UnaryOperator, FPState):
    """A floating-point converter.

    This device converts the floating-point to that of another type.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, dtype_i: Float, dtype_o: Float) -> None:
        """Creates a floating-point converter.

        Args:
            dtype_i: The input floating-point type.
            dtype_o: The output floating-point type.

        """
        super().__init__(dtype_i.size(), dtype_o.size())
        FPState.__init__(self)
        self._dtype_i: Float = dtype_i
        """The input floating-point type."""
        self._dtype_o: Float = dtype_o
        """The output floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                assert self._dtype_i in [Float16, Float32, Float64, Float128]
                self._port_o.post(Signal(
                    (
                        self._dtype_o.from_f16 if self._dtype_i == Float16 else
                        self._dtype_o.from_f32 if self._dtype_i == Float32 else
                        self._dtype_o.from_f64 if self._dtype_i == Float64 else
                        self._dtype_o.from_f128
                    )(self._dtype_i.from_bytes(self._ports_i[0].signal.word)).to_bytes(),  # type: ignore[arg-type]
                    self._time
                ))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_FPToIntegerConverter(SIMD_UnaryOperator, FPState):
    """A SIMD floating-point to integer converter.

    This device converts the respective floating-points to unsigned integers simultaneously.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, multi: int, dtype_i: Float, dsize_o: int) -> None:
        """Creates a SIMD floating-point to integer converter.

        Args:
            multi: The number of SIMD elements.
            dtype_i: The input floating-point type.
            dsize_o: The output word width in bits.
                     Must be less than or equal to the value of :func:`FPToIntegerConverter.max_width()`.

        Raises:
            ValueError: If ``width_o`` is greater than the value of :func:`FPToIntegerConverter.max_width()`.

        """
        if dsize_o > FPToIntegerConverter.max_width():
            raise ValueError(f'output word width greater than {FPToIntegerConverter.max_width()}')
        super().__init__(dtype_i.size() * multi, dtype_i.size(), dsize_o * multi)
        FPState.__init__(self)
        self._dtype_i: Float = dtype_i
        """The input floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                s: int = self._dsize_i[0]
                t: int = self._dsize_o[0]
                m: int = (1 << s) - 1
                n: int = (1 << t) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i, j in zip(
                    range(0, self._width_i, s),
                    range(0, self._width_o, t)
                ):
                    e: int = sf.get_exception_flags()
                    u: int = self._dtype_i.from_bytes(((v >> i) & m).to_bytes(s >> 3)).to_ui64().to_int()
                    if (
                        (e & (sf.ExceptionFlag.OVERFLOW | sf.ExceptionFlag.INFINITE | sf.ExceptionFlag.INVALID)) == 0 and
                        u >= (1 << t)
                    ):
                        sf.set_exception_flags(e | sf.ExceptionFlag.INVALID)
                    o |= (u & n) << j
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_FPFromIntegerConverter(SIMD_UnaryOperator, FPState):
    """A SIMD integer to floating-point converter.

    This device converts the respective unsigned integers to floating-points simultaneously.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, multi: int, dsize_i: int, dtype_o: Float) -> None:
        """Creates a SIMD integer to floating-point converter.

        Args:
            multi: The number of SIMD elements.
            dsize_i: The input word width in bits.
            dtype_o: The output floating-point type.

        """
        super().__init__(dsize_i * multi, dsize_i, dtype_o.size() * multi)
        FPState.__init__(self)
        self._dtype_o: Float = dtype_o
        """The output floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                s: int = self._dsize_i[0]
                m: int = (1 << s) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: bytes = b''
                for i in range(0, self._width_i, s):
                    o = self._dtype_o.from_ui64(sf.UInt64.from_int((v >> i) & m)).to_bytes() + o
                self._port_o.post(Signal(o, self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_FPToSignedIntegerConverter(SIMD_FPToIntegerConverter):
    """A SIMD floating-point to signed-integer converter.

    This device converts the respective floating-points to signed integers simultaneously.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, multi: int, dtype_i: Float, dsize_o: int) -> None:
        """Creates a SIMD floating-point to signed-integer converter.

        Args:
            multi: The number of SIMD elements.
            dtype_i: The input floating-point type.
            dsize_o: The output word width in bits.
                     Must be less than or equal to the value of :func:`FPToIntegerConverter.max_width()`.

        Raises:
            ValueError: If ``width_o`` is greater than the value of :func:`FPToIntegerConverter.max_width()`.

        """
        super().__init__(multi, dtype_i, dsize_o)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                s: int = self._dsize_i[0]
                t: int = self._dsize_o[0]
                m: int = (1 << s) - 1
                n: int = (1 << t) - 1
                l: int = (1 << t) >> 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: int = 0
                for i, j in zip(
                    range(0, self._width_i, s),
                    range(0, self._width_o, t)
                ):
                    e: int = sf.get_exception_flags()
                    u: int = self._dtype_i.from_bytes(((v >> i) & m).to_bytes(s >> 3)).to_i64().to_int()
                    if (
                        (e & (sf.ExceptionFlag.OVERFLOW | sf.ExceptionFlag.INFINITE | sf.ExceptionFlag.INVALID)) == 0 and
                        (u >= l or u < -l)
                    ):
                        sf.set_exception_flags(e | sf.ExceptionFlag.INVALID)
                    o |= (u & n) << j
                self._port_o.post(Signal(o.to_bytes(self._nbytes), self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_FPFromSignedIntegerConverter(SIMD_FPFromIntegerConverter):
    """A SIMD signed-integer to floating-point converter.

    This device converts the respective signed integers to floating-points simultaneously.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, multi: int, dsize_i: int, dtype_o: Float) -> None:
        """Creates a SIMD signed-integer to floating-point converter.

        Args:
            multi: The number of SIMD elements.
            dsize_i: The input word width in bits.
            dtype_o: The output floating-point type.

        """
        super().__init__(multi, dsize_i, dtype_o)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                s: int = self._dsize_i[0]
                m: int = (1 << s) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: bytes = b''
                for i in range(0, self._width_i, s):
                    o = self._dtype_o.from_i64(sf.Int64.from_int(
                        to_signed_int(s, (v >> i) & m)
                    )).to_bytes() + o
                self._port_o.post(Signal(o, self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class SIMD_FPConverter(SIMD_UnaryOperator, FPState):
    """A SIMD floating-point converter.

    This device converts the respective floating-points to those of another type simultaneously.

    Available only if an appropriate version of
    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

    """

    def __init__(self, multi: int, dtype_i: Float, dtype_o: Float) -> None:
        """Creates a SIMD floating-point converter.

        Args:
            multi: The number of SIMD elements.
            dtype_i: The input floating-point type.
            dtype_o: The output floating-point type.

        """
        super().__init__(dtype_i.size() * multi, dtype_i.size(), dtype_o.size() * multi)
        FPState.__init__(self)
        self._dtype_i: Float = dtype_i
        """The input floating-point type."""
        self._dtype_o: Float = dtype_o
        """The output floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self.apply_states()
            if not isinstance(self._ports_i[0].signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                assert self._dtype_i in [Float16, Float32, Float64, Float128]
                s: int = self._dsize_i[0]
                m: int = (1 << s) - 1
                v: int = int.from_bytes(self._ports_i[0].signal.word)
                o: bytes = b''
                for i in range(0, self._width_i, s):
                    o = (
                        self._dtype_o.from_f16 if self._dtype_i == Float16 else
                        self._dtype_o.from_f32 if self._dtype_i == Float32 else
                        self._dtype_o.from_f64 if self._dtype_i == Float64 else
                        self._dtype_o.from_f128
                    )(self._dtype_i.from_bytes(((v >> i) & m).to_bytes(self._dtype_i.size() >> 3))).to_bytes() + o  # type: ignore[arg-type]
                self._port_o.post(Signal(o, self._time))
            self.restore_states(self._time, not isinstance(self._port_o.signal.word, bytes))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)
