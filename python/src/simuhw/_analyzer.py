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

from abc import ABCMeta, abstractmethod
from typing import IO
import heapq


class Probe(metaclass=ABCMeta):
    """The super class for all probes."""

    @classmethod
    @abstractmethod
    def typename(cls) -> str:
        """The probe type string."""
        pass

    def __init__(self, name: str, width: int) -> None:
        """Creates a probe.

        Args:
            name: The probe name.
            width: The data word width in bits.

        """
        self._name: str = name
        """The probe name."""
        self._width: int = width
        """The data word width in bits."""
        self._data: list[tuple[bytes | None, float]] = []
        """The list of the data words recorded."""

    @property
    def name(self) -> str:
        """The probe name."""
        return self._name

    @property
    def width(self) -> int:
        """The data word width in bits."""
        return self._width

    @property
    def data(self) -> list[tuple[bytes | None, float]]:
        """The list of the data words recorded."""
        return self._data

    def reset(self) -> None:
        """Resets the states."""
        self._data.clear()


class ChannelProbe(Probe):
    """A probe to record timings of channel data change."""

    @classmethod
    def typename(cls) -> str:
        """The probe type string."""
        return 'wire'

    def __init__(self, name: str, width: int) -> None:
        """Creates a channel probe.

        Args:
            name: The probe name.
            width: The data word width in bits.

        """
        super().__init__(name, width)


class MemoryProbe(Probe):
    """A probe to record timings of memory data change."""

    @classmethod
    def typename(cls) -> str:
        """The probe type string."""
        return 'reg'

    def __init__(self, name: str, width: int) -> None:
        """Creates a memory probe.

        Args:
            name: The probe name.
            width: The data word width in bits.

        """
        super().__init__(name, width)


class LogicAnalyzer:
    """A logic analyzer to save the collected timings of data change."""

    def __init__(self) -> None:
        """Creates a logic analyzer."""
        self._probe: list[Probe] = []
        """The probes."""

    def add_probe(self, probe: Probe) -> None:
        """Adds a probe.

        Args:
            probe: The probe to be added.

        """
        if probe not in self._probe:
            self._probe.append(probe)

    def remove_probe(self, probe: Probe) -> None:
        """Removes a probe.

        Args:
            probe: The probe to be removed.

        Raises:
            ValueError: If a probe not yet added is specified in `probe`.

        """
        if probe not in self._probe:
            raise ValueError('not added probe')
        self._probe.remove(probe)

    def remove_all_probes(self) -> None:
        """Removes all probes."""
        self._probe.clear()

    def save_as_vcd(self, file: IO[str]) -> None:
        """Collects the timings of data change at all probes, and saves them into a file in the VCD format.

        Args:
            file: The file in which the collected timings are saved.

        """
        file.write('$timescale 1ps $end\n')
        for i, p in enumerate(self._probe):
            file.write(f'$var {p.typename()} {p.width} {i} {p.name} $end\n')
        file.write('$dumpvars\n')
        for i, p in enumerate(self._probe):
            file.write(f'b{"x" * p.width} {i}\n')
        file.write('$end\n')
        q: list[tuple[int, tuple[int, int, bytes | None]]] = []
        for i, p in enumerate(self._probe):
            for d in p.data:
                heapq.heappush(q, (int(d[1] * 1e12), (i, p.width, d[0])))
        t: int | None = None
        for i in range(len(q)):
            e: tuple[int, tuple[int, int, bytes | None]] = heapq.heappop(q)
            if t is None or t != e[0]:
                t = e[0]
                file.write(f'#{t}\n')
            s: str = ''
            if e[1][2] is None:
                s += 'x' * e[1][1]
            else:
                for b in e[1][2]:
                    s += f'{b:08b}'
            file.write(f'b{s[-e[1][1]:]} {e[1][0]}\n')
        if t is not None:
            file.write(f'#{t + (t >> 2)}\n')
