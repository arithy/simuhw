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

from collections.abc import Sequence
from random import Random
import math

from ._base import ArbitrationPolicy


class RandomArbitrationPolicy(ArbitrationPolicy):
    """A random arbitration policy."""

    def __init__(self, *, rng: Random = Random()) -> None:
        """Creates a random arbitration policy.

        Args:
            rng: The random number generator.

        """
        self._rng: Random = rng
        """The random number generator."""

    @property
    def rng(self) -> Random:
        """The random number generator."""
        return self._rng

    def select(self, targets: Sequence[tuple[bytes | None, float]]) -> int:
        """Selects one from the given inputs.

        Args:
            targets: The attributes of the targets to be selected.
                     They are specified as (*data word*, *time*).

        Returns:
            The index of the selected target.

        """
        return math.floor(len(targets) * self._rng.random())
