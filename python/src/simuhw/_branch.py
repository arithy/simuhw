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

from collections.abc import Iterable
from functools import reduce

from ._base import InputPort, OutputPort, Device, combine_bits, extract_bits
from .arbitrate.policy import ArbitrationPolicy, IndexOrderArbitrationPolicy, TimeOrderArbitrationPolicy


class DataCombiner(Device):
    """A data word combiner."""

    def __init__(self, widths: Iterable[int]) -> None:
        """Creates a data word combiner.

        Args:
            widths: The input data word widths in bits.

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
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            self._port_o.post((
                None if any((p.data[0] is None for p in self._ports_i)) else reduce(
                    lambda x, y: (x[0] + y[0], combine_bits(x[0], x[1], y[0], y[1])),  # type: ignore
                    ((p.width, p.data[0]) for p in self._ports_i), (0, b'')
                )[1],
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class DataSplitter(Device):
    """A data word splitter."""

    def __init__(self, widths: Iterable[int]) -> None:
        """Creates a data word splitter.

        Args:
            widths: The output data word widths in bits.

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
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i]
        if self._update_time_and_check_inputs(time, ports_i):
            b: bytes | None = self._port_i.data[0]
            if b is None:
                for p in self._ports_o:
                    p.post((None, self._time))
            else:
                s: int = self._port_i.width
                for p in self._ports_o:
                    s -= p.width
                    p.post((extract_bits(self._port_i.width, b, s, p.width), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class Arbitrator(Device):
    """An arbitrator."""

    def __init__(
        self, width: int, ninputs: int, *,
        policy: ArbitrationPolicy = TimeOrderArbitrationPolicy(when_same=IndexOrderArbitrationPolicy())
    ) -> None:
        """Creates an arbitrator.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.
            policy: The arbitration policy.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._policy: ArbitrationPolicy = policy
        """The arbitration policy."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width) for _ in range(ninputs))
        """The input ports."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port for the data word from the selected input port."""
        self._port_s: OutputPort = OutputPort(ninputs)
        """The output port for the selection bit flags of the input ports."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def policy(self) -> ArbitrationPolicy:
        """The arbitration policy."""
        return self._policy

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports."""
        return self._ports_i

    @property
    def port_o(self) -> OutputPort:
        """The output port for the data word from the selected input port."""
        return self._port_o

    @property
    def port_s(self) -> OutputPort:
        """The output port for the selection bit flags of the input ports."""
        return self._port_s

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for p in self._ports_i:
            p.reset()
        self._port_o.reset()
        self._port_s.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        if self._update_time_and_check_inputs(time, self._ports_i):
            i: int = self._policy.select([p.data for p in self._ports_i])
            self._port_s.post(((1 << i).to_bytes(), self._time))
            self._port_o.post((
                self._ports_i[i].data[0],
                self._time
            ))
            self._set_inputs_unchanged(self._ports_i)
        return (list(self._ports_i), None)


class Multiplexer(Device):
    """A multiplexer."""

    def __init__(self, width: int, ninputs: int) -> None:
        """Creates a multiplexer.

        Args:
            width: The data word width in bits.
            ninputs: The number of the input ports.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._ports_i: tuple[InputPort, ...] = tuple(InputPort(width) for _ in range(ninputs))
        """The input ports for the data word."""
        self._port_s: InputPort = InputPort(ninputs)
        """The input port for the selection bit flags of the input ports for the data word."""
        self._port_o: OutputPort = OutputPort(width)
        """The output port."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports for the data word."""
        return self._ports_i

    @property
    def port_s(self) -> InputPort:
        """The input port for the selection bit flags of the input ports for the data word."""
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
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [*self._ports_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if self._port_s.data[0] is None:
                self._port_o.post((None, self._time))
            else:
                i: int = int.from_bytes(self._port_s.data[0]).bit_length() - 1
                self._port_o.post((
                    self._ports_i[i].data[0] if i >= 0 else None,
                    self._time
                ))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class Demultiplexer(Device):
    """A demultiplexer."""

    def __init__(self, width: int, noutputs: int, *, deselected: bytes | None = None) -> None:
        """Creates a demultiplexer.

        Args:
            width: The data word width in bits.
            noutputs: The number of the output ports.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._deselected: bytes | None = deselected
        """The data word when not selected."""
        self._port_i: InputPort = InputPort(width)
        """The input port for the data word."""
        self._port_s: InputPort = InputPort(noutputs)
        """The input port for the selection bit flags of the output ports."""
        self._ports_o: tuple[OutputPort, ...] = tuple(OutputPort(width) for _ in range(noutputs))
        """The output ports."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def port_i(self) -> InputPort:
        """The input port for the data word."""
        return self._port_i

    @property
    def port_s(self) -> InputPort:
        """The input port for the selection bit flags of the output ports."""
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
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if self._port_s.data[0] is not None:
                s: int = int.from_bytes(self._port_s.data[0])
                for i, p in enumerate(self._ports_o):
                    if ((s >> i) & 1) == 1:
                        p.post((self._port_i.data[0], self._time))
                    else:
                        p.post((self._deselected, self._time))
            else:
                for i, p in enumerate(self._ports_o):
                    p.post((None, self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class DataRetainingDemultiplexer(Demultiplexer):
    """A demultiplexer to retain data in the unselected ports."""

    def __init__(self, width: int, noutputs: int) -> None:
        """Creates a demultiplexer to retain data in the unselected ports.

        Args:
            width: The data word width in bits.
            noutputs: The number of the output ports.

        """
        super().__init__(width, noutputs)

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i, self._port_s]
        if self._update_time_and_check_inputs(time, ports_i):
            if self._port_s.data[0] is not None:
                s: int = int.from_bytes(self._port_s.data[0])
                for i, p in enumerate(self._ports_o):
                    if ((s >> i) & 1) == 1:
                        p.post((self._port_i.data[0], self._time))
            else:
                for i, p in enumerate(self._ports_o):
                    p.post((None, self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)


class Distributor(Device):
    """A distributor."""

    def __init__(self, width: int, noutputs: int) -> None:
        """Creates a distributor.

        Args:
            width: The data word width in bits.
            noutputs: The number of the output ports.

        """
        super().__init__()
        self._width: int = width
        """The data word width in bits."""
        self._port_i: InputPort = InputPort(width)
        """The input port for the data word."""
        self._ports_o: tuple[OutputPort, ...] = tuple(OutputPort(width) for _ in range(noutputs))
        """The output ports."""

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def port_i(self) -> InputPort:
        """The input port for the data word."""
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
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_i]
        if self._update_time_and_check_inputs(time, ports_i):
            for p in self._ports_o:
                p.post((self._port_i.data[0], self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
