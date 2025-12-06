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
from ._index_order import IndexOrderArbitrationPolicy


class DataOrderArbitrationPolicy(ArbitrationPolicy):
    """A data word order arbitration policy."""

    def __init__(
        self, *,
        select_min: bool = True, prioritize_none: bool = False,
        when_same: ArbitrationPolicy = IndexOrderArbitrationPolicy()
    ) -> None:
        """Creates a data word order arbitration policy.

        Args:
            select_min: `True` if the target with the minimum data word is to be selected.
                        `False` if the target with the maximum data word is to be selected.
            prioritize_none: `True` if the target with `None` data word is prioritized; `False` otherwise.
            when_same: The arbitration policy applied when there are multiple targets with the same data word.

        """
        self._select_min: bool = select_min
        """`True` if the target with the minimum data word is to be selected."""
        self._prioritize_none: bool = prioritize_none
        """`True` if the target with `None` data word is prioritized."""
        self._when_same: ArbitrationPolicy = when_same
        """The arbitration policy applied when there are multiple targets with the same data word."""

    @property
    def select_min(self) -> bool:
        """`True` if the target with the minimum data word is to be selected."""
        return self._select_min

    @property
    def prioritize_none(self) -> bool:
        """`True` if the target with `None` data word is prioritized."""
        return self._prioritize_none

    @property
    def when_same(self) -> ArbitrationPolicy:
        """The arbitration policy applied when there are multiple targets with the same data word."""
        return self._when_same

    def select(self, targets: Sequence[tuple[bytes | None, float]]) -> int:
        """Selects one from the given inputs.

        Args:
            targets: The attributes of the targets to be selected.
                     They are specified as (*data word*, *time*).

        Returns:
            The index of the selected target.

        """
        en: list[tuple[int, tuple[bytes | None, float]]] = [(i, t) for i, t in enumerate(targets) if t[0] is None]
        if len(en) == len(targets) or (len(en) > 0 and self._prioritize_none):
            return en[self._when_same.select([e[1] for e in en]) if len(en) > 1 else 0][0]
        bm: int = (
            min([int.from_bytes(t[0]) for t in targets if t[0] is not None]) if self._select_min else
            max([int.from_bytes(t[0]) for t in targets if t[0] is not None])
        )
        em: list[tuple[int, tuple[bytes | None, float]]] = [
            (i, t) for i, t in enumerate(targets) if t[0] is not None and int.from_bytes(t[0]) == bm
        ]
        return em[self._when_same.select([e[1] for e in em]) if len(em) > 1 else 0][0]
