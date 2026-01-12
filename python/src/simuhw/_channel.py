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
from ._base import InputPort, OutputPort, Device


class Channel(Device):
    """A channel."""

    def __init__(self, width: int, *, latency: float, throughput: float) -> None:
        """Creates a channel.

        Args:
            width: The word width in bits.
            latency: The latency in seconds.
            throughput: The throughput in words per second.

        """
        super().__init__()
        self._width: int = width
        """The word width in bits."""
        self._latency: float = latency
        """The latency in seconds."""
        self._throughput: float = throughput
        """The throughput in words per second."""
        self._word_delay: float = width / throughput
        """The delay in seconds per word."""
        self._port_i: InputPort = InputPort(width)
        """The input port."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""
        self._queue: list[Signal] = []
        """The queue of words to be output later."""
        self._restore_time: float | None = None
        """The time to restore a stable state."""

    @property
    def width(self) -> int:
        """The word width in bits."""
        return self._width

    @property
    def latency(self) -> float:
        """The latency in seconds."""
        return self._latency

    @property
    def throughput(self) -> float:
        """The throughput in words per second."""
        return self._throughput

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
        self._port_i.reset()
        self._port_o.reset()
        self._queue.clear()

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
            if len(self._queue) > 0 and self._queue[-1].time > self._time and self._queue[-1].word != self._port_i.signal.word:
                self._queue.append(Signal(Unknown, self._time + self._word_delay))
                self._restore_time = self._time + self._word_delay
            else:
                self._queue.append(Signal(self._port_i.signal.word, self._time + self._word_delay))
                self._restore_time = None
            self._set_inputs_unchanged(ports_i)
        elif self._restore_time is not None and self._restore_time <= self._time:
            self._queue.append(Signal(self._port_i.signal.word, self._time + self._word_delay))
            self._restore_time = None
        elif time is None and not self._port_i.connected:  # if the input port is dangling
            self._port_o.post(Signal(HighZ, self._time))  # outputs immediately
        while len(self._queue) > 0 and self._queue[0].time + self._latency <= self._time:
            self._port_o.post(Signal(self._queue[0].word, self._queue[0].time + self._latency))
            self._queue.pop(0)
        return (
            ports_i,
            self._queue[0].time + self._latency if len(self._queue) > 0 else
            self._restore_time if self._restore_time is not None else None
        )
