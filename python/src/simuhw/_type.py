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

from abc import ABCMeta


class Unknown(metaclass=ABCMeta):
    """The unknown state."""
    pass


class HighZ(metaclass=ABCMeta):
    """The high impedance state."""
    pass


Word = bytes | type[Unknown | HighZ]


class Signal:
    """A signal."""

    def __init__(self, word: Word, time: float) -> None:
        """Creates a signal.

        Args:
            word: The word.
            time: The time in seconds.

        """
        self._word: Word = word
        """The word."""
        self._time: float = time
        """The time in seconds."""

    @property
    def word(self) -> Word:
        """The word."""
        return self._word

    @property
    def time(self) -> float:
        """The time in seconds."""
        return self._time

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._word!r}, {self._time})'
