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


class TimeOrderArbitrationPolicy(ArbitrationPolicy):
    """A time order arbitration policy."""

    def __init__(
        self, *,
        select_min: bool = True,
        when_same: ArbitrationPolicy = IndexOrderArbitrationPolicy()
    ) -> None:
        """Creates a time order arbitration policy.

        Args:
            select_min: `True` if the target with the minimum time is to be selected.
                        `False` if the target with the maximum time is to be selected.
            when_same: The arbitration policy applied when there are multiple targets with the same time.

        """
        self._select_min: bool = select_min
        """`True` if the target with the minimum time is to be selected."""
        self._when_same: ArbitrationPolicy = when_same
        """The arbitration policy applied when there are multiple targets with the same time."""

    @property
    def select_min(self) -> bool:
        """`True` if the target with the minimum time is to be selected."""
        return self._select_min

    @property
    def when_same(self) -> ArbitrationPolicy:
        """The arbitration policy applied when there are multiple targets with the same time."""
        return self._when_same

    def select(self, targets: Sequence[tuple[bytes | None, float]]) -> int:
        """Selects one from the given inputs.

        Args:
            targets: The attributes of the targets to be selected.
                     They are specified as (*data word*, *time*).

        Returns:
            The index of the selected target.

        """
        tm: float = (
            min([t[1] for t in targets]) if self._select_min else
            max([t[1] for t in targets])
        )
        em: list[tuple[int, tuple[bytes | None, float]]] = [(i, t) for i, t in enumerate(targets) if t[1] == tm]
        return em[self._when_same.select([e[1] for e in em]) if len(em) > 1 else 0][0]
