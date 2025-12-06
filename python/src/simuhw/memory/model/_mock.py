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

from collections.abc import Callable

from ._base import MemorizingModel


class MockMemorizingModel(MemorizingModel):
    """A mock memorizing model."""

    def __init__(self, data_func: Callable[[bytes | None], bytes | None] | None = None) -> None:
        """Creates a mock memorizing model.

        Args:
            data_func: The function to return a mock data according to a given address.

        """
        self._data_func: Callable[[bytes | None], bytes | None] | None = data_func
        """The function to return a mock data according to a given address."""

    def reset(self) -> None:
        """Resets the states."""
        pass

    def read(self, address: bytes | None) -> bytes | None:
        """Reads the data word from the memory device.

        Args:
            address: The memory address whose data is to be read.

        Returns:
            The data word read form the specified memory address.

        """
        return None if self._data_func is None else self._data_func(address)

    def write(self, address: bytes | None, data: bytes | None) -> None:
        """Writes the data word to the memory device.

        Args:
            address: The memory address whose data is to be written.
            data: the data word to be written to the specified memory address.

        """
        pass
