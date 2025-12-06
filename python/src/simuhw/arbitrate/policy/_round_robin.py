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

from ._base import ArbitrationPolicy


class RoundRobinArbitrationPolicy(ArbitrationPolicy):
    """A round-robin arbitration policy."""

    def __init__(self, *, initial: int = 0) -> None:
        """Creates a round-robin arbitration policy.

        Args:
            initial: The initial index.

        """
        self._next: int = initial
        """The next index."""

    @property
    def next(self) -> int:
        """The next index."""
        return self._next

    def select(self, targets: Sequence[tuple[bytes | None, float]]) -> int:
        """Selects one from the given inputs.

        Args:
            targets: The attributes of the targets to be selected.
                     They are specified as (*data word*, *time*).

        Returns:
            The index of the selected target.

        """
        i: int = self._next % len(targets)  # in case where the number of the targets varies whenever called
        self._next = (self._next + 1) % len(targets)
        return i
