#from aibbeyroad import core
#from aibbeyroad import reaper

import aibbeyroad.studio as ab
import random

songemsemble4chD = [['Pigments (Arturia)', 'Polaris'], ['Pigments (Arturia)', 'Roads Lead On'],
                     ['MS-20 (KORG)', 'Klash PWM Bass'], ['DrumComputer (Sugar Bytes) (2->20ch)', random.randint(0, 30)]]


ab.generate_song('seeds/Major Prog 01 (I-bVII-I-IV).mid', songemsemble4chD)

#session = ab.Session()

#










#core.generate_midi_bars('seeds/Final Fantasy IV - Battle Theme (seed).mid', 1)

#reaper.insert_midi('Cellofan (Arnaud CUEFF) (mono)', '/home/moebius/PycharmProjects/aibbeyroad/aibbeyroad/generated/generated_output.mid')

#reaper.get_violin_song('Cellofan (Arnaud CUEFF) (mono)', '/aibbeyroad/aibbeyroad/generated/generated_output.mid')

#core.generate_song('seeds/TearsInHeaven.mid')

#core.generate_big_song('seeds/TearsInHeaven.mid')

#core.generate_big_song('seeds/I-want-to-hold-your-hand.MID')

#core.harmonize_midi('aibbeyroad/generated/generated_song_535.mid')

#reaper.track_effects(0)

#reaper.del_track_effect(0,0)

#reaper.add_track_effect_preset(0, 'LegacyCell (KORG)',4)

#reaper.change()

#reaper.get_little_song('/home/moebius/PycharmProjects/aibbeyroad/aibbeyroad/generated/generated_song_1470.mid')