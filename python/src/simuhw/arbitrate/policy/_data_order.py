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
from collections.abc import Iterable, Sequence

from ..._word import DataWord, Unknown, HighZ
from ._base import ArbitrationPolicy
from ._index_order import IndexOrderArbitrationPolicy


class DataOrderArbitrationPolicy(ArbitrationPolicy):
    """A data word order arbitration policy."""

    def __init__(
        self, *,
        select_min: bool = True, priority: Iterable[type[bytes | Unknown | HighZ]] = [bytes, Unknown, HighZ],
        when_same: ArbitrationPolicy = IndexOrderArbitrationPolicy()
    ) -> None:
        """Creates a data word order arbitration policy.

        Args:
            select_min: ``True`` if the target with the minimum data word is to be selected.
                        ``False`` if the target with the maximum data word is to be selected.
            priority: The target types in priority order.
            when_same: The arbitration policy applied when there are multiple targets with the same data word.

        """
        self._select_min: bool = select_min
        """``True`` if the target with the minimum data word is to be selected."""
        p: list[type[bytes | Unknown | HighZ]] = [*priority, bytes, Unknown, HighZ]
        self._priority: tuple[type[bytes | Unknown | HighZ], ...] = tuple(
            t for i, t in enumerate(p) if t not in p[:i]
        )  # has always 3 different elements
        """The target types in priority order."""
        assert len(self._priority) == 3
        assert len(set(self._priority)) == 3
        self._when_same: ArbitrationPolicy = when_same
        """The arbitration policy applied when there are multiple targets with the same data word."""

    @property
    def select_min(self) -> bool:
        """``True`` if the target with the minimum data word is to be selected."""
        return self._select_min

    @property
    def priority(self) -> tuple[type[bytes | Unknown | HighZ], ...]:
        """The target types in priority order."""
        return self._priority

    @property
    def when_same(self) -> ArbitrationPolicy:
        """The arbitration policy applied when there are multiple targets with the same data word."""
        return self._when_same

    def select(self, targets: Sequence[tuple[DataWord, float]]) -> int:
        """Selects one from the given inputs.

        Args:
            targets: The attributes of the targets to be selected.
                     They are specified as (*data word*, *time*).

        Returns:
            The index of the selected target.
            -1 if ``targets`` is empty.

        """
        for p in self._priority:
            s: list[tuple[int, tuple[DataWord, float]]] = [
                (i, t)
                for i, t in enumerate(targets) if (
                    (t[0] is Unknown) if p is Unknown else
                    (t[0] is HighZ) if p is HighZ else
                    isinstance(t[0], bytes)
                )
            ]
            if len(s) > 0 and p is bytes:
                l: list[bytes] = [d[1][0] for d in cast(list[tuple[int, tuple[bytes, float]]], s)]
                m: bytes = min(l) if self._select_min else max(l)
                s = [d for d in s if d[1][0] == m]
            if len(s) == 1:
                return s[0][0]
            if len(s) > 1:
                return s[self._when_same.select([d[1] for d in s])][0]
        return -1
