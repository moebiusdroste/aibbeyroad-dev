from aibbeyroad import reaper
from aibbeyroad import core
import random
import os
import mido


class Session:
    def __init__(self):
        self.song_name = None
        self.seed_name = None
        self.session_id = None
        self.seed_dir = None
        self.seed = None

        self.generate_session_id()

        # Session Folder
        self.session_folder = None
        self.create_session_folder()

        # Melody Generation Settings
        self.bars = 4
        self.melody_name = None
        self.melody_dir = None

        # Drums Generation Settings
        self.drums_name = None
        self.drums_dir = None
        self.drums_type0_name = None
        self.drums_type0_dir = None

        # Song Recording Settings
        self.songemsemble = None

        # Reaper Settings
        # Export
        self.export_format = 'wav'

    def generate_session_id(self):
        if self.session_id is None:
            self.session_id = random.randint(0, 1000000)
            return self.session_id
        else:
            print('Session ID already exists')

    def generate_song_name(self):
        self.song_name = 'song_' + str(self.session_id)
        return self.song_name

    def create_session_folder(self):
        # Directory
        directory = 'session-' + str(self.session_id)

        # Parent Directory path
        parent_dir = 'aibbeyroad/sessions'

        # Path
        path = os.path.join(parent_dir, directory)

        os.mkdir(path)

        self.session_folder = path

        print("Directory '% s' created" % directory)


    def load_seed(self, seed):
        self.seed = seed
        #self.generate_session_id()
        self.generate_song_name()
        self.seed_name = self.seed.split('/')[-1]
        self.seed_dir = self.seed.replace(self.seed_name, '')
        #self.create_session_folder()


    def generate_melody(self):
        self.melody_name = str(self.session_id) + '_generated_(Melody).mid'
        self.melody_dir = core.generate_midi_session(self)
        return True

    def get_melody_absolute_path(self):
        if self.melody_dir is None:
            return False

        return os.path.abspath(self.melody_dir)

    def get_drums_absolute_path(self):
        if self.drums_dir is None:
            return False

        return os.path.abspath(self.drums_dir)

    def generate_drums(self):
        self.drums_name = str(self.session_id) + '_generated_(Drums).mid'
        self.drums_dir = core.generate_drums_session(self)
        self.merge_drums()
        return True

    def merge_drums(self):
        m = mido.MidiFile(self.get_drums_absolute_path())
        mido.merge_tracks(m.tracks)
        drum_midi_name_type0 = self.get_drums_absolute_path().replace('.mid', '_type0.mid')
        m.save(drum_midi_name_type0)
        self.drums_type0_name = self.drums_name.replace('.mid', '_type0.mid')
        self.drums_type0_dir = drum_midi_name_type0
        core.delete_midi_tempo_map(self.drums_type0_dir)

    def get_melody_tempo(self):
        return core.get_midi_tempo(self.get_melody_absolute_path())

    def get_drums_tempo(self):
        return core.get_midi_tempo(self.get_drums_absolute_path())

    def record_song(self):
        if self.songemsemble is None:
            return False
        #reaper.record_session(self)
        reaper.get_song_4ch(self, self.songemsemble)

    def print_session(self):
        print('Session ID: ' + str(self.session_id))
        print('Session Folder: ' + self.session_folder)
        print('Seed: ' + self.seed)
        print('Seed Name: ' + self.seed_name)
        print('Seed Dir: ' + self.seed_dir)
        print('Song Name: ' + self.song_name)
        print('Melody Name: ' + self.melody_name)
        print('Melody Dir: ' + self.melody_dir)
        print('Drums Name: ' + self.drums_name)
        print('Drums Dir: ' + self.drums_dir)
        print('Drums Type0 Name: ' + self.drums_type0_name)
        print('Drums Type0 Dir: ' + self.drums_type0_dir)
        print('Song Emsemble: ' + self.songemsemble)
        print('Export Format: ' + self.export_format)



def generate_song(seed, song_arrangements):

    session = Session()
    session.load_seed(seed)
    session.generate_melody()
    session.generate_drums()
    session.songemsemble = song_arrangements
    session.record_song()

    return True