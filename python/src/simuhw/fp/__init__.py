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

import sys
import importlib.metadata
from packaging.version import Version

__all__ = [
    'is_available',
    'get_required_softfloatpy_least_version',
    'raise_exception_if_not_available'
]

_softfloatpy_least: Version = Version('1.2.3')

_softfloatpy: Version | None = None
_available: bool = False
_error_str: str | None = None

try:
    _softfloatpy = Version(importlib.metadata.version('softfloatpy'))
    if _softfloatpy < _softfloatpy_least:
        raise RuntimeError(
            f'Improper \'softfloatpy\' version: {_softfloatpy} < {_softfloatpy_least}'
        )

    _available = True

    __all__ += [
        'TininessMode', 'RoundingMode', 'ExceptionFlag',
        'Float', 'Float16', 'Float32', 'Float64', 'Float128', 'dsize_to_dtype',
        'FPState', 'FPUnaryOperator', 'FPBinaryOperator', 'FPTernaryOperator',
        'SIMD_FPUnaryOperator', 'SIMD_FPBinaryOperator', 'SIMD_FPTernaryOperator',
        'FPNegator', 'SIMD_FPNegator',
        'FPAdder', 'SIMD_FPAdder',
        'FPSubtractor', 'SIMD_FPSubtractor',
        'FPMultiplier', 'SIMD_FPMultiplier',
        'FPMultiplyAdder', 'SIMD_FPMultiplyAdder',
        'FPDivider', 'SIMD_FPDivider',
        'FPRemainder', 'SIMD_FPRemainder',
        'FPSquareRoot', 'SIMD_FPSquareRoot',
        'FPComparator', 'SIMD_FPComparator',
        'FPClassifier', 'SIMD_FPClassifier',
        'FPToIntegerRounder', 'SIMD_FPToIntegerRounder',
        'FPToIntegerConverter', 'SIMD_FPToIntegerConverter',
        'FPFromIntegerConverter', 'SIMD_FPFromIntegerConverter',
        'FPToSignedIntegerConverter', 'SIMD_FPToSignedIntegerConverter',
        'FPFromSignedIntegerConverter', 'SIMD_FPFromSignedIntegerConverter',
        'FPConverter', 'SIMD_FPConverter'
    ]

    from softfloatpy import TininessMode, RoundingMode, ExceptionFlag
    from ._operator import (
        Float, Float16, Float32, Float64, Float128, dsize_to_dtype,
        FPState, FPUnaryOperator, FPBinaryOperator, FPTernaryOperator,
        SIMD_FPUnaryOperator, SIMD_FPBinaryOperator, SIMD_FPTernaryOperator
    )
    from ._negator import FPNegator, SIMD_FPNegator
    from ._adder import FPAdder, SIMD_FPAdder
    from ._subtractor import FPSubtractor, SIMD_FPSubtractor
    from ._multiplier import FPMultiplier, SIMD_FPMultiplier
    from ._multiply_adder import FPMultiplyAdder, SIMD_FPMultiplyAdder
    from ._divider import FPDivider, SIMD_FPDivider
    from ._remainder import FPRemainder, SIMD_FPRemainder
    from ._square_root import FPSquareRoot, SIMD_FPSquareRoot
    from ._comparator import FPComparator, SIMD_FPComparator
    from ._classifier import FPClassifier, SIMD_FPClassifier
    from ._rounder import FPToIntegerRounder, SIMD_FPToIntegerRounder
    from ._converter import (
        FPToIntegerConverter, SIMD_FPToIntegerConverter,
        FPFromIntegerConverter, SIMD_FPFromIntegerConverter,
        FPToSignedIntegerConverter, SIMD_FPToSignedIntegerConverter,
        FPFromSignedIntegerConverter, SIMD_FPFromSignedIntegerConverter,
        FPConverter, SIMD_FPConverter
    )

except importlib.metadata.PackageNotFoundError:
    _error_str = 'No \'softfloatpy\' module'
except RuntimeError as e:
    _error_str = f'{e}'

if _error_str is not None:
    print(f'{__name__} [WARNING] Not available ({_error_str})', file=sys.stderr)


def is_available() -> bool:
    """Checks whether ``simuhw.fp`` submodule is available or not.

    Returns:
        ``True`` if ``simuhw.fp`` submodule is available.

    Note:
        ``simuhw.fp`` submodule is available only when an appropriate version of
        `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.
        The least version can be retrieved using :func:`get_required_softfloatpy_least_version()`

    """
    return _available


def get_required_softfloatpy_least_version() -> str:
    """Retrieves the least version of `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module
    required for ``simuhw.fp`` submodule.

    Returns:
        The least version of `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module
        required for ``simuhw.fp`` submodule.

    """
    return str(_softfloatpy_least)


def raise_exception_if_not_available() -> None:
    """Raises an exception if ``simuhw.fp`` submodule is not available.

    Raises:
        RuntimeError: If ``simuhw.fp`` submodule is not available.

    Note:
        ``simuhw.fp`` submodule is available only when an appropriate version of
        `softfloatpy <https://pypi.org/project/softfloatpy/>`_ module is found.
        The least version can be retrieved using :func:`get_required_softfloatpy_least_version()`

    """
    if not _available:
        raise RuntimeError(_error_str)
