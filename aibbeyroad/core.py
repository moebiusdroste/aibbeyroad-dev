import magenta
import note_seq
import tensorflow
from aibbeyroad import reaper
import os
import random
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.polyphony_rnn import polyphony_sequence_generator
from magenta.models.drums_rnn import drums_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2

print('🎉 Done!')
print(magenta.__version__)
print(tensorflow.__version__)


def delete_midi_tempo_map(midi_file):
    seq = note_seq.midi_io.midi_file_to_note_sequence(midi_file)
    seq.tempos.remove(seq.tempos[0])
    note_seq.sequence_proto_to_midi_file(seq, midi_file)
    return True


def generate_drums_session(session):
    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(session.seed)

    # Drums RNN
    print("Initializing Drums RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/drum_kit_rnn.mag')
    generator_map = drums_rnn_sequence_generator.get_generator_map()
    drums_rnn = generator_map['drum_kit'](checkpoint=None, bundle=bundle)
    drums_rnn.initialize()

    input_sequence = sample_seq  # change this to teapot if you want
    num_steps = 128  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in input_sequence.notes)
                     if input_sequence.notes else 0)
    qpm = input_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / drums_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Ask the model to continue the sequence.

    base_sequence = drums_rnn.generate(input_sequence, generator_options)

    sequences = []

    for i in range(0,session.bars):
        sequences.append(base_sequence)

    sequence = note_seq.concatenate_sequences(sequences)

    # export midi

    note_seq.sequence_proto_to_midi_file(sequence, session.session_folder + '/' + session.drums_name)

    return session.session_folder + '/' +session.drums_name


def generate_drums(seed):

    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(seed)

    # Drums RNN
    print("Initializing Drums RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/drum_kit_rnn.mag')
    generator_map = drums_rnn_sequence_generator.get_generator_map()
    drums_rnn = generator_map['drum_kit'](checkpoint=None, bundle=bundle)
    drums_rnn.initialize()

    input_sequence = sample_seq  # change this to teapot if you want
    num_steps = 128  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in input_sequence.notes)
                     if input_sequence.notes else 0)
    qpm = input_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / drums_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Ask the model to continue the sequence.

    sequence = drums_rnn.generate(input_sequence, generator_options)

    # export midi

    note_seq.sequence_proto_to_midi_file(sequence, 'generated_song_drum.mid')


    return True

def get_midi_tempo(midi_file):
    seq = note_seq.midi_io.midi_file_to_note_sequence(midi_file)
    return seq.tempos[0].qpm

def get_bass(seq):
    bass = []
    for note in seq.notes:
        if note.pitch < 60:
            bass.append(note)
    return bass

def compose_song(session):
    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(session.seed)

    # print(sample_seq.notes)
    # Model options. Change these to get different generated sequences!

    # Initialize the model.
    print("Initializing Melody RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/attention_rnn.mag')
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map['attention_rnn'](checkpoint=None, bundle=bundle)
    melody_rnn.initialize()

    input_sequence = sample_seq  # change this to teapot if you want
    num_steps = 128  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in input_sequence.notes)
                     if input_sequence.notes else 0)
    qpm = input_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / melody_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Ask the model to continue the sequence.

    sequence = melody_rnn.generate(input_sequence, generator_options)

    # print(sample_seq.notes)
    # print(len(sequence.notes))
    # twinkle_twinkle = music_pb2.NoteSequence()
    # Add the notes to the sequence.
    # twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)

    for i in range(len(sample_seq.notes)):
        try:
            sequence.notes.remove(sequence.notes[i])
        except IndexError:
            continue

    print(len(sequence.notes))

    sequences = []
    sequences_harmonics = []
    sequence_harmonics = None

    if session.bars != 1:
        sequences.append(sequence)
        for k in range(session.bars):
            sequencex = melody_rnn.generate(input_sequence, generator_options)
            for j in range(len(sample_seq.notes)):
                # print(j)
                try:
                    sequencex.notes.remove(sequencex.notes[j])
                except IndexError:
                    continue

            sequences.append(sequencex)
            # Do Harmonization
            sequencex_harmonics = harmonize_seq(sequencex)
            sequences_harmonics.append(sequencex_harmonics)

        sequence = note_seq.concatenate_sequences(sequences)
        sequence_harmonics = note_seq.concatenate_sequences(sequences_harmonics)

    # note_seq.plot_sequence(sequence)
    # note_seq.play_sequence(sequence, synth=note_seq.fluidsynth)

    # Save the generated MIDI file.
    note_seq.sequence_proto_to_midi_file(sequence, session.session_folder + '/' + session.melody_name)
    note_seq.sequence_proto_to_midi_file(sequence_harmonics, session.session_folder + '/' + session.harmony_name)

    #File dirs
    melody_file = session.session_folder + '/' + session.melody_name
    harmony_file = session.session_folder + '/' + session.harmony_name

    return melody_file, harmony_file

def choo(seed, bars):

    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(seed)

    #print(sample_seq.notes)
    #print(len(sample_seq.notes))
    #twinkle_twinkle = music_pb2.NoteSequence()
    # Add the notes to the sequence.
    #twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)
    sample_seq.notes.remove(sample_seq.notes[0])
    #print(len(sample_seq.notes))


# Polyphonic Harmony Generation
# MIDI
def harmonize_midi(midi):
    # Polyphony RNN
    # Initialize the model.
    print("Initializing Polyphony RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/polyphony_rnn.mag')
    generator_map = polyphony_sequence_generator.get_generator_map()
    polyphony_rnn = generator_map['polyphony'](checkpoint=None, bundle=bundle)
    polyphony_rnn.initialize()

    # Load the primer melody as a NoteSequence.
    primer_sequence = note_seq.midi_file_to_note_sequence(midi)

    num_steps = 512  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in primer_sequence.notes)
                     if primer_sequence.notes else 0)
    qpm = primer_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / polyphony_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)


    # Generate a harmony.
    print("Generating harmony...")
    #generated_sequence = polyphony_rnn.generate(primer_sequence, steps_per_quarter=4, temperature=1.0)

    generated_sequence = polyphony_rnn.generate(primer_sequence, generator_options)

    # Play the generated NoteSequence.
    #note_seq.play_sequence(generated_sequence, synth=note_seq.fluidsynth)

    # Save the generated MIDI file.
    note_seq.sequence_proto_to_midi_file(generated_sequence, 'generated_song_poly_535_test.mid')

    return True

#note_seq
def harmonize_seq(seq):
    # Polyphony RNN
    # Initialize the model.
    print("Initializing Polyphony RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/polyphony_rnn.mag')
    generator_map = polyphony_sequence_generator.get_generator_map()
    polyphony_rnn = generator_map['polyphony'](checkpoint=None, bundle=bundle)
    polyphony_rnn.initialize()

    # Load the primer melody as a NoteSequence.
    primer_sequence = seq

    temperature = 1.0  # Higher is more random; 1.0 is default.

    # Generate 32 bars of polyphonic music.
    num_bars = 32
    last_end_time = max(n.end_time for n in primer_sequence.notes)
    seconds_per_step = 0.25
    total_seconds = num_bars * seconds_per_step * polyphony_rnn.steps_per_quarter


    generator_options = generator_pb2.GeneratorOptions()
    print(generator_options.args)
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)


    # Generate a harmony.
    print("Generating harmony...")
    #generated_sequence = polyphony_rnn.generate(primer_sequence, steps_per_quarter=4, temperature=1.0)

    generated_sequence = polyphony_rnn.generate(primer_sequence, generator_options)

    for i in range(len(seq.notes)):
        try:
            generated_sequence.notes.remove(generated_sequence.notes[i])
        except IndexError:
            continue

    print(len(generated_sequence.notes))

    # Play the generated NoteSequence.
    #note_seq.play_sequence(generated_sequence, synth=note_seq.fluidsynth)

    # Save the generated MIDI file.
    #note_seq.sequence_proto_to_midi_file(generated_sequence, 'generated_song_poly.mid')

    return generated_sequence

#session object
def harmonize_midi_session(session):
    # Polyphony RNN
    # Initialize the model.
    print("Initializing Polyphony RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/polyphony_rnn.mag')
    generator_map = polyphony_sequence_generator.get_generator_map()
    polyphony_rnn = generator_map['polyphony'](checkpoint=None, bundle=bundle)
    polyphony_rnn.initialize()

    # Load the primer melody as a NoteSequence.
    primer_sequence = note_seq.midi_file_to_note_sequence(session.melody_dir)

    temperature = 1.0  # Higher is more random; 1.0 is default.

    # Generate 32 bars of polyphonic music.
    num_bars = 16
    last_end_time = max(n.end_time for n in primer_sequence.notes)
    seconds_per_step = 0.25
    total_seconds = num_bars * seconds_per_step * polyphony_rnn.steps_per_quarter


    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)


    # Generate a harmony.
    print("Generating harmony...")
    #generated_sequence = polyphony_rnn.generate(primer_sequence, steps_per_quarter=4, temperature=1.0)

    generated_sequence = polyphony_rnn.generate(primer_sequence, generator_options)

    # Play the generated NoteSequence.
    #note_seq.play_sequence(generated_sequence, synth=note_seq.fluidsynth)

    # Save the generated MIDI file.
    note_seq.sequence_proto_to_midi_file(generated_sequence, session.session_folder + '/' + session.harmony_name)

    return True


# Monophonic Melody Generation

# N Bars Midi Generation Session
def generate_midi_session(session):

    print("Session: " + session.song_name)
    print("Seed: " + session.seed)

    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(session.seed)

    #print(sample_seq.notes)
    # Model options. Change these to get different generated sequences!

    # Initialize the model.
    print("Initializing Melody RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/attention_rnn.mag')
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map['attention_rnn'](checkpoint=None, bundle=bundle)
    melody_rnn.initialize()

    input_sequence = sample_seq  # change this to teapot if you want
    num_steps = 128  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in input_sequence.notes)
                     if input_sequence.notes else 0)
    qpm = input_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / melody_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Ask the model to continue the sequence.

    sequence = melody_rnn.generate(input_sequence, generator_options)

    # print(sample_seq.notes)
    #print(len(sequence.notes))
    # twinkle_twinkle = music_pb2.NoteSequence()
    # Add the notes to the sequence.
    # twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)

    for i in range(len(sample_seq.notes)):
        try:
            sequence.notes.remove(sequence.notes[i])
        except IndexError:
            continue

    print(len(sequence.notes))

    sequences = []
    if session.bars != 1:
        sequences.append(sequence)
        for k in range(session.bars):
            sequencex = melody_rnn.generate(input_sequence, generator_options)
            for j in range(len(sample_seq.notes)):
                            #print(j)
                            try:
                                sequencex.notes.remove(sequencex.notes[j])
                            except IndexError:
                                continue

            sequences.append(sequencex)

        sequence=note_seq.concatenate_sequences(sequences)



    #note_seq.plot_sequence(sequence)
    # note_seq.play_sequence(sequence, synth=note_seq.fluidsynth)

    # Save the generated MIDI file.
    note_seq.sequence_proto_to_midi_file(sequence, session.session_folder + '/' +session.melody_name)

    return session.session_folder + '/' +session.melody_name


# N Bars Midi Generation
def generate_midi_bars(seed, bars):

    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(seed)

    #print(sample_seq.notes)
    # Model options. Change these to get different generated sequences!

    # Initialize the model.
    print("Initializing Melody RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/attention_rnn.mag')
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map['attention_rnn'](checkpoint=None, bundle=bundle)
    melody_rnn.initialize()

    input_sequence = sample_seq  # change this to teapot if you want
    num_steps = 100 #128  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in input_sequence.notes)
                     if input_sequence.notes else 0)
    qpm = input_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / melody_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Ask the model to continue the sequence.

    sequence = melody_rnn.generate(input_sequence, generator_options)

    # print(sample_seq.notes)
    #print(len(sequence.notes))
    # twinkle_twinkle = music_pb2.NoteSequence()
    # Add the notes to the sequence.
    # twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)

    for i in range(len(sample_seq.notes)):
        try:
            sequence.notes.remove(sequence.notes[i])
        except IndexError:
            continue

    print(len(sequence.notes))

    sequences = []
    if bars != 1:
        sequences.append(sequence)
        for k in range(bars):
            sequencex = melody_rnn.generate(input_sequence, generator_options)
            for j in range(len(sample_seq.notes)):
                            #print(j)
                            try:
                                sequencex.notes.remove(sequencex.notes[j])
                            except IndexError:
                                continue

            sequences.append(sequencex)

        sequence=note_seq.concatenate_sequences(sequences)



    note_seq.plot_sequence(sequence)
    # note_seq.play_sequence(sequence, synth=note_seq.fluidsynth)

    a = random.randint(0, 9000)

    fname = 'generated_song_' + str(a) + '.mid'

    relpath = 'aibbeyroad/generated/' + fname

    note_seq.sequence_proto_to_midi_file(sequence, relpath)

    abpath = os.path.abspath(relpath)

    print(abpath)

    return abpath, fname


# 1 Bar Midi Generation
def generate_midi(seed):

    print('generating song')

    sample_seq = note_seq.midi_io.midi_file_to_note_sequence(seed)
    #print(type(sample_seq))

    # This is a colab utility method that visualizes a NoteSequence.
    #note_seq.plot_sequence(sample_seq)

    # This is a colab utility method that plays a NoteSequence.
    #note_seq.play_sequence(sample_seq, synth=note_seq.fluidsynth)

    # Model

    print('Downloading model bundle. This will take less than a minute...')
    #note_seq.notebook_utils.download_bundle('attention_rnn.mag', 'aibbeyroad/models')

    # Import dependencies.
    from magenta.models.melody_rnn import melody_rnn_sequence_generator
    from magenta.models.shared import sequence_generator_bundle
    from note_seq.protobuf import generator_pb2
    from note_seq.protobuf import music_pb2

    # Initialize the model.
    print("Initializing Melody RNN...")
    bundle = sequence_generator_bundle.read_bundle_file('aibbeyroad/models/attention_rnn.mag')
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map['attention_rnn'](checkpoint=None, bundle=bundle)
    melody_rnn.initialize()

    print('🎉 Done!')

    # Model options. Change these to get different generated sequences!

    input_sequence = sample_seq  # change this to teapot if you want
    num_steps = 128  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.

    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in input_sequence.notes)
                     if input_sequence.notes else 0)
    qpm = input_sequence.tempos[0].qpm
    seconds_per_step = 60.0 / qpm / melody_rnn.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Ask the model to continue the sequence.
    sequence = melody_rnn.generate(input_sequence, generator_options)

    note_seq.plot_sequence(sequence)
    #note_seq.play_sequence(sequence, synth=note_seq.fluidsynth)

    a=random.randint(0,9000)

    fname = 'generated_song_' +  str(a) + '.mid'

    relpath = 'aibbeyroad/generated/'+fname

    note_seq.sequence_proto_to_midi_file(sequence, relpath)

    abpath = os.path.abspath(relpath)

    print(abpath)

    return abpath, fname