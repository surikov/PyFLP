import enum
from typing import List, Optional

import colour

from pyflp._event import _DataEventType, _DWordEvent, _EventType, _TextEvent, _WordEvent
from pyflp._flobject import _MaxInstancedFLObject
from pyflp._properties import _ColorProperty, _IntProperty, _StrProperty, _UIntProperty
from pyflp._validators import _IntValidator, _UIntValidator
from pyflp.constants import DATA, DWORD, TEXT, WORD
from pyflp.insert.parameters import InsertFlags, InsertParameters
from pyflp.insert.slot import InsertSlot


class Insert(_MaxInstancedFLObject):
    # Parser will decide a value for max_count

    class EQ(_MaxInstancedFLObject):
        """Insert post EQ.

        [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/mixer_trackprops.htm)
        """

        _LEVEL_VALIDATOR = _IntValidator(-1800, 1800)
        _FREQ_Q_VALIDATOR = _UIntValidator(65536)

        low_level: int = _IntProperty(_LEVEL_VALIDATOR)
        """Gain of first band. Min: -1800, Max: 1800, Default: 0."""

        band_level: int = _IntProperty(_LEVEL_VALIDATOR)
        """Gain of second band. Min: -1800, Max: 1800, Default: 0."""

        high_level: int = _IntProperty(_LEVEL_VALIDATOR)
        """Gain of third band. Min: -1800, Max: 1800, Default: 0."""

        low_freq: int = _UIntProperty(_FREQ_Q_VALIDATOR)
        """Frequency of first band. Min: 0, Max: 65536, Default: 5777 (90 Hz)."""

        band_freq: int = _UIntProperty(_FREQ_Q_VALIDATOR)
        """Frequency of second band. Min: 0, Max: 65536, Default: 33145 (1500 Hz)."""

        high_freq: int = _UIntProperty(_FREQ_Q_VALIDATOR)
        """Frequency of third band. Min: 0, Max: 65536, Default: 55825 (8000 Hz)."""

        low_q: int = _UIntProperty(_FREQ_Q_VALIDATOR)
        """Resonance of first band. Min: 0, Max: 65536, Default: 17500."""

        band_q: int = _UIntProperty(_FREQ_Q_VALIDATOR)
        """Resonance of second band. Min: 0, Max: 65536, Default: 17500."""

        high_q: int = _UIntProperty(_FREQ_Q_VALIDATOR)
        """Resonance of thid band. Min: 0, Max: 65536, Default: 17500."""

    @enum.unique
    class EventID(enum.IntEnum):
        """Events used by `Insert`."""

        Parameters = DATA + 28
        """Stored in `Insert.locked` and `Insert.flags`."""

        Routing = DATA + 27
        """See `Insert.routing`."""

        Input = DWORD + 26
        """See `Insert.input`."""

        Output = DWORD + 19
        """See `Insert.output`."""

        Color = DWORD + 21
        """See `Insert.color`. Default event is not stored."""

        Icon = WORD + 31
        """See `Insert.icon`. Default event is not stored."""

        Name = TEXT + 12
        """See `Insert.name`. Default event doesn't exist."""

    # * Properties
    name: Optional[str] = _StrProperty()

    @property
    def routing(self) -> List[bool]:
        """An order collection of booleans, representing how `Insert` is routed. e.g.
        if it is [False, True, True, ...] then this insert is routed to insert 2, 3."""
        return getattr(self, "_routing", [])

    icon: Optional[int] = _IntProperty()

    input: Optional[int] = _IntProperty()
    """Hardware input, dk exactly."""

    output: Optional[int] = _IntProperty()
    """Hardware output, dk exactly."""

    color: Optional[colour.Color] = _ColorProperty()

    @property
    def flags(self) -> Optional[InsertFlags]:
        return self._parameters.flags

    @flags.setter
    def flags(self, value: InsertFlags):
        self._parameters.flags = value

    @property
    def slots(self) -> List[InsertSlot]:
        """Holds `InsertSlot` objects (empty and used, both)."""
        return getattr(self, "_slots", [])

    @property
    def enabled(self) -> Optional[bool]:
        """Whether `Insert` is in enabled state in the mixer."""
        flags = self._parameters.flags
        if flags:
            return InsertFlags.Enabled in flags

    @enabled.setter
    def enabled(self, value: bool):
        # https://stackoverflow.com/a/66667330
        if value:
            self._parameters.flags |= InsertFlags.Enabled
        else:
            self._parameters.flags &= ~InsertFlags.Enabled

    volume: Optional[int] = _UIntProperty(max_=16000)
    """Post volume fader. Min: 0 (0% / -INFdB / 0.00), Max: 16000 \
    (125% / 5.6dB / 1.90), Default: 12800 (100% / 0.0dB / 1.00)."""

    pan: Optional[int] = _IntProperty(min_=-6400, max_=6400)
    """Min: -6400 (100% left), Max: 6400 (100% right), Default: 0."""

    stereo_separation: Optional[int] = _IntProperty(min_=-64, max_=64)
    """Min: -64 (100% merged), Max: 64 (100% separated), Default: 0."""

    @property
    def eq(self) -> Optional[EQ]:
        """3-band post EQ. See `InsertEQ`."""
        return getattr(self, "_eq", None)

    @property
    def route_volumes(self) -> List[int]:
        """Ordered list of route volumes."""
        return getattr(self, "_route_volumes", [])

    @route_volumes.setter
    def route_volumes(self, value: List[int]):
        if len(value) != Insert.max_count:
            raise ValueError(f"Expected a list of size {Insert.max_count}")
        self._route_volumes = value

    @property
    def locked(self) -> Optional[bool]:
        """Whether `Insert` is in locked state in the mixer."""
        flags = self._parameters.flags
        if flags:
            return InsertFlags.Locked in flags

    @locked.setter
    def locked(self, value: bool):
        if value:
            self._parameters.flags |= InsertFlags.Locked
        else:
            self._parameters.flags &= ~InsertFlags.Locked

    # * Parsing logic
    def parse_event(self, e: _EventType) -> None:
        if e.id == InsertSlot.EventID.Index:
            self._cur_slot.parse_event(e)
            self._slots.append(self._cur_slot)
            if len(self._slots) < InsertSlot.max_count:
                self._cur_slot = InsertSlot()
        elif e.id in (
            InsertSlot.EventID.Color,
            InsertSlot.EventID.Icon,
            InsertSlot.EventID.PluginNew,
            InsertSlot.EventID.Plugin,
            InsertSlot.EventID.DefaultName,
            InsertSlot.EventID.Name,
        ):
            self._cur_slot.parse_event(e)
        else:
            return super().parse_event(e)

    def _parse_word_event(self, e: _WordEvent):
        if e.id == Insert.EventID.Icon:
            self._parse_H(e, "icon")

    def _parse_dword_event(self, e: _DWordEvent):
        if e.id == Insert.EventID.Input:
            self._parse_i(e, "input")
        elif e.id == Insert.EventID.Color:
            self._parse_color(e, "color")
        elif e.id == Insert.EventID.Output:
            self._parse_i(e, "output")

    def _parse_text_event(self, e: _TextEvent):
        if e.id == Insert.EventID.Name:
            self._parse_s(e, "name")

    def _parse_data_event(self, e: _DataEventType):
        if e.id == Insert.EventID.Parameters:
            self._events["parameters"] = e
            self._parameters = InsertParameters()
            self._parameters.parse_event(e)
        elif e.id == Insert.EventID.Routing:
            routing = []
            for byte in e.data:
                route = True if byte > 0 else False
                routing.append(route)
            self._parseprop(e, "routing", routing)

    def _save(self) -> List[_EventType]:
        events = list(super()._save())
        for slot in self.slots:
            events.extend(slot._save())
        return events

    def __init__(self):
        super().__init__()
        InsertSlot._count = Insert.EQ._count = 0
        self._slots: List[InsertSlot] = []
        self._cur_slot = InsertSlot()
        self._eq = Insert.EQ()
        self._route_volumes = [int()] * Insert.max_count
        self.index = Insert._count - 2
