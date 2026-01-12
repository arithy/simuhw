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

from abc import ABCMeta
from collections.abc import Iterable

import softfloatpy as sf

from .._type import Unknown, Signal
from .._base import InputPort, OutputPort
from .._operator import (
    UnaryOperator, BinaryOperator, TernaryOperator,
    SIMD_UnaryOperator, SIMD_BinaryOperator, SIMD_TernaryOperator
)


class Float16(sf.Float16, metaclass=ABCMeta):
    """An IEEE 754 binary16 floating point data type."""
    pass


class Float32(sf.Float32, metaclass=ABCMeta):
    """An IEEE 754 binary32 floating point data type."""
    pass


class Float64(sf.Float64, metaclass=ABCMeta):
    """An IEEE 754 binary64 floating point data type."""
    pass


class Float128(sf.Float128, metaclass=ABCMeta):
    """An IEEE 754 binary128 floating point data type."""
    pass


Float = type[Float16 | Float32 | Float64 | Float128]


def dsize_to_dtype(dsize: int) -> Float:
    """Returns a floating-point type that has the specified data size.

    Args:
        dsize: The data size in bits.

    Returns:
        A floating-point type that has the specified data size.

    Raises:
        ValueError: If no floating-point type that has the specified data size.

    """
    if dsize == 16:
        return Float16
    if dsize == 32:
        return Float32
    if dsize == 64:
        return Float64
    if dsize == 128:
        return Float128
    raise ValueError(f'No floating-point type with {dsize} bits')


class FPState(metaclass=ABCMeta):
    """A class that manipulates the floating-point states."""

    width_ft: int = 1
    """The bit width of the input port to set tininess detection mode."""
    width_fr: int = 3
    """The bit width of the input port to set rounding mode."""
    width_fe: int = 5
    """The bit width of the input and output ports to set and get floating-point exception flags."""

    def __init__(self) -> None:
        """Creates a class that manipulates the floating-point states."""
        self._tininess_mode: sf.TininessMode | None = None
        """The saved tininess detection mode."""
        self._rounding_mode: sf.RoundingMode | None = None
        """The saved rounding mode."""
        self._exception_flags: int | None = None
        """The saved floating-point exception flags."""
        self._port_ft: InputPort = InputPort(self.width_ft)
        """The input port to set the tininess detection mode."""
        self._port_fr: InputPort = InputPort(self.width_fr)
        """The input port to set the rounding mode."""
        self._port_fe_i: InputPort = InputPort(self.width_fe)
        """The input port to set the floating-point exception flags."""
        self._port_fe_o: OutputPort = OutputPort(self.width_fe)
        """The output port to get the floating-point exception flags."""

    @property
    def port_ft(self) -> InputPort:
        """The input port to set the tininess detection mode."""
        return self._port_ft

    @property
    def port_fr(self) -> InputPort:
        """The input port to set the rounding mode."""
        return self._port_fr

    @property
    def port_fe_i(self) -> InputPort:
        """The input port to set the floating-point exception flags."""
        return self._port_fe_i

    @property
    def port_fe_o(self) -> OutputPort:
        """The output port to get the floating-point exception flags."""
        return self._port_fe_o

    def reset(self) -> None:
        """Resets the states."""
        self._tininess_mode = None
        self._rounding_mode = None
        self._exception_flags = None
        self._port_ft.reset()
        self._port_fr.reset()
        self._port_fe_i.reset()
        self._port_fe_o.reset()

    def apply_states(self) -> None:
        """Applies the floating-point states from the input ports after saving the current ones."""
        self._tininess_mode = sf.get_tininess_mode()
        self._rounding_mode = sf.get_rounding_mode()
        self._exception_flags = sf.get_exception_flags()
        if isinstance(self._port_ft.signal.word, bytes) and int.from_bytes(self._port_ft.signal.word) in [m.value for m in sf.TininessMode]:
            sf.set_tininess_mode(sf.TininessMode(int.from_bytes(self._port_ft.signal.word)))
        if isinstance(self._port_fr.signal.word, bytes) and int.from_bytes(self._port_fr.signal.word) in [m.value for m in sf.RoundingMode]:
            sf.set_rounding_mode(sf.RoundingMode(int.from_bytes(self._port_fr.signal.word)))
        if isinstance(self._port_fe_i.signal.word, bytes):
            sf.set_exception_flags(int.from_bytes(self._port_fe_i.signal.word))

    def restore_states(self, time: float, not_bytes: bool) -> None:
        """Restores the floating-point states after posting the current ones to the output port.

        Args:
            time: The current device time in seconds.
            not_bytes: ``True`` if the type of the output word is not ``bytes``.

        """
        if not_bytes or any((
            not isinstance(d, bytes) for d in [self._port_ft.signal.word, self._port_fr.signal.word, self._port_fe_i.signal.word]
        )):
            self._port_fe_o.post(Signal(Unknown, time))
        else:
            self._port_fe_o.post(Signal(sf.get_exception_flags().to_bytes(1), time))
        if self._tininess_mode is not None:
            sf.set_tininess_mode(self._tininess_mode)
        if self._rounding_mode is not None:
            sf.set_rounding_mode(self._rounding_mode)
        if self._exception_flags is not None:
            sf.set_exception_flags(self._exception_flags)


class FPUnaryOperator(UnaryOperator, FPState, metaclass=ABCMeta):
    """The super class for all floating-point unary operators."""

    def __init__(self, dtype: Float) -> None:
        """Creates a floating-point unary operators.

        Args:
            dtype: The floating-point type.

        """
        super().__init__(dtype.size())
        FPState.__init__(self)
        self._dtype: Float = dtype
        """The floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)


class FPBinaryOperator(BinaryOperator, FPState, metaclass=ABCMeta):
    """The super class for all floating-point binary operators."""

    def __init__(self, dtype: Float) -> None:
        """Creates a floating-point binary operators.

        Args:
            dtype: The floating-point type.

        """
        super().__init__(dtype.size())
        FPState.__init__(self)
        self._dtype: Float = dtype
        """The floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)


class FPTernaryOperator(TernaryOperator, FPState, metaclass=ABCMeta):
    """The super class for all floating-point ternary operators."""

    def __init__(self, dtype: Float) -> None:
        """Creates a floating-point ternary operators.

        Args:
            dtype: The floating-point type.

        """
        super().__init__(dtype.size())
        FPState.__init__(self)
        self._dtype: Float = dtype
        """The floating-point type."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)


class SIMD_FPUnaryOperator(SIMD_UnaryOperator, FPState, metaclass=ABCMeta):
    """The super class for all SIMD floating-point unary operators."""

    def __init__(self, width: int, dtype: Float | Iterable[Float]) -> None:
        """Creates a SIMD floating-point unary operators.

        Args:
            width: The total width of words in bits.
            dtype: The selectable floating-point type or types.

        """
        super().__init__(width, tuple(t.size() for t in dtype) if isinstance(dtype, Iterable) else (dtype.size(),))
        FPState.__init__(self)
        self._dtype: tuple[Float, ...] = tuple(dtype) if isinstance(dtype, Iterable) else (dtype,)
        """The selectable floating-point types."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)


class SIMD_FPBinaryOperator(SIMD_BinaryOperator, FPState, metaclass=ABCMeta):
    """The super class for all SIMD floating-point binary operators."""

    def __init__(self, width: int, dtype: Float | Iterable[Float]) -> None:
        """Creates a SIMD floating-point binary operators.

        Args:
            width: The total width of words in bits.
            dtype: The selectable floating-point type or types.

        """
        super().__init__(width, tuple(t.size() for t in dtype) if isinstance(dtype, Iterable) else (dtype.size(),))
        FPState.__init__(self)
        self._dtype: tuple[Float, ...] = tuple(dtype) if isinstance(dtype, Iterable) else (dtype,)
        """The selectable floating-point types."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)


class SIMD_FPTernaryOperator(SIMD_TernaryOperator, FPState, metaclass=ABCMeta):
    """The super class for all SIMD floating-point ternary operators."""

    def __init__(self, width: int, dtype: Float | Iterable[Float]) -> None:
        """Creates a SIMD floating-point ternary operators.

        Args:
            width: The total width of words in bits.
            dtype: The selectable floating-point type or types.

        """
        super().__init__(width, tuple(t.size() for t in dtype) if isinstance(dtype, Iterable) else (dtype.size(),))
        FPState.__init__(self)
        self._dtype: tuple[Float, ...] = tuple(dtype) if isinstance(dtype, Iterable) else (dtype,)
        """The selectable floating-point types."""

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        FPState.reset(self)
