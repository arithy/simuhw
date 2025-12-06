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

from abc import ABCMeta
from functools import reduce

from ._base import InputPort, OutputPort, Device


class Gate(Device, metaclass=ABCMeta):
    """The super class for all gates."""

    def __init__(self, width: int, *, ninputs: int) -> None:
        """Creates a gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._mask: int = (1 << width) - 1
        """The mask."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width) for _ in range(ninputs))
        """The input ports."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports."""
        return self._ports_i

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in self._ports_i:
            p.reset()
        self._port_o.reset()


class BufferGate(Gate):
    """A buffer gate."""

    def __init__(self, width: int) -> None:
        """Creates a buffer gate.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width, ninputs=1)

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._ports_i[0]

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                self._ports_i[0].data[0],
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class NOTGate(Gate):
    """A NOT gate."""

    def __init__(self, width: int) -> None:
        """Creates a NOT gate.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width, ninputs=1)

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._ports_i[0]

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if self._ports_i[0].data[0] is None else (
                    ~int.from_bytes(self._ports_i[0].data[0]) & self._mask
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class ANDGate(Gate):
    """An AND gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an AND gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, ninputs=ninputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else (
                    reduce(lambda x, y: x & y, (int.from_bytes(p.data[0]) for p in self._ports_i), self._mask)  # type: ignore
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class ORGate(Gate):
    """An OR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an OR gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, ninputs=ninputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else (
                    reduce(lambda x, y: x | y, (int.from_bytes(p.data[0]) for p in self._ports_i), 0)  # type: ignore
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class XORGate(Gate):
    """An XOR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an XOR gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, ninputs=ninputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else (
                    reduce(lambda x, y: x ^ y, (int.from_bytes(p.data[0]) for p in self._ports_i), 0)  # type: ignore
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class NANDGate(Gate):
    """A NAND gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates a NAND gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, ninputs=ninputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else (
                    ~reduce(lambda x, y: x & y, (int.from_bytes(p.data[0]) for p in self._ports_i), self._mask) & self._mask  # type: ignore
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class NORGate(Gate):
    """A NOR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates a NOR gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, ninputs=ninputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else (
                    ~reduce(lambda x, y: x | y, (int.from_bytes(p.data[0]) for p in self._ports_i), 0) & self._mask  # type: ignore
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class XNORGate(Gate):
    """An XNOR gate."""

    def __init__(self, width: int, *, ninputs: int = 2) -> None:
        """Creates an XNOR gate.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__(width, ninputs=ninputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else (
                    ~reduce(lambda x, y: x ^ y, (int.from_bytes(p.data[0]) for p in self._ports_i), 0) & self._mask  # type: ignore
                ).to_bytes(),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)
