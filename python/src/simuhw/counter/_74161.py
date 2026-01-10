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

from .._word import DataWord, Unknown
from .._base import InputPort
from ._base import SynchronousBinaryCounter


class SynchronousBinaryCounter74161(SynchronousBinaryCounter):
    """A synchronous binary counter 74161 with arbitrary bits.

    This device behaves like the logic IC 74161 with no timing delay and with arbitrary counter bits.

    **Truth Table:**

    .. code-block:: text

        +-----------------------------------+-----------+-----------------------+
        |           Inputs                  |  Outputs  |                       |
        +-----+-----+-----+-----+-----+-----+-----+-----+       Function        |
        | clr |load |  d  | enp | ent | ck  |  q  | co  |                       |
        +-----+-----+-----+-----+-----+-----+-----+-----+-----------------------+
        |  L  |  X  |  X  |  X  |  X  |  X  |  L  |  L  | Resets count to 0.    |
        |  H  |  L  | H/L |  X  |  X  | Rise| H/L |  L  | Presets count with d. |
        |  H  |  H  |  X  |  X  |  L  | Rise| H/L | H/L | No change.            |
        |  H  |  H  |  X  |  L  |  X  | Rise| H/L | H/L | No change.            |
        |  H  |  H  |  X  |  H  |  H  | Rise| H/L | H/L | Counts up.            |
        |  H  |  X  |  X  |  X  |  X  | Fall| H/L | H/L | No change.            |
        +-----+-----+-----+-----+-----+-----+-----+-----+-----------------------+

    """

    def __init__(self, width: int) -> None:
        """Creates a synchronous binary counter 74161 with arbitrary bits.

        Args:
            width: The data word width in bits.

        """
        super().__init__(width, neg_edged=False)
        self._port_clr: InputPort = InputPort(1)
        """The clear port.

        Active if the data word is 0."""
        self._port_load: InputPort = InputPort(1)
        """The load enable port.

        Active if the data word is 0."""
        self._port_enp: InputPort = InputPort(1)
        """The count enable port.

        Active if the data word is 1."""
        self._port_ent: InputPort = InputPort(1)
        """The carry input port."""

    @property
    def port_clr(self) -> InputPort:
        """The clear port.

        Active if the data word is 0."""
        return self._port_clr

    @property
    def port_load(self) -> InputPort:
        """The load enable port.

        Active if the data word is 0."""
        return self._port_load

    @property
    def port_enp(self) -> InputPort:
        """The count enable port.

        Active if the data word is 1."""
        return self._port_enp

    @property
    def port_ent(self) -> InputPort:
        """The carry input port."""
        return self._port_ent

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._port_clr.reset()
        self._port_load.reset()
        self._port_enp.reset()
        self._port_ent.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a data word, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        ports_i: list[InputPort] = [self._port_ck, self._port_clr, self._port_load, self._port_enp, self._port_ent, self._port_d]
        ck: DataWord = self._port_ck.data[0]
        if self._update_time_and_check_inputs(time, ports_i):
            if not isinstance(self._port_clr.data[0], bytes):
                self._count = Unknown
                self._port_q.post((Unknown, self._time))
                self._port_co.post((Unknown, self._time))
            elif int.from_bytes(self._port_clr.data[0]) == 0:
                self._count = (0).to_bytes(self._nbytes)
                self._port_q.post((self._count, self._time))
                self._port_co.post(((0).to_bytes(1), self._time))
            elif not isinstance(ck, bytes) or not isinstance(self._prev_ck, bytes):
                self._count = Unknown
                self._port_q.post((Unknown, self._time))
                self._port_co.post((Unknown, self._time))
            elif int.from_bytes(ck) - int.from_bytes(self._prev_ck) == 1:
                if not isinstance(self._port_load.data[0], bytes):
                    self._count = Unknown
                    self._port_q.post((Unknown, self._time))
                    self._port_co.post((Unknown, self._time))
                elif int.from_bytes(self._port_load.data[0]) == 0:
                    self._count = self._port_d.data[0]
                    self._port_q.post((self._count, self._time))
                    self._port_co.post(((0).to_bytes(1), self._time))
                elif (
                    isinstance(self._port_enp.data[0], bytes) and
                    isinstance(self._port_ent.data[0], bytes) and
                    int.from_bytes(self._port_enp.data[0]) == 1 and
                    int.from_bytes(self._port_ent.data[0]) == 1 and
                    isinstance(self._count, bytes)
                ):
                    q: int = int.from_bytes(self._count)
                    co: int = 0
                    if q < self._mask:
                        q += 1
                    else:
                        q = 0
                        co = 1
                    self._count = q.to_bytes(self._nbytes)
                    self._port_q.post((self._count, self._time))
                    self._port_co.post((co.to_bytes(1), self._time))
            self._prev_ck = ck
            self._set_inputs_unchanged(ports_i)
        return (ports_i, None)
