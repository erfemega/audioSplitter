from pydub import AudioSegment
import pandas as pd
import sys
import re
import pathlib

from local_config import LOCATION_PATH, EXCEL_PATH, INITIAL_ROW, OUTPUT_FOLDER

sys.stdout.reconfigure(encoding='utf-8')

def time_to_miliseconds(time):
    time_parts = time.split(':')
    if len(time_parts) == 3:  
      hours, minutes, seconds = map(int, time_parts)
    elif len(time_parts) == 2:
       hours = 0
       minutes, seconds = map(int, time_parts)
    else:
       raise ValueError('Time format not valid!!!!!!')
    miliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000
    formated_hours = str(hours).zfill(2)
    formated_minutes = str(minutes).zfill(2)
    formated_seconds = str(seconds).zfill(2)
    formated_time = f"{formated_hours}_{formated_minutes}_{formated_seconds}"
    return [miliseconds, formated_time]
    
def get_sub_track(current_audio_data, time_start, time_finish, output_base_name):
  [t1, formated_start] = time_to_miliseconds(time_start)
  [t2, formated_end] = time_to_miliseconds(time_finish)
  output_name = f"{output_base_name}_{formated_start}.mp3"
  splittedAudio = current_audio_data[t1:t2]
  splittedAudio.export(output_name, format='mp3')
  return output_name

def handle_identifier(identifier):
   return re.sub(r'([a-zA-Z]+)(\d+)', r'\1_\2', identifier).lower()

COLUMNS = {
   'identifier': 'Identificador',
   'song_title': 'Título',
   'start': 'INICIO',
   'end': 'FINAL',
   'year': 'Año'
}

file_location = LOCATION_PATH
excel_file = EXCEL_PATH
initial_row = INITIAL_ROW

print(f"""
  This script will use:
      file location: {file_location}
      excel file: {excel_file}
      initial row: {initial_row}
""")

rows_to_skip = list(range(1, initial_row - 1))
print('Step 1: Reading excel')
df = pd.read_excel(excel_file, skiprows=rows_to_skip)

current_audio_identifier = ''
current_audio_data = None
track_number = 0
current_output_folder = ''
print('Step2: Start row iteration')
for i, row in (df.iterrows()):
  identifier = row[COLUMNS['identifier']]
  start_time = row[COLUMNS['start']]
  end_time = row[COLUMNS['end']]
  year = row[COLUMNS['year']]
  song_title = row[COLUMNS['song_title']].lower().replace(' ', '_')

  input_name = f"{handle_identifier(identifier)}_{str(year)}.wav"

  if pd.isna(start_time) or pd.isna(end_time):
     #print(f"Song from identifier {identifier} and name {song_title} does not contain start/end info")
     continue
  
  if identifier != current_audio_identifier:
    track_number = 1
    current_audio_identifier = identifier
    current_output_folder = f"{OUTPUT_FOLDER}/{identifier}/"
    pathlib.Path(current_output_folder).mkdir(parents=True, exist_ok=True)
    print('\r')
    print(f"#### Creating files identifier: {identifier}")
    current_audio_data = AudioSegment.from_wav(file_location + input_name)
  else:
     track_number = track_number + 1

  output_base_name = f"{current_output_folder}{handle_identifier(identifier)}_{year}_{str(track_number).zfill(2)}_{song_title}"
  print(f"Creating track number: {track_number}")
  
  output_name = get_sub_track(current_audio_data, start_time, end_time, output_base_name)
  print(f"Saved as: {output_name}")

