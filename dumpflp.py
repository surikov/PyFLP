import sys
import importlib.util
import datetime

import pyflp

debugLimit = 0


def json_string(txt: any):
    if txt is None:
        return ""
    else:
        rr = str(txt)
        rr = rr.replace("'", '"')
        rr = rr.replace("\n", " ")
        rr = rr.replace("\r", " ")
        rr = rr.replace("\\", "/")
        # rr=rr.replace("2", "8")
        return '"' + rr + '"'


def json_bool(bb: bool):
    if bb is None:
        return "false"
    else:
        if bb:
            return "true"
        else:
            return "false"


def json_num(nn):
    if nn is None:
        return "0"
    else:
        return str(nn)


def json_date(dd: datetime):
    if dd is None:
        return '""'
    else:
        return '"' + dd.strftime("%Y.%d.%m %H:%M:%S") + '"'


def dump_timemarker(delimiter: str, timemarker: pyflp.arrangement.TimeMarker):
    print("							" + delimiter + "{")
    print("								denominator: " + json_num(timemarker.denominator))
    print("								, name: " + json_string(timemarker.name))
    print("								, numerator: " + json_num(timemarker.numerator))
    print("								, position: " + json_num(timemarker.position))
    print("								, type: " + json_string(timemarker.type))
    print("							}")


def dump_track_item(delimiter: str, item: pyflp.arrangement.PLItemBase):
    print("									" + delimiter + "{")
    print("										data: " + json_string(item))
    print("									}")


def dump_track(delimiter: str, track: pyflp.arrangement.Track):
    print("							" + delimiter + "{")
    print("								name: " + json_string(track.name))
    print("								, enabled: " + json_bool(track.enabled))
    print("								, grouped: " + json_bool(track.grouped))
    print("								, items: [")
    delimiter = ""
    counter = 0
    for item in track:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("							...")
            break
        dump_track_item(delimiter, item)
        delimiter = delimiter = ", "
    print("								]")
    print("							}")


def dump_arrangement(delimiter: str, arrangement: pyflp.arrangement):
    print("					" + delimiter + "{")
    print("					name: " + json_string(arrangement.name))
    print("					, timemarkers: [")
    delimiter2 = ""
    counter = 0
    for timemarker in arrangement.timemarkers:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("							...")
            break
        dump_timemarker(delimiter2, timemarker)
        delimiter2 = ", "
    print("						]")
    print("					, tracks: [")
    delimiter2 = ""
    counter = 0
    for track in arrangement.tracks:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("					...")
            break
        if len(track) > 0:
            dump_track(delimiter2, track)
            delimiter2 = ", "
    print("						]")
    print("					}")


def dump_arrangements(project: pyflp.Project):
    print("		, arrangements: {")
    print("			loop_pos: " + json_num(project.arrangements.loop_pos))
    print(
        "			, time_signature_beat: "
        + json_num(project.arrangements.time_signature.beat)
    )
    print(
        "			, time_signature_num: " + json_num(project.arrangements.time_signature.num)
    )
    print("			, max_tracks: " + json_num(project.arrangements.max_tracks))
    print("			, arrangements_len: " + json_string(str(len(project.arrangements))))
    print("			, arrangements_items: [")
    delimiter = ""
    counter = 0
    for arrangement in project.arrangements:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("					...")
            break
        dump_arrangement(delimiter, arrangement)
        delimiter = ", "
    print("				]")
    print("			}")


def dump_automation(delimiter: str, automation: pyflp.channel.Automation):
    print("					" + delimiter + "{name: " + json_string(automation) + "}")


def dump_channel(delimiter: str, channel: pyflp.channel):
    print("					" + delimiter + "{name: " + json_string(channel.name) + "}")


def dump_channel_rack(project: pyflp.Project):
    print("		, channel_rack: {")

    print("			automations: [")
    delimiter = ""
    counter = 0
    for automation in project.channels.automations:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("					...")
            break
        dump_automation(delimiter, automation)
        delimiter = ", "
    print("				]")
    print("			, fit_to_steps: " + json_num(project.channels.fit_to_steps))
    print("			, height: " + json_num(project.channels.height))
    print("			, channels: [")
    delimiter = ""
    counter = 0
    for channel in project.channels:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("					...")
            break
        dump_channel(delimiter, channel)
        delimiter = ", "
    print("				]")
    print("			}")


def dump_insert(delimiter: str, insert: pyflp.mixer.Insert):
    print("					" + delimiter + "{insert: " + json_string(insert) + "}")


def dump_mixer(project: pyflp.Project):
    print("		, mixer: {")
    print("			apdc: " + json_bool(project.mixer.apdc))
    print("			, max_inserts: " + json_num(project.mixer.max_inserts))
    print("			, max_slots: " + json_num(project.mixer.max_slots))
    print("			, inserts: [")
    delimiter = ""
    counter = 0
    for insert in project.mixer:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("					...")
            break
        if insert.name is not None:
            dump_insert(delimiter, insert)
            delimiter = ", "
    print("				]")
    print("			}")


def dump_controller(delimiter: str, controller: pyflp.pattern.Controller):
    print(
        "						"
        + delimiter
        + "{channel: "
        + json_num(controller.channel)
        + ", position: "
        + json_num(controller.position)
        + ", value: "
        + json_num(controller.value)
        + "}"
    )


def dump_pattern(delimiter: str, pattern: pyflp.pattern.Pattern):
    print("					" + delimiter + "{name: " + json_string(pattern.name))
    print("						, color: " + json_string(pattern.color))
    print("						, length: " + json_num(pattern.length))
    print("						, looped: " + json_bool(pattern.looped))
    print("						, controllers: [")
    delimiter2 = ""
    counter = 0
    for controller in pattern.controllers:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("						...")
            break
        dump_controller(delimiter2, controller)
        delimiter2 = ", "
    print("							]")
    print("						}")


def dump_patterns(project: pyflp.Project):
    print("		, patterns: {")
    print("			play_cut_notes: " + json_bool(project.patterns.play_cut_notes))
    print("			, patterns: [")
    delimiter = ""
    counter = 0
    for pattern in project.patterns:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("					...")
            break
        dump_pattern(delimiter, pattern)
        delimiter = ", "
    print("				]")
    print("			}")


def dump_flp(project: pyflp.Project):
    print("	, flp: {")
    print("		version: " + json_string(str(project.version)))
    dump_arrangements(project)
    print("		, artists: " + json_string(project.artists))
    dump_channel_rack(project)
    print("		, comments: " + json_string(project.comments))
    print("		, created_on: " + json_date(project.created_on))
    print("		, data_path: " + json_string(project.data_path))
    print("		, format: " + json_num(project.format.value))
    print("		, genre: " + json_string(project.genre))
    print("		, licensed: " + json_bool(project.licensed))
    print("		, licensee: " + json_string(project.licensee))
    print("		, looped: " + json_bool(project.looped))
    print("		, main_pitch: " + json_num(project.main_pitch))
    print("		, main_volume: " + json_num(project.main_volume))
    dump_mixer(project)
    print("		, pan_law: " + json_num(project.pan_law))
    dump_patterns(project)
    print("		, ppq: " + json_num(project.ppq))
    print("		, show_info: " + json_bool(project.show_info))
    print("		, tempo: " + json_num(project.tempo))
    print("		, time_spent: " + json_num(project.time_spent.seconds))
    print("		, title: " + json_string(project.title))
    print("		, url: " + json_string(project.url))
    print("	}")


def dump(filepath: str):
    project = pyflp.parse(filepath)
    print("{")
    print("	dump: " + json_string("v1.01.0a6"))
    print("	, filepath: " + json_string(filepath))
    print("	, pyflp: " + json_string(pyflp.__version__))
    dump_flp(project)
    print("}")


filepath = sys.argv[1]
dump(filepath)
