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

from abc import ABCMeta, abstractmethod

from ..._type import Word


class MemorizingModel(metaclass=ABCMeta):
    """The super class for all memorizing models."""

    @abstractmethod
    def reset(self) -> None:
        """Resets the states."""
        pass

    @abstractmethod
    def read(self, address: Word) -> Word:
        """Reads the word from the memory device.

        Args:
            address: The memory address whose word is to be read.

        Returns:
            The word read form the specified memory address.

        """
        pass

    @abstractmethod
    def write(self, address: Word, word: Word) -> None:
        """Writes the word to the memory device.

        Args:
            address: The memory address whose word is to be updated.
            word: the word to be written to the specified memory address.

        """
        pass
