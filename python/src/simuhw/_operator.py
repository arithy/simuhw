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

from ._base import InputPort, OutputPort, Device


class Operator(Device, metaclass=ABCMeta):
    """The super class for all operators."""

    def __init__(self, width: int, *, ninputs: int) -> None:
        """Creates an operator.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._nbytes: int = (width + 7) >> 3
        """The number of bytes required to represent the output."""
        self._mask: int = (1 << width) - 1
        """The mask."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width) for _ in range(ninputs))
        """The input ports."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports."""
        return self._ports_i

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in self._ports_i:
            p.reset()
        self._port_o.reset()


class UnaryOperator(Operator, metaclass=ABCMeta):
    """The super class for all unary operators."""

    def __init__(self, width: int) -> None:
        """Creates a unary operators.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width, ninputs=1)

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._ports_i[0]


class BinaryOperator(Operator, metaclass=ABCMeta):
    """The super class for all binary operators."""

    def __init__(self, width: int) -> None:
        """Creates a binary operators.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width, ninputs=2)

    @property
    def port_i0(self) -> InputPort:
        """The input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The input port 1."""
        return self._ports_i[1]


class TernaryOperator(Operator, metaclass=ABCMeta):
    """The super class for all binary operators."""

    def __init__(self, width: int) -> None:
        """Creates a binary operators.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width, ninputs=3)

    @property
    def port_i0(self) -> InputPort:
        """The input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The input port 1."""
        return self._ports_i[1]

    @property
    def port_i2(self) -> InputPort:
        """The input port 2."""
        return self._ports_i[2]


class SIMD_Operator(Operator, metaclass=ABCMeta):
    """The super class for all SIMD operators."""

    def __init__(self, width: int, dsize: int | Iterable[int], *, ninputs: int) -> None:
        """Creates a SIMD operator.

        Args:
            width: The data word width in bits.
            dsize: The selectable data word width or widths in bits.
            ninputs: The number of the input ports.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, ninputs=ninputs)
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


class SIMD_UnaryOperator(SIMD_Operator, metaclass=ABCMeta):
    """The super class for all SIMD unary operators."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD unary operator.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize, ninputs=1)

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._ports_i[0]


class SIMD_BinaryOperator(SIMD_Operator, metaclass=ABCMeta):
    """The super class for all SIMD binary operators."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD binary operator.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize, ninputs=2)

    @property
    def port_i0(self) -> InputPort:
        """The input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The input port 1."""
        return self._ports_i[1]


class SIMD_TernaryOperator(SIMD_Operator, metaclass=ABCMeta):
    """The super class for all SIMD ternary operators."""

    def __init__(self, width: int, dsize: int | Iterable[int]) -> None:
        """Creates a SIMD ternary operator.

        Args:
            width: The total width of data words in bits.
            dsize: The selectable data word width or widths in bits.

        Raises:
            ValueError: If `width` is not divisible by any of `dsize`.

        """
        super().__init__(width, dsize, ninputs=3)

    @property
    def port_i0(self) -> InputPort:
        """The input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The input port 1."""
        return self._ports_i[1]

    @property
    def port_i2(self) -> InputPort:
        """The input port 2."""
        return self._ports_i[2]
