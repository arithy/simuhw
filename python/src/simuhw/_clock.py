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

import math

from ._type import Signal
from ._base import InputPort, OutputPort, Device


class Clock(Device):
    """A clock generator."""

    def __init__(self, period: float, *, phase: float = 0.0) -> None:
        """Creates a clock generator.

        Args:
            period: The period in seconds.
            phase: The phase in seconds.

        """
        super().__init__()
        self._period: float = period
        """The period in seconds."""
        self._phase: float = phase - period * math.floor(phase / period)  # normalize
        """The phase in seconds."""
        self._port_o: OutputPort = OutputPort(1)
        """The output port."""
        self._hcycle: int = 0
        """The number of half cycles."""

    @property
    def period(self) -> float:
        """The period in seconds."""
        return self._period

    @property
    def phase(self) -> float:
        """The phase in seconds."""
        return self._phase

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_o.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if time is None:
            if self._phase < self._period * 0.5:
                self._hcycle = 0
            else:
                self._hcycle = -1
        self._update_time_and_check_inputs(time)
        while True:
            t: float = self._phase + self._period * 0.5 * self._hcycle
            if t > self._time:
                return ([], t)
            self._hcycle += 1
            self._port_o.post(Signal((self._hcycle & 1).to_bytes(1), t))
