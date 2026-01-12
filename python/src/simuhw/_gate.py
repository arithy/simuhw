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
from functools import reduce

from ._type import Unknown, Signal
from ._base import InputPort
from ._operator import Operator


class ANDGate(Operator):
    """An AND gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an AND gate.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, width, ninputs=ninputs)

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else (
                    reduce(lambda x, y: x & y, (int.from_bytes(cast(bytes, p.signal.word)) for p in self._ports_i), self._mask)
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class ORGate(Operator):
    """An OR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an OR gate.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, width, ninputs=ninputs)

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else (
                    reduce(lambda x, y: x | y, (int.from_bytes(cast(bytes, p.signal.word)) for p in self._ports_i), 0)
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class XORGate(Operator):
    """An XOR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an XOR gate.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, width, ninputs=ninputs)

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else (
                    reduce(lambda x, y: x ^ y, (int.from_bytes(cast(bytes, p.signal.word)) for p in self._ports_i), 0)
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class NANDGate(Operator):
    """A NAND gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates a NAND gate.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, width, ninputs=ninputs)

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else (
                    ~reduce(lambda x, y: x & y, (int.from_bytes(cast(bytes, p.signal.word)) for p in self._ports_i), self._mask) & self._mask
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class NORGate(Operator):
    """A NOR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates a NOR gate.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, width, ninputs=ninputs)

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else (
                    ~reduce(lambda x, y: x | y, (int.from_bytes(cast(bytes, p.signal.word)) for p in self._ports_i), 0) & self._mask
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class XNORGate(Operator):
    """An XNOR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an XNOR gate.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, width, ninputs=ninputs)

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else (
                    ~reduce(lambda x, y: x ^ y, (int.from_bytes(cast(bytes, p.signal.word)) for p in self._ports_i), 0) & self._mask
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)
