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

import pytest

from simuhw.float import is_available, get_required_softfloatpy_least_version

__all__ = ['skipif_unavailable']

skipif_unavailable = pytest.mark.skipif(
    not is_available(),
    reason=f'\'float\' subpackage is not available (reason: \'softfloatpy\' version {get_required_softfloatpy_least_version()} or later is not found)'
)

if is_available():
    __all__ += [
        'set_tininess_mode', 'get_tininess_mode',
        'set_rounding_mode', 'get_rounding_mode',
        'set_exception_flags', 'get_exception_flags', 'test_exception_flags',
        'UInt32', 'UInt64', 'Int32', 'Int64'
    ]

    from softfloatpy import (
        set_tininess_mode, get_tininess_mode,
        set_rounding_mode, get_rounding_mode,
        set_exception_flags, get_exception_flags, test_exception_flags,
        UInt32, UInt64, Int32, Int64
    )
