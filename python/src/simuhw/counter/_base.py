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

from .._type import Word, Unknown
from .._base import InputPort, OutputPort, Device


class Counter(Device, metaclass=ABCMeta):
    """The super class for all counters."""

    def __init__(self, width: int) -> None:
        """Creates a counter.

        Args:
            width: The word width in bits.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._nbytes: int = (width + 7) >> 3
        """The number of bytes required to represent the output."""
        self._mask: int = (1 << width) - 1
        """The mask."""
        self._port_d: InputPort = InputPort(width)
        """The load input port."""
        self._port_q: OutputPort = OutputPort(width)
        """The count output port."""
        self._port_co: OutputPort = OutputPort(1)
        """The carry output port."""
        self._count: Word = Unknown
        """The count."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def port_d(self) -> InputPort:
        """The load input port."""
        return self._port_d

    @property
    def port_q(self) -> OutputPort:
        """The count output port."""
        return self._port_q

    @property
    def port_co(self) -> OutputPort:
        """The carry output port.

        The width is 1 bit.

        """
        return self._port_co

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_d.reset()
        self._port_q.reset()
        self._port_co.reset()


class SynchronousCounter(Counter, metaclass=ABCMeta):
    """The super class for all synchronous counters."""

    def __init__(self, width: int, *, neg_edged: bool) -> None:
        """Creates a synchronous counter.

        Args:
            width: The word width in bits.
            neg_edged: ``True`` if negative-edged, ``False`` otherwise.

        """
        super().__init__(width)
        self._neg_edged = neg_edged
        """``True`` if negative-edged, ``False`` otherwise."""
        self._port_ck: InputPort = InputPort(1)
        """The clock port."""
        self._prev_ck: Word = Unknown
        """The previous clock word."""

    @property
    def negative_edged(self) -> bool:
        """``True`` if negative-edged, ``False`` otherwise."""
        return self._neg_edged

    @property
    def port_ck(self) -> InputPort:
        """The clock port.

        The width is 1 bit.

        """
        return self._port_ck

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_ck.reset()


class SynchronousBinaryCounter(SynchronousCounter, metaclass=ABCMeta):
    """The super class for all synchronous binary counters."""

    def __init__(self, width: int, *, neg_edged: bool) -> None:
        """Creates a synchronous binary counter.

        Args:
            width: The word width in bits.
            neg_edged: ``True`` if negative-edged, ``False`` otherwise.

        """
        super().__init__(width, neg_edged=neg_edged)
