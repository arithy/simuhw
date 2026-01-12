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

from .._type import Word, Unknown, Signal
from .._base import InputPort, OutputPort, Device
from .._analyzer import MemoryProbe
from .model._base import MemorizingModel


class Memory(Device, metaclass=ABCMeta):
    """The super class for all memory devices."""

    def __init__(self, width: int, width_a: int, model: MemorizingModel) -> None:
        """Creates a memory device.

        Args:
            width: The word width in bits.
            width_a: The address word width in bits.
            model: The memorizing model.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._width_a: int = width_a
        """The address word width in bits."""
        self._model: MemorizingModel = model
        """The memorizing model."""
        self._port_a: InputPort = InputPort(width_a)
        """The address port."""
        self._port_i: InputPort = InputPort(width)
        """The input port."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""
        self._probes: dict[MemoryProbe, bytes] = {}
        """The memory probes."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def width_a(self) -> int:
        """The address word width in bits."""
        return self._width

    @property
    def port_a(self) -> InputPort:
        """The address port."""
        return self._port_a

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._port_i

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._model.reset()
        self._port_a.reset()
        self._port_i.reset()
        self._port_o.reset()

    def add_probe(self, probe: MemoryProbe, address: bytes) -> None:
        """Adds a memory probe.

        Args:
            probe: The memory probe to be added.
            address: The probe address.

        Raises:
            ValueError: If a memory probe with a different word width is specified in ``probe``.

        """
        if self._width != probe.width:
            raise ValueError('inconsistent word width')
        self._probes[probe] = address

    def remove_probe(self, probe: MemoryProbe) -> None:
        """Removes a memory probe.

        Args:
            probe: The memory probe to be removed.

        Raises:
            ValueError: If a memory probe not yet added is specified in ``probe``.

        """
        if probe not in self._probes:
            raise ValueError('not added memory probe')
        self._probes.pop(probe)

    def remove_all_probes(self) -> None:
        """Removes all memory probes."""
        self._probes.clear()

    def _initialize_probes(self, exclude: Word = Unknown) -> None:
        for p in self._probes:
            if self._probes[p] != exclude:
                p.append(Signal(self._model.read(self._probes[p]), 0.0))

    def _update_probes(self, address: Word, signal: Signal) -> None:
        if isinstance(address, bytes):
            for p in self._probes:
                if self._probes[p] == address:
                    p.append(signal)
