# Music Generator  
  
Generate music with artificial intelligence.  
  
## Installation  
  
### Requirements  
  
- Ubuntu 18.06 or Higher  
- Python 3.7 (Does not work on Python 3.10)  
- Reaper 6.69

## Build & Run

### Midi Generator Only
  
### Virtual Environment:



     $ sudo apt-get install build-essential libasound2-dev libjack-dev portaudio19-dev -y sl  
     $ sudo apt-get install libsndfile1 -y sl 
     $ sudo apt install -y fluidsynth 
     $ sudo pip install --no-cache-dir -r requirements.txt  
     

### As Package:

     from aibbeyroad import core 
 
     core.generate_midi('seeds/TearsInHeaven.mid')   
     core.generate_midi_only('seeds/I-want-to-hold-your-hand.MID',4)  

  
## Docs  
  
### aibbeyroad.core  
  
 *Function* **generate_midi(_filename_):**   
   
 Parameters:  
  
-   **filename** (_str_) – Filename or Filepath.  
  
  
 *Function* **generate_midi_only(_filename_, _bars_):**   
   
 Parameters:  
   
-   **filename** (_str_) – Filename or Filepath.  
-   **bars** (_int_) – Number of bars (Length or Compases)


