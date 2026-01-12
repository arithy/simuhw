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


class Group(Device):
    """A device made by grouping multiple devices."""

    def __init__(self, devices: Iterable[Device]) -> None:
        """Creates a device made by grouping multiple devices.

        Args:
            devices: The devices to be grouped.

        """
        super().__init__()
        self._devices: tuple[Device, ...] = tuple(iter(devices))
        """The grouped devices."""
        self._changes: list[tuple[list[InputPort], float | None]] = [([], None) for _ in self._devices]
        """The changes watched for the respective grouped devices."""

    @property
    def devices(self) -> tuple[Device, ...]:
        """The grouped devices."""
        return self._devices

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        for d in self._devices:
            d.reset()

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        if time is None:
            for i, d in enumerate(self._devices):
                self._changes[i] = d.work(time)
        else:
            for i, d in enumerate(self._devices):
                c: tuple[list[InputPort], float | None] = self._changes[i]
                if (c[1] is not None and c[1] <= time) or any((p.changed for p in c[0])):
                    self._changes[i] = d.work(time)
        self._update_time_and_check_inputs(time)
        return (
            [p for c in self._changes for p in c[0]],
            self._time if any(
                (p.changed for c in self._changes for p in c[0])
            ) else None if all(
                (c[1] is None for c in self._changes)
            ) else max(self._time, min((c[1] for c in self._changes if c[1] is not None)))
        )
