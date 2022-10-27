import reapy
from reapy import reascript_api as RPR
import os
import random



def cleanmiditake(tracknum):
    project = reapy.Project()
    track = project.tracks[tracknum]
    print(track.items)
    items = track.items[0]
    print(items.takes[0])
    take = items.takes[0]
    print(take.midi_events)
    firstev = take.midi_events[0]
    firstev.delete()

# Insert MIDI File from filepath
def insert_midi(file):

    print(reapy.get_reaper_version())

    project = reapy.Project()

    RPR.InsertMedia(file, 1)

    reapy.update_timeline()

    return True

def insert_midi_drum(file):

    print(reapy.get_reaper_version())

    project = reapy.Project()

    RPR.InsertMedia(file, 1)


    reapy.update_timeline()

    return True

# List of Track Effects on a given Track
def track_effects(tracknum):
    project = reapy.Project()
    track = project.tracks[tracknum]
    print(len(track.fxs))

    for effect in range(len(track.fxs)):
        fx = track.fxs[effect]
        print(fx.name)

# Delete FX on a given Track
def del_track_effect(tracknum, effectnum):
    project = reapy.Project()
    track = project.tracks[tracknum]
    print(len(track.fxs))
    fx = track.fxs[effectnum]
    fx.delete()

# Add FX onto a given Track
def add_track_effect(tracknum, effect):
    project = reapy.Project()
    track = project.tracks[tracknum]
    track.add_fx(effect)
    print(len(track.fxs))

# Set Preset onto a FX/Track
def add_track_effect_preset(tracknum, effect, preset):
    project = reapy.Project()
    track = project.tracks[tracknum]
    fx = track.add_fx(effect)
    fx.preset = preset

# Next preset
def np(tracknum, effectnum):
    project = reapy.Project()
    track = project.tracks[tracknum]
    fx = track.fxs[effectnum]
    fx.use_next_preset()

# Delete All Tracks on project
def delete_tracks(numtracks):

    project = reapy.Project()

    for tracknum in range(numtracks):
        track = project.tracks[numtracks-tracknum]
        track.delete()

    track = project.tracks[0]
    track.delete()


# Export project
def export():
    project = reapy.Project()
    # Export to WAV (Default)
    project.perform_action(41824)
    track = project.tracks[0]
    fx = track.fxs[0]
    fx.close_ui()


    # Closes Project


    #project.close()


# Song Ensemble Functions

def get_violin_song(file):

    insert_midi(file)

    track_effects(0)

    del_track_effect(0,0)

    track_effects(0)

    export()

    return True

def get_little_song(file, fname):

    change_filename(fname)

    #ViolinSetting
    track1 = 0
    insert_midi(file)
    cleanmiditake(track1)
    track_effects(track1)
    del_track_effect(track1,0)
    track_effects(track1)
    add_track_effect_preset(track1,'Polysix (KORG)', 'Reso Bell')

    #KeyboardSetting track 1
    track2 = 1
    insert_midi(file)
    cleanmiditake(track2)
    track_effects(track2)
    del_track_effect(track2, 0)
    track_effects(track2)
    add_track_effect_preset(track2, 'LegacyCell (KORG)', 4)

    # Drms Setting track 1
    track2 = 2
    insert_midi(file)
    cleanmiditake(track2)
    track_effects(track2)
    del_track_effect(track2, 0)
    track_effects(track2)
    add_track_effect_preset(track2, 'DrumComputer (Sugar Bytes) (2->20ch)', random.randint(0,10))
    export()
    delete_tracks()

    return True


def set_up_export(fname, format):
    change_filename(fname.replace('.mid', format))


def get_song_3ch(file, fname, song3ch):

    #song3ch=[['Polysix (KORG)', 'Reso Bell'],['LegacyCell (KORG)', 4],['DrumComputer (Sugar Bytes) (2->20ch)', random.randint(0,10)]]


    change_filename(fname.replace('.mid',''))

    #ViolinSetting
    track1 = 0
    insert_midi(file)
    #cleanmiditake(track1)
    track_effects(track1)
    #del_track_effect(track1,0)
    track_effects(track1)
    add_track_effect_preset(track1,song3ch[0][0], song3ch[0][1])

    #KeyboardSetting track 1
    track2 = 1
    insert_midi(file)
    #cleanmiditake(track2)
    track_effects(track2)
    #del_track_effect(track2, 0)
    track_effects(track2)
    add_track_effect_preset(track2, song3ch[1][0], song3ch[1][1])

    # Drms Setting track 1
    track2 = 2
    insert_midi(file)
    #cleanmiditake(track2)
    track_effects(track2)
    #del_track_effect(track2, 0)
    track_effects(track2)
    add_track_effect_preset(track2, song3ch[2][0], song3ch[2][1])
    #export()
    #delete_tracks()

    print('Song Generated: ' + fname.replace('.mid','.wav'))

    return True

def get_song_4ch(session,song4ch):

    #song3ch=[['Polysix (KORG)', 'Reso Bell'],['LegacyCell (KORG)', 4],['DrumComputer (Sugar Bytes) (2->20ch)', random.randint(0,10)]]

    change_filename(session.melody_name.replace('.mid',''))

    #Lead Keyboard Track
    track1 = 0
    insert_midi(session.get_melody_absolute_path())
    #cleanmiditake(track1)
    track_effects(track1)
    #del_track_effect(track1,0)
    track_effects(track1)
    add_track_effect_preset(track1,song4ch[0][0], song4ch[0][1])

    #Pad Keyboard Track
    track2 = 1
    insert_midi(session.get_melody_absolute_path())
    #cleanmiditake(track2)
    track_effects(track2)
    #del_track_effect(track2, 0)
    track_effects(track2)
    add_track_effect_preset(track2, song4ch[1][0], song4ch[1][1])

    # Bass Track
    track3 = 2
    insert_midi(session.get_melody_absolute_path())
    #cleanmiditake(track2)
    track_effects(track3)
    #del_track_effect(track2, 0)
    track_effects(track3)
    add_track_effect_preset(track3, song4ch[2][0], song4ch[2][1])


    # Drms Track
    track4 = 3
    insert_midi_drum(session.drums_type0_dir)
    # cleanmiditake(track2)
    track_effects(track4)
    # del_track_effect(track2, 0)
    track_effects(track4)
    add_track_effect_preset(track4, song4ch[3][0], song4ch[3][1])
    export()

    delete_tracks(3)

    print('Song Generated: ' + session.melody_name.replace('.mid','.wav'))

    #delete_tracks()

    return True

def change_filename(filename):

    project = reapy.Project()

    print(project.time_signature)

    x = project.set_info_string('RENDER_PATTERN',filename)

    print(x)

    print(project.path)

    #RPR.Main_SaveProject(0, False)


    return True