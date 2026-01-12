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

from ._type import Unknown, Signal
from ._base import InputPort, OutputPort, Device


class DLatch(Device):
    """A D latch."""

    def __init__(self, width: int, *, neg_leveled: bool = False) -> None:
        """Creates a D latch.

        Args:
            width: The word width in bits.
            neg_leveled: ``True`` if negative-leveled, ``False`` otherwise.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._neg_leveled = neg_leveled
        """``True`` if negative-leveled, ``False`` otherwise."""
        self._port_g: InputPort = InputPort(1)
        """The gate port."""
        self._port_i: InputPort = InputPort(width)
        """The input port."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def negative_leveled(self) -> bool:
        """``True`` if negative-leveled, ``False`` otherwise."""
        return self._neg_leveled

    @property
    def port_g(self) -> InputPort:
        """The gate port."""
        return self._port_g

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
        self._port_g.reset()
        self._port_i.reset()
        self._port_o.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_g, self._port_i]
        if self._update_time_and_check_inputs(time, ports_i):
            if not isinstance(self._port_g.signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            elif int.from_bytes(self._port_g.signal.word) == (0 if self._neg_leveled else 1):
                self._port_o.post(Signal(self._port_i.signal.word, self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
