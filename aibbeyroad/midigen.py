from midiutil import MIDIFile
# importing "random" for random operations
import random

# Python program to get average of a list
def Average(lst):
    return sum(lst) / len(lst)

#asthetic_degrees  = [5,2,3,4,5,4,1,6,30,4,10,3,0,3,5,0,5,0,4,4,3,2,5,0,0,0]  # MIDI note number Pumping Anthem
degrees  = [3,2,1,10,20,5,2,3,3]  #spiritual

average = Average(degrees)

track    = 0
channel  = 0
time     = 0    # In beats
duration = 1    # In beats
tempo    = round(average, 2)   # In BPM
volume   = 100  # 0-127, as per the MIDI standard

# Python code to count the number of occurrences
def countX(lst, x):
    count = 0
    for ele in lst:
        if (ele == x):
            count = count + 1
    return count

MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
MyMIDI.addTempo(track, time, tempo)

for i, pitch in enumerate(degrees):
    time = degrees.index(pitch)           # start on beat 0
    duration = countX(degrees, pitch)     # 1 beat long
    volume = 100     # 1 beat long
    MyMIDI.addNote(track, channel, pitch, time, duration, volume)

with open("aliya_spirit.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)