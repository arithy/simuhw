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
from collections.abc import Iterable

from ._type import Word, Unknown, HighZ, Signal
from ._analyzer import ChannelProbe


def combine_bits(nbits0: int, bits0: bytes, nbits1: int, bits1: bytes) -> bytes:
    """Returns the bit sequence obtained by combining the specified bit sequences.

    Args:
        nbits0: The number of bits in the bit sequence ``bits0``.
        bits0: The bit sequence to be the left bits in the combined bit sequence.
        nbits1: The number of bits in the bit sequence ``bits1``.
        bits1: The bit sequence to be the right bits in the combined bit sequence.

    Returns:
        The bit sequence obtained by combining the specified bit sequences.

    """
    return (
        ((int.from_bytes(bits0) & ((1 << nbits0) - 1)) << nbits1) | (int.from_bytes(bits1) & ((1 << nbits1) - 1))
    ).to_bytes((nbits0 + nbits1 + 7) >> 3)


def extract_bits(nbits: int, bits: bytes, start: int, length: int) -> bytes:
    """Returns the new bit sequence extracted from the specified bit sequence.

    Args:
        nbits: The number of bits in the bit sequence ``bits``.
        bits: The bit sequence from which the bit sequence is to be extracted.
        start: The start bit position in the bit sequence ``bits`` from which the new bit sequence is to be extracted.
        length: The length in bits of the new bit sequence.

    Returns:
        The bit sequence extracted from the specified bit sequence.

    """
    return ((int.from_bytes(bits) >> start) & ((1 << length) - 1)).to_bytes((length + 7) >> 3)


def to_signed_int(nbits: int, value: int) -> int:
    """Returns the signed integer converted from the specified unsigned integer with the specified bits.

    Args:
        nbits: The number of bits of the unsigned integer.
        value: The unsigned integer.

    Returns:
        The signed integer converted from the specified unsigned integer with the specified bits.

    """
    return value if nbits <= 0 or (value >> (nbits - 1)) & 1 == 0 else -((~value + 1) & ((1 << nbits) - 1))


class Port(metaclass=ABCMeta):
    """The super class for all ports."""

    def __init__(self, width: int) -> None:
        """Creates a port.

        Args:
            width: The word width in bits.

        """
        self._width: int = width
        """The word width in bits."""
        self._signal: Signal = Signal(Unknown, 0.0)
        """The latest signal."""
        self._probes: list[ChannelProbe] = []
        """The channel probes."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def signal(self) -> Signal:
        """The latest signal."""
        return self._signal

    def reset(self) -> None:
        """Resets the states."""
        self._signal = Signal(Unknown, 0.0)

    def add_probe(self, probe: ChannelProbe) -> None:
        """Adds a channel probe.

        Args:
            probe: The channel probe to be added.

        Raises:
            ValueError: If a channel probe with a different word width is specified in ``probe``.

        """
        if self._width != probe.width:
            raise ValueError('inconsistent word width')
        if probe not in self._probes:
            self._probes.append(probe)

    def remove_probe(self, probe: ChannelProbe) -> None:
        """Removes a channel probe.

        Args:
            probe: The channel probe to be removed.

        Raises:
            ValueError: If a channel probe not yet added is specified in ``probe``.

        """
        if probe not in self._probes:
            raise ValueError('not added channel probe')
        self._probes.remove(probe)

    def remove_all_probes(self) -> None:
        """Removes all channel probes."""
        self._probes.clear()


class InputPort(Port):
    """An input port to receive signals from an output port."""

    def __init__(self, width: int) -> None:
        """Creates an input port.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)
        self._connected: bool = False
        """``True`` if connected to an output port, ``False`` otherwise."""
        self._changed: bool = False
        """``True`` if the signal word has been changed, ``False`` otherwise."""

    @property
    def connected(self) -> bool:
        """``True`` if connected to an output port, ``False`` otherwise."""
        return self._connected

    def mark_as_connected(self) -> None:
        """Marks this object as connected to an output port."""
        self._connected = True

    def mark_as_disconnected(self) -> None:
        """Marks this object as disconnected from an output port."""
        self._connected = False

    @property
    def changed(self) -> bool:
        """``True`` if the signal word has been changed, ``False`` otherwise."""
        return self._changed

    def mark_as_changed(self) -> None:
        """Marks the signal word as changed."""
        self._changed = True

    def mark_as_unchanged(self) -> None:
        """Marks the signal word as unchanged."""
        self._changed = False

    def post(self, signal: Signal) -> None:
        """Posts the signal to this port.

        Args:
            signal: The signal to be posted.

        """
        if self._signal.word != signal.word:
            self._signal = signal
            for p in self._probes:
                p.append(signal)
            self._changed = True


class OutputPort(Port):
    """An output port to send signals to an input port."""

    def __init__(self, width: int) -> None:
        """Creates an output port.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)
        self._peer: InputPort | None = None
        """The input port. ``None`` if no connected input port."""

    @property
    def peer(self) -> InputPort | None:
        """The input port. ``None`` if no connected input port."""
        return self._peer

    @property
    def connected(self) -> bool:
        """``True`` if connected to an input port, ``False`` otherwise."""
        return self._peer is not None

    def connect(self, peer: InputPort | None) -> None:
        """Connects to an input port, or disconnect.

        Args:
            peer: The input port. The connected input port is disconnected if ``None``.

        Raises:
            ValueError: If an input port with a different word width is specified in ``peer``.

        """
        if self._peer is not None and self._peer is not peer:
            p: InputPort = self._peer
            self._peer = None  # This is done first to avoid infinite recursive calls between InputPort.mark_as_connected() and OutputPort.connect().
            p.mark_as_disconnected()
        if peer is not None and peer is not self._peer:
            if self._width != peer.width:
                raise ValueError('inconsistent word width')
            self._peer = peer  # This is done first to avoid infinite recursive calls between InputPort.mark_as_connected() and OutputPort.connect().
            peer.mark_as_connected()

    def post(self, signal: Signal) -> None:
        """Posts the signal to this port.

        Args:
            signal: The signal to be posted.

        """
        if self._signal.word != signal.word:
            self._signal = signal
            for p in self._probes:
                p.append(signal)
            if self._peer is not None:
                self._peer.post(signal)


class Device(metaclass=ABCMeta):
    """The super class for all devices."""

    def __init__(self) -> None:
        """Creates a device."""
        self._time: float = 0.0
        """The next resuming time in seconds."""

    @property
    def time(self) -> float:
        """The next resuming time in seconds."""
        return self._time

    def _update_time_and_check_inputs(self, time: float | None, ports_i: Iterable[InputPort] = []) -> bool:
        self._time = 0.0 if time is None else time
        assert all((p.signal.time <= self._time for p in ports_i))
        return any((p.changed for p in ports_i))

    def _set_inputs_unchanged(self, ports_i: Iterable[InputPort] = []) -> None:
        for p in ports_i:
            p.mark_as_unchanged()

    @abstractmethod
    def reset(self) -> None:
        """Resets the states."""
        self._time = 0.0

    @abstractmethod
    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        pass


class Source(Device):
    """A source device to emit signals."""

    def __init__(self, width: int, signals: Iterable[Signal | tuple[Word, float]]) -> None:
        """Creates a source device.

        Args:
            width: The word width in bits.
            signals: The iterator to supply signals.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._signals: list[Signal] = [g if isinstance(g, Signal) else Signal(g[0], g[1]) for g in signals]
        """The signals to be emitted."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""
        self._index: int = 0
        """The index of the next signal to be emitted."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_o.reset()
        self._index = 0

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if time is None:
            self._index = 0
        self._update_time_and_check_inputs(time)
        while self._index < len(self._signals):
            g: Signal = self._signals[self._index]
            if self._time < g.time:
                return ([], g.time)
            self._port_o.post(g)
            self._index += 1
        return ([], None)


class LogicLowSource(Source):
    """A source device to hold a logic-low word."""

    def __init__(self, width: int) -> None:
        """Creates a source device to hold a logic-low word.

        Args:
            width: The word width in bits.

        """
        super().__init__(width, [((0).to_bytes((width + 7) >> 3), 0.0)])


class LogicHighSource(Source):
    """A source device to hold a logic-high word."""

    def __init__(self, width: int) -> None:
        """Creates a source device to hold a logic-high word.

        Args:
            width: The word width in bits.

        """
        super().__init__(width, [(((1 << width) - 1).to_bytes((width + 7) >> 3), 0.0)])


class LogicUnknownSource(Source):
    """A source device to hold a logic-unknown word."""

    def __init__(self, width: int) -> None:
        """Creates a source device to hold a logic-unknown word.

        Args:
            width: The word width in bits.

        """
        super().__init__(width, [Signal(Unknown, 0.0)])


class HighZSource(Source):
    """A source device to hold high impedance."""

    def __init__(self, width: int) -> None:
        """Creates a source device to hold high impedance.

        Args:
            width: The word width in bits.

        """
        super().__init__(width, [(HighZ, 0.0)])


class Drain(Device):
    """A drain device to absorb signals."""

    def __init__(self, width: int) -> None:
        """Creates a drain device.

        Args:
            width: The word width in bits.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._port_i: InputPort = InputPort(width)
        """The input port."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._port_i

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_i.reset()

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
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
