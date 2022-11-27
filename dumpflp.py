import sys
import importlib.util
import datetime

import pyflp

debugLimit = 0


def float_to_str(f):
    float_string = repr(f)
    if "e" in float_string:  # detect scientific notation
        digits, exp = float_string.split("e")
        digits = digits.replace(".", "").replace("-", "")
        exp = int(exp)
        zero_padding = "0" * (
            abs(int(exp)) - 1
        )  # minus 1 for decimal point in the sci notation
        sign = "-" if f < 0 else ""
        if exp > 0:
            float_string = "{}{}{}.0".format(sign, digits, zero_padding)
        else:
            float_string = "{}0.{}{}".format(sign, zero_padding, digits)
    return float_string


def json_string(txt: any):
    if txt is None:
        return '""'
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
        return float_to_str(nn)


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


def dump_eq(eq: pyflp.mixer.Insert.eq):
    print(
        "						, eq: high: {freq: "
        + json_num(eq.high.freq)
        + ", gain: "
        + json_num(eq.high.gain)
        + ", reso: "
        + json_num(eq.high.reso)
        + "}"
    )
    print(
        "							,mid: {freq: "
        + json_num(eq.mid.freq)
        + ", gain: "
        + json_num(eq.mid.gain)
        + ", reso: "
        + json_num(eq.mid.reso)
        + "}"
    )
    print(
        "							,low: {freq: "
        + json_num(eq.low.freq)
        + ", gain: "
        + json_num(eq.low.gain)
        + ", reso: "
        + json_num(eq.low.reso)
        + "}"
    )
    print("							}")


def dump_routes(insert: pyflp.mixer.Insert):
    print("						, routes: [")
    delimiter = ""
    counter = 0
    for route in insert.routes:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("							...")
            break
        print("							" + delimiter + json_num(route))
        delimiter = ", "
    print("							]")


def dump_remoteControllers(slot: pyflp.mixer.Slot):
    controllers = None
    try:
        controllers = slot.controllers
    except KeyError:
        controllers = None
    print("								, controllers: [")
    if controllers is not None:
        delimiter = ""
        counter = 0
        for remoteController in controllers:
            counter = counter + 1
            if counter > debugLimit and debugLimit > 0:
                print("								...")
                break
            print("										" + delimiter + json_string(remoteController))
            delimiter = ", "
    print("									]")


def dump_slots(insert: pyflp.mixer.Insert):
    print("						, slots: [")
    delimiter = ""
    counter = 0
    for slot in insert:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("							...")
            break
        print("							" + delimiter + "{color: " + json_string(slot.color))
        # dump_remoteControllers(slot)
        print("								, icon: " + json_num(slot.icon))
        print("								, index: " + json_num(slot.index))
        print("								, internal_name: " + json_string(slot.internal_name))
        # print("								, mix: " + json_num(slot.mix))
        print("								, name: " + json_string(slot.name))
        print("								, plugin: " + json_string(slot.plugin))
        print("								}")
        delimiter = ", "
    print("							]")


def dump_insert(delimiter: str, insert: pyflp.mixer.Insert):
    print("					" + delimiter + "{insert: " + json_string(insert) + "}")
    print("						bypassed: " + json_bool(insert.bypassed))
    print("						, channels_swapped: " + json_bool(insert.channels_swapped))
    print("						, color: " + json_string(insert.color))
    print("						, dock: " + json_string(insert.dock))
    print("						, enabled: " + json_bool(insert.enabled))
    dump_eq(insert.eq)
    print("						, icon: " + json_num(insert.icon))
    print("						, input: " + json_num(insert.input))
    print("						, is_solo: " + json_bool(insert.is_solo))
    print("						, locked: " + json_bool(insert.locked))
    print("						, name: " + json_string(insert.name))
    print("						, output: " + json_num(insert.output))
    print("						, pan: " + json_num(insert.pan))
    print("						, polarity_reversed: " + json_bool(insert.polarity_reversed))
    dump_routes(insert)
    print("						, separator_shown: " + json_bool(insert.separator_shown))
    print("						, stereo_separation: " + json_num(insert.stereo_separation))
    print("						, volume: " + json_num(insert.volume))
    dump_slots(insert)
    print("						}")


def dump_mixer(project: pyflp.Project):
    print("		, mixer: {")
    print("			apdc: " + json_bool(project.mixer.apdc))
    print("			, max_inserts: " + json_num(project.mixer.max_inserts))
    print("			, max_slots: " + json_num(project.mixer.max_slots))
    print("			, inserts: [")
    delimiter = ""
    counter = 0
    for insert in project.mixer:
        if insert.name is not None:
            counter = counter + 1
            if counter > debugLimit and debugLimit > 0:
                print("					...")
                break
            dump_insert(delimiter, insert)
            delimiter = ", "
    print("				]")
    print("			}")


def dump_controller(delimiter: str, controller: pyflp.pattern.Controller):
    print(
        "							"
        + delimiter
        + "{channel: "
        + json_num(controller.channel)
        + ", position: "
        + json_num(controller.position)
        + ", value: "
        + json_num(controller.value)
        + "}"
    )


def dump_note(delimiter: str, note: pyflp.pattern.Note):
    print(
        "							"
        + delimiter
        + "{fine_pitch: "
        + json_num(note.fine_pitch)
        + ", group: "
        + json_num(note.group)
        + ", key: "
        + json_string(note.key)
        + ", length: "
        + json_num(note.length)
        + ", midi_channel: "
        + json_num(note.midi_channel)
        + ", mod_x: "
        + json_num(note.mod_x)
        + ", mod_y: "
        + json_num(note.mod_y)
    )
    print(
        "										, pan: "
        + json_num(note.pan)
        + ", position: "
        + json_num(note.position)
        + ", rack_channel: "
        + json_num(note.rack_channel)
        + ", release: "
        + json_num(note.release)
        + ", slide: "
        + json_bool(note.slide)
        + ", velocity: "
        + json_num(note.velocity)
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
    print("						, notes: [")
    delimiter2 = ""
    counter = 0
    for note in pattern:
        counter = counter + 1
        if counter > debugLimit and debugLimit > 0:
            print("						...")
            break
        dump_note(delimiter2, note)
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
    # dump_arrangements(project)
    print("		, artists: " + json_string(project.artists))
    # dump_channel_rack(project)
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
    # dump_patterns(project)
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
