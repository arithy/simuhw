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

from .. import (
    SIMD_UnaryOperator, SIMD_BinaryOperator,
    Buffer, Inverter, ANDGate, ORGate, XORGate, NANDGate, NORGate, XNORGate,
    LeftShifter, RightShifter, ArithmeticRightShifter, LeftRotator, RightRotator,
    SIMD_LeftShifter, SIMD_RightShifter, SIMD_ArithmeticRightShifter, SIMD_LeftRotator, SIMD_RightRotator,
    PopulationCounter, LeadingZeroCounter, TrailingZeroCounter, BitReverser,
    SIMD_PopulationCounter, SIMD_LeadingZeroCounter, SIMD_TrailingZeroCounter, SIMD_BitReverser,
    Negator, SIMD_Negator,
    FullAdder, SIMD_Adder,
    FullSubtractor, SIMD_Subtractor,
    Multiplier, SignedMultiplier, SIMD_Multiplier, SIMD_SignedMultiplier,
    Divider, SignedDivider, SIMD_Divider, SIMD_SignedDivider,
    Remainder, SignedRemainder, SIMD_Remainder, SIMD_SignedRemainder,
    Comparator, SignedComparator, SIMD_Comparator, SIMD_SignedComparator,
    IntegerConverter, SignedIntegerConverter, SIMD_IntegerConverter, SIMD_SignedIntegerConverter
)
from .._operator import Operator, SIMD_Operator
from ._generic import GenericArithmeticLogicUnit
from .. import fp
from ..fp import riscv


def _create_operators(
    dsize: Iterable[int], *,
    use_int: bool, use_fp: bool, use_fp_riscv: bool
) -> list[Operator]:
    o: list[Operator] = []
    if use_int:
        o += [
            *(
                d(w)
                for d in [
                    Buffer, Inverter, ANDGate, ORGate, XORGate, NANDGate, NORGate, XNORGate,
                    LeftShifter, RightShifter, ArithmeticRightShifter, LeftRotator, RightRotator,
                    PopulationCounter, LeadingZeroCounter, TrailingZeroCounter, BitReverser,
                    Negator, FullAdder, FullSubtractor, Multiplier, SignedMultiplier,
                    Divider, SignedDivider, Remainder, SignedRemainder,
                    Comparator, SignedComparator
                ]
                for w in dsize
            ),
            *(
                d(wi, wo)
                for d in [
                    IntegerConverter, SignedIntegerConverter
                ]
                for wi in dsize
                for wo in dsize
                if wi != wo
            )
        ]
    if use_fp:
        fp.raise_exception_if_not_available()
        o += [
            *(
                d(fp.dsize_to_dtype(w))
                for d in cast(list[type[fp.FPUnaryOperator | fp.FPBinaryOperator | fp.FPTernaryOperator]], [
                    fp.FPNegator, fp.FPAdder, fp.FPSubtractor,
                    fp.FPMultiplier, fp.FPMultiplyAdder,
                    fp.FPDivider, fp.FPRemainder, fp.FPSquareRoot,
                    fp.FPComparator, fp.FPClassifier, fp.FPToIntegerRounder
                ])
                for w in dsize
                if w in [16, 32, 64, 128]
            ),
            *(
                d(wi, fp.dsize_to_dtype(wo))
                for d in [
                    fp.FPFromIntegerConverter, fp.FPFromSignedIntegerConverter
                ]
                for wi in dsize
                for wo in dsize
                if wo in [16, 32, 64, 128]
            ),
            *(
                d(fp.dsize_to_dtype(wi), wo)
                for d in [
                    fp.FPToIntegerConverter, fp.FPToSignedIntegerConverter
                ]
                for wi in dsize
                for wo in dsize
                if wi in [16, 32, 64, 128]
                if wo <= fp.FPToIntegerConverter.max_width()
            ),
            *(
                d(fp.dsize_to_dtype(wi), fp.dsize_to_dtype(wo))
                for d in [
                    fp.FPConverter
                ]
                for wi in dsize
                for wo in dsize
                if wi != wo and wi in [16, 32, 64, 128] and wo in [16, 32, 64, 128]
            )
        ]
    if use_fp_riscv:
        fp.raise_exception_if_not_available()
        o += [
            *(
                d(fp.dsize_to_dtype(w))
                for d in [
                    riscv.FRec7, riscv.FRSqrt7
                ]
                for w in dsize
                if w in [16, 32, 64, 128]
            )
        ]
    return o


def _create_simd_operators(
    width: int, dsize: Iterable[int], *,
    use_int: bool, use_fp: bool, use_fp_riscv: bool
) -> list[SIMD_Operator]:
    o: list[SIMD_Operator] = []
    if use_int:
        o += [
            *(
                d(width, dsize)
                for d in cast(list[type[SIMD_UnaryOperator | SIMD_BinaryOperator]], [
                    SIMD_LeftShifter, SIMD_RightShifter, SIMD_ArithmeticRightShifter, SIMD_LeftRotator, SIMD_RightRotator,
                    SIMD_PopulationCounter, SIMD_LeadingZeroCounter, SIMD_TrailingZeroCounter, SIMD_BitReverser,
                    SIMD_Negator, SIMD_Adder, SIMD_Subtractor, SIMD_Multiplier, SIMD_SignedMultiplier,
                    SIMD_Divider, SIMD_SignedDivider, SIMD_Remainder, SIMD_SignedRemainder,
                    SIMD_Comparator, SIMD_SignedComparator
                ])
            ),
            *(
                d(width // max(wi, wo), wi, wo)
                for d in [
                    SIMD_IntegerConverter, SIMD_SignedIntegerConverter
                ]
                for wi in dsize
                for wo in dsize
                if wi != wo
            )
        ]
    if use_fp:
        fp.raise_exception_if_not_available()
        o += [
            *(
                d(width, [fp.dsize_to_dtype(w) for w in dsize if w in [16, 32, 64, 128]])
                for d in cast(list[type[fp.SIMD_FPUnaryOperator | fp.SIMD_FPBinaryOperator]], [
                    fp.SIMD_FPNegator, fp.SIMD_FPAdder, fp.SIMD_FPSubtractor,
                    fp.SIMD_FPMultiplier, fp.SIMD_FPMultiplyAdder,
                    fp.SIMD_FPDivider, fp.SIMD_FPRemainder, fp.SIMD_FPSquareRoot,
                    fp.SIMD_FPComparator, fp.SIMD_FPClassifier, fp.SIMD_FPToIntegerRounder
                ])
            ),
            *(
                d(width // max(wi, wo), wi, fp.dsize_to_dtype(wo))
                for d in [
                    fp.SIMD_FPFromIntegerConverter, fp.SIMD_FPFromSignedIntegerConverter
                ]
                for wi in dsize
                for wo in dsize
                if wo in [16, 32, 64, 128]
            ),
            *(
                d(width // max(wi, wo), fp.dsize_to_dtype(wi), wo)
                for d in [
                    fp.SIMD_FPToIntegerConverter, fp.SIMD_FPToSignedIntegerConverter
                ]
                for wi in dsize
                for wo in dsize
                if wi in [16, 32, 64, 128]
                if wo <= fp.FPToIntegerConverter.max_width()
            ),
            *(
                d(width // max(wi, wo), fp.dsize_to_dtype(wi), fp.dsize_to_dtype(wo))
                for d in [
                    fp.SIMD_FPConverter
                ]
                for wi in dsize
                for wo in dsize
                if wi != wo and wi in [16, 32, 64, 128] and wo in [16, 32, 64, 128]
            )
        ]
    if use_fp_riscv:
        fp.raise_exception_if_not_available()
        o += [
            *(
                d(width, fp.dsize_to_dtype(w))
                for d in [
                    riscv.SIMD_FRec7, riscv.SIMD_FRSqrt7
                ]
                for w in dsize
                if w in [16, 32, 64, 128]
            )
        ]
    return o


class FullArithmeticLogicUnit(GenericArithmeticLogicUnit):
    """A full arithmetic logic unit.

    This device integrates all operator devices supported by SimuHW.

    """

    def __init__(
        self, dsize: int | Iterable[int], *,
        use_int: bool = True, use_fp: bool = False, use_fp_riscv: bool = False,
        add_ops: Iterable[Operator] = []
    ) -> None:
        """Creates a full arithmetic logic unit.

        Args:
            dsize: The word width or widths in bits.
            use_int: If it is ``True``, all integer operator devices other than architecture-specific ones are integrated.
                     Every multiple-input bitwise logic gate such as :class:`~simuhw.ANDGate` has two inputs.
                     The :class:`~simuhw.LookupTable` device is not integrated unless specifying it in ``add_ops`` argument.
            use_fp: If it is ``True``, all floating-point operator devices other than architecture-specific ones are integrated.
                    The integration can be done only if an appropriate version of
                    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.
            use_fp_riscv: If it is ``True``, all floating-point operator devices specific to RISC-V are integrated.
                          The integration can be done only if an appropriate version of
                          `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.
            add_ops: The additional operator devices.

        Raises:
            RuntimeError: If no appropriate version of `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

        """
        dsize = [*dsize] if isinstance(dsize, Iterable) else [dsize]
        super().__init__([
            *_create_operators(dsize, use_int=use_int, use_fp=use_fp, use_fp_riscv=use_fp_riscv),
            *add_ops
        ])
        self._dsize: tuple[int, ...] = tuple(dsize)
        """The word widths in bits."""

    @property
    def dsize(self) -> tuple[int, ...]:
        """The word widths in bits."""
        return self._dsize


class SIMD_FullArithmeticLogicUnit(GenericArithmeticLogicUnit):
    """A SIMD full arithmetic logic unit.

    This device integrates all non-SIMD and SIMD operator devices supported by SimuHW.

    """

    def __init__(
        self, width: int, dsize: int | Iterable[int], *,
        with_non_simd: bool = True,
        use_int: bool = True, use_fp: bool = False, use_fp_riscv: bool = False,
        add_ops: Iterable[Operator] = []
    ) -> None:
        """Creates a SIMD full arithmetic logic unit.

        Args:
            width: The total width of words in bits.
            dsize: The selectable word width or widths in bits.
            with_non_simd: If it is ``True``, non-SIMD operator devices are also integrated.
            use_int: If it is ``True``, all integer operator devices other than architecture-specific ones are integrated.
                     Every multiple-input bitwise logic gate such as :class:`~simuhw.ANDGate` has two inputs.
                     The :class:`~simuhw.LookupTable` device is not integrated unless specifying it in ``add_ops`` argument.
            use_fp: If it is ``True``, all floating-point operator devices other than architecture-specific ones are integrated.
                    The integration can be done only if an appropriate version of
                    `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.
            use_fp_riscv: If it is ``True``, all floating-point operator devices specific to RISC-V are integrated.
                          The integration can be done only if an appropriate version of
                          `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.
            add_ops: The additional operator devices.

        Raises:
            ValueError: If ``width`` is not divisible by any of ``dsize``.
            RuntimeError: If no appropriate version of `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.

        """
        dsize = [*dsize] if isinstance(dsize, Iterable) else [dsize]
        super().__init__([
            *(_create_operators(dsize, use_int=use_int, use_fp=use_fp, use_fp_riscv=use_fp_riscv) if with_non_simd else []),
            *_create_simd_operators(width, dsize, use_int=use_int, use_fp=use_fp, use_fp_riscv=use_fp_riscv),
            *add_ops
        ])
        self._width: int = width
        """The total width of words in bits."""
        self._dsize: tuple[int, ...] = tuple(dsize)
        """The word widths in bits."""

    @property
    def width(self) -> int:
        """The total width of words in bits."""
        return self._width

    @property
    def dsize(self) -> tuple[int, ...]:
        """The word widths in bits."""
        return self._dsize
