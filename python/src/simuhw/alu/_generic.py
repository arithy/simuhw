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

from collections.abc import Iterable
import math

from .._base import InputPort, OutputPort, Device, Source, Drain
from .._branch import Distributor, Multiplexer, WordRetainingDemultiplexer, WordCombiner, WordSplitter
from .._group import Group
from .._operator import Operator, SIMD_Operator
from .._adder import HalfAdder, FullAdder
from .._subtractor import HalfSubtractor, FullSubtractor
from .._multiplier import Multiplier, SIMD_Multiplier
from .._divider import Divider, SIMD_Divider
from .._remainder import Remainder, SIMD_Remainder
from .. import fp


def _connect_ports(devs: list[Device], port_o: OutputPort | None, port_i: InputPort | None) -> None:
    if port_o is not None and port_i is not None:
        wo: int = port_o.width
        wi: int = port_i.width
        if wo < wi:
            ds: Source = Source(wi - wo, [((0).to_bytes((wi - wo + 7) >> 3), 0.0)])
            co: WordCombiner = WordCombiner([wi - wo, wo])
            ds.port_o.connect(co.ports_i[0])
            port_o.connect(co.ports_i[1])
            co.port_o.connect(port_i)
            devs.append(ds)
            devs.append(co)
        elif wo > wi:
            dd: Drain = Drain(wo - wi)
            sp: WordSplitter = WordSplitter([wo - wi, wi])
            port_o.connect(sp.port_i)
            sp.ports_o[0].connect(dd.port_i)
            sp.ports_o[1].connect(port_i)
            devs.append(dd)
            devs.append(sp)
        else:
            port_o.connect(port_i)
    elif port_o is not None:
        wo: int = port_o.width  # type: ignore[no-redef]
        dd: Drain = Drain(wo)  # type: ignore[no-redef]
        port_o.connect(dd.port_i)
        devs.append(dd)
    elif port_i is not None:
        wi: int = port_i.width  # type: ignore[no-redef]
        ds: Source = Source(wi, [((0).to_bytes((wi + 7) >> 3), 0.0)])  # type: ignore[no-redef]
        ds.port_o.connect(port_i)
        devs.append(ds)


class GenericArithmeticLogicUnit(Device):
    """A generic arithmetic logic unit.

    This device can integrate any operator devices.

    """

    def __init__(self, ops: Iterable[Operator]) -> None:
        """Creates a generic arithmetic logic unit.

        Args:
            ops: The operator devices to be integrated.

        """
        super().__init__()
        self._ops: tuple[Operator, ...] = tuple(ops)  # immutable to be used for a getter property
        """The operator devices."""
        self._n_ports_i: int = max((len(op.ports_i) for op in self._ops))
        """The number of the input ports."""
        self._width_i: int = max((op.width_i for op in self._ops))
        """The bit width of the input ports."""
        self._width_o: int = max((op.width_o for op in self._ops))
        """The bit width of the output port."""
        self._width_op: int = math.ceil(math.log2(len(self._ops)))
        """The bit width of the operator device selection port."""
        self._width_s: int = max((*(d.port_s.width for d in self._ops if isinstance(d, SIMD_Operator)), 0))
        """The bit width of the SIMD word width selection port."""
        self._width_ft: int = 0
        """The bit width of the input port to set tininess detection mode.

        The value is 0 unless `simuhw.fp` submodule is available.

        """
        self._width_fr: int = 0
        """The bit width of the input port to set rounding mode.

        The value is 0 unless `simuhw.fp` submodule is available.

        """
        self._width_fe: int = 0
        """The bit width of the input and output ports to set and get floating-point exception flags.

        The value is 0 unless `simuhw.fp` submodule is available.

        """
        if fp.is_available():
            self._width_ft = fp.FPState.width_ft
            self._width_fr = fp.FPState.width_fr
            self._width_fe = fp.FPState.width_fe
        n_op: int = len(self._ops)
        n_pi: int = self._n_ports_i + 5  # *ports_i, port_s, port_ci, port_ft, port_fr, port_fe_i
        n_po: int = 4  # port_o, port_co, port_e, port_fe_o
        distributor: Distributor = Distributor(self._width_op, n_pi + n_po)
        demultiplexer: list[WordRetainingDemultiplexer] = [
            WordRetainingDemultiplexer(w, n_op) for w in [
                *(self._width_i for _ in range(self._n_ports_i)),
                self._width_s, 1, self._width_ft, self._width_fr, self._width_fe
            ]
        ]
        multiplexer: list[Multiplexer] = [
            Multiplexer(w, n_op) for w in [
                self._width_o, 1, 1, self._width_fe
            ]
        ]
        self._devs: list[Device] = [distributor, *demultiplexer, *multiplexer]
        """The additional devices to arbitrate the multiple operator devices."""
        self._ports_i: tuple[InputPort, ...] = tuple(d.port_i for d in demultiplexer[:self._n_ports_i])
        """The input ports."""
        self._port_o: OutputPort = multiplexer[0].port_o
        """The output port."""
        self._port_op: InputPort = distributor.port_i
        """The operator device selection port."""
        self._port_s: InputPort = demultiplexer[self._n_ports_i].port_i
        """The SIMD word width selection port."""
        self._port_ci: InputPort = demultiplexer[self._n_ports_i + 1].port_i
        """The carry input port."""
        self._port_co: OutputPort = multiplexer[1].port_o
        """The carry output port."""
        self._port_e: OutputPort = multiplexer[2].port_o
        """The output port to emit overflow exception."""
        self._port_ft: InputPort = demultiplexer[self._n_ports_i + 2].port_i
        """The input port to set the tininess detection mode."""
        self._port_fr: InputPort = demultiplexer[self._n_ports_i + 3].port_i
        """The input port to set the rounding mode."""
        self._port_fe_i: InputPort = demultiplexer[self._n_ports_i + 4].port_i
        """The input port to set the floating-point exception flags."""
        self._port_fe_o: OutputPort = multiplexer[3].port_o
        """The output port to get the floating-point exception flags."""
        for i in range(n_pi):
            distributor.ports_o[i].connect(demultiplexer[i].port_s)
        for i in range(n_po):
            distributor.ports_o[n_pi + i].connect(multiplexer[i].port_s)
        for iop, op in enumerate(self._ops):
            assert op.width_i <= self._width_i
            for id, d in enumerate(demultiplexer[:self._n_ports_i]):
                assert d.ports_o[iop].width == self._width_i
                assert id >= len(op.ports_i) or op.ports_i[id].width == op.width_i
                _connect_ports(self._devs, d.ports_o[iop], op.ports_i[id] if id < len(op.ports_i) else None)
            _connect_ports(self._devs, demultiplexer[self._n_ports_i].ports_o[iop], op.port_s if isinstance(op, SIMD_Operator) else None)
            _connect_ports(self._devs, demultiplexer[self._n_ports_i + 1].ports_o[iop], op.port_ci if isinstance(op, (FullAdder, FullSubtractor)) else None)
            _connect_ports(self._devs, op.port_o, multiplexer[0].ports_i[iop])
            _connect_ports(self._devs, op.port_co if isinstance(op, (HalfAdder, HalfSubtractor)) else None, multiplexer[1].ports_i[iop])
            _connect_ports(self._devs, op.port_e if isinstance(op, (Multiplier, Divider, Remainder, SIMD_Multiplier, SIMD_Divider, SIMD_Remainder)) else None, multiplexer[2].ports_i[iop])
            if fp.is_available():
                _connect_ports(self._devs, demultiplexer[self._n_ports_i + 2].ports_o[iop], op.port_ft if isinstance(op, fp.FPState) else None)
                _connect_ports(self._devs, demultiplexer[self._n_ports_i + 3].ports_o[iop], op.port_fr if isinstance(op, fp.FPState) else None)
                _connect_ports(self._devs, demultiplexer[self._n_ports_i + 4].ports_o[iop], op.port_fe_i if isinstance(op, fp.FPState) else None)
                _connect_ports(self._devs, op.port_fe_o if isinstance(op, fp.FPState) else None, multiplexer[3].ports_i[iop])
            else:
                _connect_ports(self._devs, demultiplexer[self._n_ports_i + 2].ports_o[iop], None)
                _connect_ports(self._devs, demultiplexer[self._n_ports_i + 3].ports_o[iop], None)
                _connect_ports(self._devs, demultiplexer[self._n_ports_i + 4].ports_o[iop], None)
                _connect_ports(self._devs, None, multiplexer[3].ports_i[iop])
        self._group: Group = Group([*self._ops, *self._devs])
        """The device grouping all involved devices."""

    @property
    def ops(self) -> tuple[Operator, ...]:
        """The integrated operator devices."""
        return self._ops

    @property
    def width_i(self) -> int:
        """The bit width of the input ports."""
        return self._width_i

    @property
    def width_o(self) -> int:
        """The bit width of the output port."""
        return self._width_o

    @property
    def width_op(self) -> int:
        """The bit width of the operator device selection port."""
        return self._width_op

    @property
    def width_s(self) -> int:
        """The bit width of the SIMD word width selection port."""
        return self._width_s

    @property
    def width_ft(self) -> int:
        """The bit width of the input port to set tininess detection mode.

        The value is 0 unless `simuhw.fp` submodule is available.

        """
        return self._width_ft

    @property
    def width_fr(self) -> int:
        """The bit width of the input port to set rounding mode.

        The value is 0 unless `simuhw.fp` submodule is available.

        """
        return self._width_fr

    @property
    def width_fe(self) -> int:
        """The bit width of the input and output ports to set and get floating-point exception flags.

        The value is 0 unless `simuhw.fp` submodule is available.

        """
        return self._width_fe

    @property
    def ports_i(self) -> tuple[InputPort, ...]:
        """The input ports."""
        return self._ports_i

    @property
    def port_o(self) -> OutputPort:
        """The output port."""
        return self._port_o

    @property
    def port_op(self) -> InputPort:
        """The operator device selection port."""
        return self._port_op

    @property
    def port_s(self) -> InputPort:
        """The SIMD word width selection port."""
        return self._port_s

    @property
    def port_ci(self) -> InputPort:
        """The carry input port.

        The width is 1 bit.

        """
        return self._port_ci

    @property
    def port_co(self) -> OutputPort:
        """The carry output port.

        The width is 1 bit.

        """
        return self._port_co

    @property
    def port_e(self) -> OutputPort:
        """The output port to emit overflow exception of integer multiplication and division.

        The width is 1 bit.

        """
        return self._port_e

    @property
    def port_ft(self) -> InputPort:
        """The input port to set the tininess detection mode."""
        return self._port_ft

    @property
    def port_fr(self) -> InputPort:
        """The input port to set the rounding mode."""
        return self._port_fr

    @property
    def port_fe_i(self) -> InputPort:
        """The input port to set the floating-point exception flags."""
        return self._port_fe_i

    @property
    def port_fe_o(self) -> OutputPort:
        """The output port to get the floating-point exception flags."""
        return self._port_fe_o

    def reset(self) -> None:
        """Resets the states."""
        super().reset()
        self._group.reset()

    def find_op_indices(self, cond: tuple[type[Operator], int, int]) -> list[int]:
        """Returns the indices of the integrated operator devices that match the specified condition.

        Each index can be used to create a word for the operator device selection port (``port_op``).

        Args:
            cond: The condition to be matched with the integrated operator devices.
                  The first tuple element is the type of the operator device,
                  the second tuple element is the bit width of the input port or ports, and
                  the third tuple element is the bit width of the output port.

        Returns:
            The indices of the integrated operator devices that match the specified condition.

        """
        return [
            iop
            for iop, op in enumerate(self._ops)
            if type(op) is cond[0] and op.width_i == cond[1] and op.width_o == cond[2]
        ]

    def work(self, time: float | None) -> tuple[list[InputPort], float | None]:
        """Makes the device work.

        Args:
            time: The current time in seconds. ``None`` when starting to make the device work.

        Returns:
            A tuple of the list of the input ports that are to be watched receive a signal, and the next resuming time in seconds.
            The next resuming time can be ``None`` if resumable anytime.

        """
        return self._group.work(time)
