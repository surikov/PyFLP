# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""
PyFLP - FL Studio project file parser
=====================================

Load a project file:

    >>> import pyflp
    >>> project = pyflp.parse("/path/to/parse.flp")

Save the project:

    >>> pyflp.save(project, "/path/to/save.flp")

Full docs are available at https://pyflp.rtfd.io.
"""  # noqa

from __future__ import annotations

import io
import os
import pathlib
import sys

import construct as c

from ._events import (
    DATA,
    DWORD,
    NEW_TEXT_IDS,
    TEXT,
    WORD,
    AnyEvent,
    AsciiEvent,
    EventEnum,
    EventTree,
    IndexedEvent,
    U8Event,
    U16Event,
    U32Event,
    UnicodeEvent,
    UnknownDataEvent,
)
from .exceptions import HeaderCorrupted, VersionNotDetected
from .plugin import PluginID, get_event_by_internal_name
from .project import VALID_PPQS, FileFormat, Project, ProjectID

__all__ = ["parse", "save"]
__version__ = "2.0.0a6"

if sys.version_info < (3, 11):  # https://github.com/Bobronium/fastenum/issues/2
    import fastenum

    fastenum.enable()  # 50% faster parse()


def parse(file: pathlib.Path | str) -> Project:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # pylint: disable=too-complex
    """Parses an FL Studio project file and returns a parsed :class:`Project`.

    Args:
        file: Path to the FLP.

    Raises:
        HeaderCorrupted: When an invalid value is found in the file header.
        VersionNotDetected: A correct string type couldn't be determined.
    """
    with open(file, "rb") as flp:
        stream = io.BytesIO(flp.read())

    events: list[AnyEvent] = []

    if stream.read(4) != b"FLhd":  # 4
        raise HeaderCorrupted("Unexpected header chunk magic; expected 'FLhd'")

    if c.Int32ul.parse_stream(stream) != 6:  # 8
        raise HeaderCorrupted("Unexpected header chunk size; expected 6")

    try:
        file_format = FileFormat(c.Int16sl.parse_stream(stream))  # 10
    except ValueError as exc:
        raise HeaderCorrupted("Unsupported project file format") from exc

    channel_count = c.Int16ul.parse_stream(stream)  # 12
    if channel_count is None:  # pragma: no cover
        raise HeaderCorrupted("Channel count couldn't be read")

    ppq = c.Int16ul.parse_stream(stream)  # 14
    if ppq not in VALID_PPQS:
        raise HeaderCorrupted("Invalid PPQ")

    if stream.read(4) != b"FLdt":  # 18
        raise HeaderCorrupted("Unexpected data chunk magic; expected 'FLdt'")

    events_size = c.Int32ul.parse_stream(stream)  # 22
    if events_size is None:  # pragma: no cover
        raise HeaderCorrupted("Data chunk size couldn't be read")

    stream.seek(0, os.SEEK_END)
    file_size = stream.tell()
    if file_size != events_size + 22:
        raise HeaderCorrupted("Data chunk size corrupted")

    plug_name = None
    str_type: type[AsciiEvent] | type[UnicodeEvent] | None = None
    stream.seek(22)  # Back to start of events
    while stream.tell() < file_size:
        event_type: type[AnyEvent] | None = None
        id = EventEnum(int.from_bytes(stream.read(1), "little"))

        if id < WORD:
            value = stream.read(1)
        elif id < DWORD:
            value = stream.read(2)
        elif id < TEXT:
            value = stream.read(4)
        else:
            size = c.VarInt.parse_stream(stream)
            value = stream.read(size)

        if id == ProjectID.FLVersion:
            parts = value.decode("ascii").rstrip("\0").split(".")
            if [int(part) for part in parts][0:2] >= [11, 5]:
                str_type = UnicodeEvent
            else:
                str_type = AsciiEvent

        for enum_ in EventEnum.__subclasses__():
            if id in enum_:
                event_type = getattr(enum_(id), "type")
                break

        if event_type is None:
            if id < WORD:
                event_type = U8Event
            elif id < DWORD:
                event_type = U16Event
            elif id < TEXT:
                event_type = U32Event
            elif id < DATA or id.value in NEW_TEXT_IDS:
                if str_type is None:  # pragma: no cover
                    raise VersionNotDetected  # ! This should never happen
                event_type = str_type

                if id == PluginID.InternalName:
                    plug_name = event_type(id, value).value
            elif id == PluginID.Data and plug_name is not None:
                event_type = get_event_by_internal_name(plug_name)
            else:
                event_type = UnknownDataEvent

        events.append(event_type(id, value))

    return Project(
        EventTree(init=(IndexedEvent(r, e) for r, e in enumerate(events))),
        channel_count=channel_count,
        format=file_format,
        ppq=ppq,
    )


def save(project: Project, file: pathlib.Path | str):
    """Save a parsed project back into a file.

    Caution:
        Always have a backup ready, just in case 😉

    Args:
        project: The object returned by :meth:`parse`.
        file: The file in which the contents of :attr:`project` are serialised back.
    """
    stream = io.BytesIO()
    stream.write(b"FLhd")  # 4
    c.Int32ul.build_stream(6, stream)  # 8
    c.Int16sl.build_stream(project.format, stream)  # 10
    c.Int16ul.build_stream(project.channel_count, stream)  # 12
    c.Int16ul.build_stream(project.ppq, stream)  # 14
    stream.write(b"FLdt")  # 18
    stream.seek(4, 1)  # leave space for total event size

    project.events.insert(0, project.events.pop(ProjectID.FLVersion))
    events_size = 0
    for event in project.events:
        events_size += event.size
        stream.write(bytes(event))

    stream.seek(18)
    c.Int32ul.build_stream(events_size, stream)

    with open(file, "wb") as flp:
        flp.write(stream.getvalue())
