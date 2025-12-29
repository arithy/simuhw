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

import importlib.metadata
from packaging.version import Version

__all__ = ['is_available']

_softfloatpy_least: Version = Version('1.2.2')

_softfloatpy: Version | None = None
_available: bool = False

try:
    _softfloatpy = Version(importlib.metadata.version('softfloatpy'))
    if _softfloatpy < _softfloatpy_least:
        raise RuntimeError(
            f'Improper \'softfloatpy\' version: {_softfloatpy} < {_softfloatpy_least}'
        )

    _available = True

    __all__ += [
        'TininessMode', 'RoundingMode', 'ExceptionFlag',
        'UInt32', 'UInt64', 'Int32', 'Int64',
        'BFloat16', 'Float16', 'Float32', 'Float64', 'Float128',
        'set_tininess_mode', 'get_tininess_mode',
        'set_rounding_mode', 'get_rounding_mode',
        'set_exception_flags', 'get_exception_flags', 'test_exception_flags',
        'Float', 'FPState',
        'FPUnaryOperator', 'FPBinaryOperator', 'FPTernaryOperator',
        'SIMD_FPUnaryOperator', 'SIMD_FPBinaryOperator', 'SIMD_FPTernaryOperator'
    ]

    from softfloatpy import (
        TininessMode, RoundingMode, ExceptionFlag,
        UInt32, UInt64, Int32, Int64,
        BFloat16, Float16, Float32, Float64, Float128,
        set_tininess_mode, get_tininess_mode,
        set_rounding_mode, get_rounding_mode,
        set_exception_flags, get_exception_flags, test_exception_flags
    )
    from ._operator import (
        Float, FPState,
        FPUnaryOperator, FPBinaryOperator, FPTernaryOperator,
        SIMD_FPUnaryOperator, SIMD_FPBinaryOperator, SIMD_FPTernaryOperator
    )

except importlib.metadata.PackageNotFoundError:
    print(f'{__name__} [WARNING] No \'softfloatpy\' module')
except RuntimeError as e:
    print(f'{__name__} [WARNING] {e}')


def is_available() -> bool:
    return _available
