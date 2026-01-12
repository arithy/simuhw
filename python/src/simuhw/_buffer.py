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

from ._type import Unknown, HighZ, Signal
from ._base import InputPort
from ._operator import UnaryOperator


class Buffer(UnaryOperator):
    """A buffer."""

    def __init__(self, width: int) -> None:
        """Creates a buffer.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)

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
                Unknown if not isinstance(self._ports_i[0].signal.word, bytes) else self._ports_i[0].signal.word,
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class Inverter(Buffer):
    """An inverter."""

    def __init__(self, width: int) -> None:
        """Creates an inverter.

        Args:
            width: The word width in bits.

        """
        super().__init__(width)

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
                Unknown if not isinstance(self._ports_i[0].signal.word, bytes) else (
                    ~int.from_bytes(self._ports_i[0].signal.word) & self._mask
                ).to_bytes(self._nbytes),
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return ([*self._ports_i], None)


class TriStateBuffer(UnaryOperator):
    """A tri-state buffer."""

    def __init__(self, width: int, *, active_high: bool = True) -> None:
        """Creates a tri-state buffer.

        Args:
            width: The word width in bits.
            active_high: ``True`` if the control port is active-high, ``False`` if it is active-low.

        """
        super().__init__(width)
        self._active_high: bool = active_high
        """``True`` if the control port is active-high, ``False`` if it is active-low."""
        self._port_c: InputPort = InputPort(1)
        """The control port."""

    @property
    def active_high(self) -> bool:
        """``True`` if the control port is active-high, ``False`` if it is active-low."""
        return self._active_high

    @property
    def port_i(self) -> InputPort:
        """The input port."""
        return self._ports_i[0]

    @property
    def port_c(self) -> InputPort:
        """The control port."""
        return self._port_c

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_c]
        if self._update_time_and_check_inputs(time, ports_i):
            if not isinstance(self._port_c.signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                self._port_o.post(Signal(
                    HighZ if int.from_bytes(self._port_c.signal.word) == (0 if self._active_high else 1) else
                    Unknown if not isinstance(self._ports_i[0].signal.word, bytes) else self._ports_i[0].signal.word,
                    self._time
                ))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class TriStateInverter(TriStateBuffer):
    """A tri-state inverter."""

    def __init__(self, width: int, *, active_high: bool = True) -> None:
        """Creates a tri-state inverter.

        Args:
            width: The word width in bits.
            active_high: ``True`` if the control port is active-high, ``False`` if it is active-low.

        """
        super().__init__(width, active_high=active_high)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_c]
        if self._update_time_and_check_inputs(time, ports_i):
            if not isinstance(self._port_c.signal.word, bytes):
                self._port_o.post(Signal(Unknown, self._time))
            else:
                self._port_o.post(Signal(
                    HighZ if int.from_bytes(self._port_c.signal.word) == (0 if self._active_high else 1) else
                    Unknown if not isinstance(self._ports_i[0].signal.word, bytes) else (
                        ~int.from_bytes(self._ports_i[0].signal.word) & self._mask
                    ).to_bytes(self._nbytes),
                    self._time
                ))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
