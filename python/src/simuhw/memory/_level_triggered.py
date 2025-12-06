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

from .._base import InputPort
from ._base import Memory
from .model._base import MemorizingModel
from .model._real import RealMemorizingModel


class LevelTriggeredMemory(Memory):
    """A level-triggered memory device."""

    def __init__(
        self, width: int, width_a: int, *,
        model: MemorizingModel = RealMemorizingModel(),
        neg_leveled: bool = False
    ) -> None:
        """Creates a level-triggered memory device.

        Args:
            width: The data word width in bits.
            width_a: The address word width in bits.
            model: The memorizing model.
            neg_leveled: `True` if negative-leveled, `False` otherwise.

        """
        super().__init__(width, width_a, model)
        self._neg_leveled: bool = neg_leveled
        """`True` if negative-leveled, `False` otherwise."""
        self._port_g: InputPort = InputPort(1)
        """The gate port."""

    @property
    def negative_leveled(self) -> bool:
        """`True` if negative-leveled, `False` otherwise."""
        return self._neg_leveled

    @property
    def port_g(self) -> InputPort:
        """The gate port."""
        return self._port_g

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_g.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. `None` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be `None` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_g, self._port_a, self._port_i]
        addr: bytes | None = self._port_a.data[0]
        gate: bytes | None = self._port_g.data[0]
        if time is None:
            if gate is None or addr is None:
                self._initialize_probes()
            elif int.from_bytes(gate) != 0:
                self._initialize_probes(addr)
            else:
                self._initialize_probes()
        if self._update_time_and_check_inputs(time, ports_i):
            if gate is None or addr is None:
                self._port_o.post((None, self._time))
            elif int.from_bytes(gate) == (0 if self._neg_leveled else 1):
                self._model.write(addr, self._port_i.data[0])
                d: tuple[bytes | None, float] = (self._model.read(addr), self._time)
                self._port_o.post(d)
                self._update_probes(addr, d)
            else:
                self._port_o.post((self._model.read(addr), self._time))
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
