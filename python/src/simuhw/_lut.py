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

from collections.abc import Iterable

from ._type import Unknown, Signal
from ._base import InputPort
from ._operator import UnaryOperator


class LookupTable(UnaryOperator):
    """A lookup Table device.

    This device outputs words according to inputs by referring to the preset lookup table.

    """

    def __init__(self, width_i: int, width_o: int, table: Iterable[bytes]) -> None:
        """Creates a lookup table device.

        Args:
            width_i: The input word width in bits.
            width_o: The output word width in bits.
                     If a negative value is specified, ``width_i`` is used instead.
            table: The table data.
                   The bit width of every list element must be ``width_o``,
                   and the number of list elements must be 2 to the power of ``width_i``.

        Raises:
            ValueError: If the size of the table data and ``width_i`` are inconsistent.

        Caution:
            As ``width_i`` is large, the amount of memory required to retain the table data becomes huge exponentially.

        """
        super().__init__(width_i, width_o)
        self._table: list[bytes] = [*table]
        """The table data."""
        if len(self._table) != 2**self._width_i:
            raise ValueError(f'Inconsistent table size for input word width {self._width_i}: {len(self._table)} != {2**self._width_i}')

    def updata_table(self, table: Iterable[bytes]) -> None:
        """Updates the table data.

        Args:
            table: The table data.
                   The bit width of every list element must be ``width_o``,
                   and the number of list elements must be 2 to the power of ``width_i``.

        Raises:
            ValueError: If the size of the table data and ``width_i`` are inconsistent.

        """
        self._table = [*table]
        if len(self._table) != 2**self._width_i:
            raise ValueError(f'Inconsistent table size for input word width {self._width_i}: {len(self._table)} != {2**self._width_i}')

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post(Signal(
                self._table[int.from_bytes(self._ports_i[0].signal.word)] if isinstance(self._ports_i[0].signal.word, bytes) else Unknown,
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)
