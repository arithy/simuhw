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
import math

from ._base import InputPort, OutputPort, Device


class Operator(Device, metaclass=ABCMeta):
    """The super class for all operators."""

    def __init__(self, width_i: int, width_o: int, *, ninputs: int) -> None:
        """Creates an operator.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.
            ninputs: The number of the operand input ports.

        """
        super().__init__()
        self._width_i: int = width_i
        """The input word width in bits."""
        self._width_o: int = width_o
        """The output word width in bits."""
        self._width: int = width_i if width_i == width_o else 0
        """The word width in bits if the input and output word widths are the same, 0 otherwise."""
        self._nbytes: int = (width_o + 7) >> 3
        """The number of bytes required to represent the output."""
        self._mask: int = (1 << width_o) - 1
        """The bit mask for the output."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width_i) for _ in range(ninputs))
        """The operand input ports."""
        self._port_o: OutputPort = OutputPort(width_o)
        """The result output port."""

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._width_i} bits -> {self._width_o} bits)'

    @property
    def width_i(self) -> int:
        """The input word width in bits."""
        return self._width_i

    @property
    def width_o(self) -> int:
        """The output word width in bits."""
        return self._width_o

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The operand input ports."""
        return self._ports_i

    @property
    def port_o(self) -> OutputPort:
        """The result output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in self._ports_i:
            p.reset()
        self._port_o.reset()


class UnaryOperator(Operator, metaclass=ABCMeta):
    """The super class for all unary operators."""

    def __init__(self, width_i: int, width_o: int = -1) -> None:
        """Creates a unary operators.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.
                     If a negative value is specified, ``width_i`` is used instead.

        """
        super().__init__(width_i, width_o if width_o >= 0 else width_i, ninputs=1)

    @property
    def port_i(self) -> InputPort:
        """The operand input port."""
        return self._ports_i[0]


class BinaryOperator(Operator, metaclass=ABCMeta):
    """The super class for all binary operators."""

    def __init__(self, width_i: int, width_o: int = -1) -> None:
        """Creates a binary operators.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.
                     If a negative value is specified, ``width_i`` is used instead.

        """
        super().__init__(width_i, width_o if width_o >= 0 else width_i, ninputs=2)

    @property
    def port_i0(self) -> InputPort:
        """The operand input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The operand input port 1."""
        return self._ports_i[1]


class TernaryOperator(Operator, metaclass=ABCMeta):
    """The super class for all binary operators."""

    def __init__(self, width_i: int, width_o: int = -1) -> None:
        """Creates a binary operators.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.
                     If a negative value is specified, ``width_i`` is used instead.

        """
        super().__init__(width_i, width_o if width_o >= 0 else width_i, ninputs=3)

    @property
    def port_i0(self) -> InputPort:
        """The operand input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The operand input port 1."""
        return self._ports_i[1]

    @property
    def port_i2(self) -> InputPort:
        """The operand input port 2."""
        return self._ports_i[2]


class SIMD_Operator(Operator, metaclass=ABCMeta):
    """The super class for all SIMD operators."""

    def __init__(self, width_i: int, dsize_i: int | Iterable[int], width_o: int, *, ninputs: int) -> None:
        """Creates a SIMD operator.

        Args:
            width_i: The total width of input words in bits.
            dsize_i: The selectable input word width or widths in bits.
            width_o: The total width of output words in bits.
            ninputs: The number of the operand input ports.

        Raises:
            ValueError: If ``width_i`` is not divisible by any of ``dsize_i``, or if ``width_o`` is inconsistent with them.

        """
        super().__init__(width_i, width_o, ninputs=ninputs)
        self._dsize_i: tuple[int, ...] = tuple(dsize_i) if isinstance(dsize_i, Iterable) else (dsize_i,)
        """The selectable input word widths in bits."""
        if len(self._dsize_i) == 0 or any((w <= 0 or width_i % w != 0 for w in self._dsize_i)):
            raise ValueError('inconsistent input word widths')
        self._multi: tuple[int, ...] = tuple(width_i // w for w in self._dsize_i)
        """The selectable operation multiplicities."""
        if any((width_o % m != 0 for m in self._multi)):
            raise ValueError('inconsistent input word widths')
        self._dsize_o: tuple[int, ...] = tuple(width_o // m for m in self._multi)
        """The selectable output word widths in bits."""
        self._dsize: tuple[int, ...] = self._dsize_i if width_i == width_o else ()
        """The selectable word widths in bits if the input and output word widths are the same, empty otherwise."""
        self._port_s: InputPort = InputPort(math.ceil(math.log2(len(self._dsize_i))))
        """The input port to select the input word width."""

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._width_i} bits: {[*self._dsize_i]} -> {self._width_o} bits: {[*self._dsize_o]})'

    @property
    def multi(self) -> tuple[int, ...]:
        """The selectable operation multiplicities."""
        return self._multi

    @property
    def dsize_i(self) -> tuple[int, ...]:
        """The selectable input word widths in bits."""
        return self._dsize_i

    @property
    def dsize_o(self) -> tuple[int, ...]:
        """The selectable output word widths in bits."""
        return self._dsize_o

    @property
    def port_s(self) -> InputPort:
        """The input port to select the input word width."""
        return self._port_s

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_s.reset()


class SIMD_UnaryOperator(SIMD_Operator, metaclass=ABCMeta):
    """The super class for all SIMD unary operators."""

    def __init__(self, width_i: int, dsize_i: int | Iterable[int], width_o: int = -1) -> None:
        """Creates a SIMD unary operator.

        Args:
            width_i: The total width of input words in bits.
            dsize_i: The selectable input word width or widths in bits.
            width_o: The total width of output words in bits.
                     If a negative value is specified, ``width_i`` is used instead.

        Raises:
            ValueError: If ``width_i`` is not divisible by any of ``dsize_i``, or if ``width_o`` is inconsistent with them.

        """
        super().__init__(width_i, dsize_i, width_o if width_o >= 0 else width_i, ninputs=1)

    @property
    def port_i(self) -> InputPort:
        """The operand input port."""
        return self._ports_i[0]


class SIMD_BinaryOperator(SIMD_Operator, metaclass=ABCMeta):
    """The super class for all SIMD binary operators."""

    def __init__(self, width_i: int, dsize_i: int | Iterable[int], width_o: int = -1) -> None:
        """Creates a SIMD binary operator.

        Args:
            width_i: The total width of input words in bits.
            dsize_i: The selectable input word width or widths in bits.
            width_o: The total width of output words in bits.
                     If a negative value is specified, ``width_i`` is used instead.

        Raises:
            ValueError: If ``width_i`` is not divisible by any of ``dsize_i``, or if ``width_o`` is inconsistent with them.

        """
        super().__init__(width_i, dsize_i, width_o if width_o >= 0 else width_i, ninputs=2)

    @property
    def port_i0(self) -> InputPort:
        """The operand input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The operand input port 1."""
        return self._ports_i[1]


class SIMD_TernaryOperator(SIMD_Operator, metaclass=ABCMeta):
    """The super class for all SIMD ternary operators."""

    def __init__(self, width_i: int, dsize_i: int | Iterable[int], width_o: int = -1) -> None:
        """Creates a SIMD ternary operator.

        Args:
            width_i: The total width of input words in bits.
            dsize_i: The selectable input word width or widths in bits.
            width_o: The total width of output words in bits.
                     If a negative value is specified, ``width_i`` is used instead.

        Raises:
            ValueError: If ``width_i`` is not divisible by any of ``dsize_i``, or if ``width_o`` is inconsistent with them.

        """
        super().__init__(width_i, dsize_i, width_o if width_o >= 0 else width_i, ninputs=3)

    @property
    def port_i0(self) -> InputPort:
        """The operand input port 0."""
        return self._ports_i[0]

    @property
    def port_i1(self) -> InputPort:
        """The operand input port 1."""
        return self._ports_i[1]

    @property
    def port_i2(self) -> InputPort:
        """The operand input port 2."""
        return self._ports_i[2]
