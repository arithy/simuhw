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

from ._base import InputPort, Device
from ._group import Group


class Simulator:
    """A simulator.

    It executes behavioral simulation of devices.

    """

    def __init__(self, devices: Iterable[Device]) -> None:
        """Creates a simulator.

        Args:
            devices: The devices.

        """
        self._group: Group = Group(devices)
        """The grouped devices."""
        self._time: float = 0.0
        """The current time in the simulation."""

    @property
    def devices(self) -> tuple[Device, ...]:
        """The devices."""
        return self._group.devices

    @property
    def time(self) -> float:
        """The current time in the simulation."""
        return self._time

    def start(
        self, *,
        duration: float | None = None, max_iter: int | None = None, show_time: bool = False
    ) -> None:
        """Starts the simulation.

        Args:
            duration: The duration time. No limit in duration if ``None``.
            max_iter: The maximum iteration count during the same current time. No limit in iteration if ``None``.

        """
        self._time = 0.0
        self._group.reset()
        self.resume(duration=duration, max_iter=max_iter, show_time=show_time, first=True)

    def resume(
        self, *,
        duration: float | None = None, max_iter: int | None = None, show_time: bool = False, first: bool = False
    ) -> None:
        """Resumes the simulation.

        Args:
            duration: The duration time. No limit in duration if ``None``.
            max_iter: The maximum iteration count during the same current time. No limit in iteration if ``None``.

        """
        c: tuple[list[InputPort], float | None] = ([], None if first else self._time)
        t0: float = self._time
        iter: int = 0
        while (duration is None or self._time < t0 + duration) and (max_iter is None or iter < max_iter):
            if show_time:
                print(f'iteration: {iter}, time: {self._time}')
            c = self._group.work(c[1])
            if c[1] is None:
                break
            self._time = c[1]
            iter += 1
