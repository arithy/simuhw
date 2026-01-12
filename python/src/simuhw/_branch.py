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
from collections.abc import Iterable
from functools import reduce
import math

from ._type import Word, Unknown, HighZ, Signal
from ._base import InputPort, OutputPort, Device, combine_bits, extract_bits


class WordCombiner(Device):
    """A word combiner.

    This device combines multiple input words into one word.
    The word from the first input port will be the most significant bits
    in the output word.

    """

    def __init__(self, widths: Iterable[int]) -> None:
        """Creates a word combiner.

        Args:
            widths: The input word widths in bits.

        """
        super().__init__()
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(w) for w in widths)
        """The input ports."""
        self._port_o: OutputPort = OutputPort(sum(widths))
        """The output port."""

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
                Unknown if any((not isinstance(p.signal.word, bytes) for p in self._ports_i)) else reduce(
                    lambda x, y: (x[0] + y[0], combine_bits(x[0], x[1], y[0], y[1])),
                    ((p.width, cast(bytes, p.signal.word)) for p in self._ports_i), (0, b'')
                )[1],
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class WordSplitter(Device):
    """A word splitter.

    This device splits an input word into multiple words.
    The most significant bits in the input word will be output to the first output port.

    """

    def __init__(self, widths: Iterable[int]) -> None:
        """Creates a word splitter.

        Args:
            widths: The output word widths in bits.

        """
        super().__init__()
        self._port_i: InputPort = InputPort(sum(widths))
        """The input port."""
        self._ports_o: tuple[OutputPort, ...] = tuple(OutputPort(w) for w in widths)
        """The output ports."""

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._port_i

    @property
    def ports_o(self) -> tuple[OutputPort, ...]:
        """The output ports."""
        return self._ports_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_i.reset()
        for p in self._ports_o:
            p.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i]
        if self._update_time_and_check_inputs(time, ports_i):
            b: Word = self._port_i.signal.word
            if not isinstance(b, bytes):
                for p in self._ports_o:
                    p.post(Signal(Unknown, self._time))
            else:
                s: int = self._port_i.width
                for p in self._ports_o:
                    s -= p.width
                    p.post(Signal(extract_bits(self._port_i.width, b, s, p.width), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class Multiplexer(Device):
    """A multiplexer."""

    def __init__(self, width: int, ninputs: int) -> None:
        """Creates a multiplexer.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._width_s: int = math.ceil(math.log2(ninputs)) if ninputs > 0 else 0
        """The selection port width in bits."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width) for _ in range(ninputs))
        """The input ports."""
        self._port_s: InputPort = InputPort(self._width_s)
        """The selection port."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def width_s(self) -> int:
        """The selection port width in bits."""
        return self._width_s

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports."""
        return self._ports_i

    @property
    def port_s(self) -> InputPort:
        """The selection port."""
        return self._port_s

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in self._ports_i:
            p.reset()
        self._port_s.reset()
        self._port_o.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if not isinstance(self._port_s.signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                i: int = int.from_bytes(self._port_s.signal.word)
                self._port_o.post(Signal(
                    self._ports_i[i].signal.word if i < len(self._ports_i) else Unknown,
                    self._time
                ))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class Demultiplexer(Device):
    """A demultiplexer."""

    def __init__(self, width: int, noutputs: int, *, deselected: Word = Unknown) -> None:
        """Creates a demultiplexer.

        Args:
            width: The word width in bits.
            noutputs: The number of the output ports.
            deselected: The word to be output to ports not selected.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._width_s: int = math.ceil(math.log2(noutputs)) if noutputs > 0 else 0
        """The selection port width in bits."""
        self._deselected: Word = deselected
        """The word to be output to ports not selected."""
        self._port_i: InputPort = InputPort(width)
        """The input port."""
        self._port_s: InputPort = InputPort(self._width_s)
        """The selection port."""
        self._ports_o: tuple[OutputPort, ...] = tuple(OutputPort(width) for _ in range(noutputs))
        """The output ports."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def width_s(self) -> int:
        """The selection port width in bits."""
        return self._width_s

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._port_i

    @property
    def port_s(self) -> InputPort:
        """The selection port."""
        return self._port_s

    @property
    def ports_o(self) -> tuple[OutputPort, ...]:
        """The output ports."""
        return self._ports_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_i.reset()
        self._port_s.reset()
        for p in self._ports_o:
            p.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if isinstance(self._port_s.signal.word, bytes):
                s: int = int.from_bytes(self._port_s.signal.word)
                for i, p in enumerate(self._ports_o):
                    if i == s:
                        p.post(Signal(self._port_i.signal.word, self._time))
                    else:
                        p.post(Signal(self._deselected, self._time))
            else:
                for i, p in enumerate(self._ports_o):
                    p.post(Signal(Unknown, self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class WordRetainingDemultiplexer(Demultiplexer):
    """A demultiplexer to retain word in the unselected ports."""

    def __init__(self, width: int, noutputs: int) -> None:
        """Creates a demultiplexer to retain word in the unselected ports.

        Args:
            width: The word width in bits.
            noutputs: The number of the output ports.

        """
        super().__init__(width, noutputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if isinstance(self._port_s.signal.word, bytes):
                s: int = int.from_bytes(self._port_s.signal.word)
                for i, p in enumerate(self._ports_o):
                    if i == s:
                        p.post(Signal(self._port_i.signal.word, self._time))
            else:
                for i, p in enumerate(self._ports_o):
                    p.post(Signal(Unknown, self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class Junction(Device):
    """A junction.

    This device merges multiple inputs.
    Its behavior is that of directly connected multiple input wires.

    """

    def __init__(self, width: int, ninputs: int) -> None:
        """Creates a junction.

        Args:
            width: The word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width) for _ in range(ninputs))
        """The input ports."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""

    @property
    def width(self) -> int:
        """The word width in bits."""
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

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i]
        if self._update_time_and_check_inputs(time, ports_i):
            bs: list[Word] = [p.signal.word for p in self._ports_i if p.connected and p.signal.word is not HighZ]
            if len(bs) == 0:
                self._port_o.post(Signal(HighZ, self._time))
            elif all((b == bs[0] for b in bs)):
                self._port_o.post(Signal(bs[0], self._time))
            else:
                self._port_o.post(Signal(Unknown, self._time))
            self._set_inputs_unchanged(ports_i)
        elif time is None and all((not p.connected for p in self._ports_i)):  # if all input ports are dangling or no input port exists
            self._port_o.post(Signal(HighZ, self._time))
        return (ports_i, None)


class Distributor(Device):
    """A distributor.

    This device forwards the input word to multiple output ports.
    Its behavior is that of directly connected multiple output wires.

    """

    def __init__(self, width: int, noutputs: int) -> None:
        """Creates a distributor.

        Args:
            width: The word width in bits.
            noutputs: The number of the output ports.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._port_i: InputPort = InputPort(width)
        """The input port."""
        self._ports_o: tuple[OutputPort, ...] = tuple(OutputPort(width) for _ in range(noutputs))
        """The output ports."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._port_i

    @property
    def ports_o(self) -> tuple[OutputPort, ...]:
        """The output ports."""
        return self._ports_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_i.reset()
        for p in self._ports_o:
            p.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i]
        if self._update_time_and_check_inputs(time, ports_i):
            for p in self._ports_o:
                p.post(Signal(self._port_i.signal.word, self._time))
            self._set_inputs_unchanged(ports_i)
        elif time is None and not self._port_i.connected:  # if the input port is dangling
            for p in self._ports_o:
                p.post(Signal(HighZ, self._time))
        return (ports_i, None)
