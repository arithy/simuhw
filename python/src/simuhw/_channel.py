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

from ._base import InputPort, OutputPort, Device
from ._group import Group
from ._branch import DataCombiner, DataSplitter, Arbitrator, DataRetainingDemultiplexer
from .arbitrate.policy._base import ArbitrationPolicy
from .arbitrate.policy._time_order import TimeOrderArbitrationPolicy


class Channel(Device):
    """A channel."""

    def __init__(self, width: int, *, latency: float, throughput: float) -> None:
        """Creates a channel.

        Args:
            width: The data word width in bits.
            latency: The latency in seconds.
            throughput: The throughput in words per second.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
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
        self._queue: list[tuple[bytes | None, float]] = []
        """The queue of data words to be output later."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
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
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i]
        if self._update_time_and_check_inputs(time, ports_i):
            self._queue.append((
                None if len(self._queue) > 0 and self._queue[-1][1] > self._time and self._queue[-1][0] != self._port_i.data[0] else self._port_i.data[0],
                self._time + self._word_delay
            ))
            self._set_inputs_unchanged(ports_i)
        while len(self._queue) > 0 and self._queue[0][1] + self._latency <= self._time:
            self._port_o.post((self._queue[0][0], self._queue[0][1] + self._latency))
            self._queue.pop(0)
        return (ports_i, self._queue[0][1] + self._latency if len(self._queue) > 0 else None)


class MultiplexChannel(Device):
    """A multiplex channel."""

    def __init__(
        self, width: int, multi: int, *,
        latency: float, throughput: float,
        policy: ArbitrationPolicy = TimeOrderArbitrationPolicy(select_min=False)
    ) -> None:
        """Creates a multiplex channel.

        Args:
            width: The data word width in bits.
            multi: The multiplexity.
            latency: The latency in seconds.
            throughput: The throughput in words per second.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._latency: float = latency
        """The latency in seconds."""
        self._throughput: float = throughput
        """The throughput in words per second."""
        self._channel: Channel = Channel(width + multi, latency=latency, throughput=throughput * ((width + multi) / width))
        """The channel."""
        self._arbitrator: Arbitrator = Arbitrator(width, multi, policy=policy)
        """The arbitrator."""
        self._combiner: DataCombiner = DataCombiner([width, multi])
        """The data word combiner."""
        self._splitter: DataSplitter = DataSplitter([width, multi])
        """The data word splitter."""
        self._demultiplexer: DataRetainingDemultiplexer = DataRetainingDemultiplexer(width, multi)
        """The data retaining demultiplexer."""
        self._group: Group = Group([self._arbitrator, self._combiner, self._channel, self._splitter, self._demultiplexer])
        """The grouped devices."""
        self._arbitrator.port_o.connect(self._combiner.ports_i[0])
        self._arbitrator.port_s.connect(self._combiner.ports_i[1])
        self._combiner.port_o.connect(self._channel.port_i)
        self._channel.port_o.connect(self._splitter.port_i)
        self._splitter.ports_o[0].connect(self._demultiplexer.port_i)
        self._splitter.ports_o[1].connect(self._demultiplexer.port_s)

    @property
    def width(self) -> int:
        """The data word width in bits."""
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
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports."""
        return self._arbitrator.ports_i

    @property
    def ports_o(self) -> tuple[OutputPort, ...]:
        """The output ports."""
        return self._demultiplexer.ports_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._group.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        return self._group.work(time)
