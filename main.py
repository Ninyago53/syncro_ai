import yt_dlp

URL = input("Welches Youtube Video wollen Sie herunterladen?: ")
language_used = input("Which language is used? (name the language in English) ")
intentional_language = input("What language do you want your video translated into?: ")
question = input("Do you want to have the original audio of the video in the background with reduced volume?: ")


def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'Video.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

download_video(URL)


from moviepy.editor import AudioFileClip

def convert_mp4_to_mp3(mp4_file_path, mp3_file_path):
    audio = AudioFileClip(mp4_file_path)
    audio.write_audiofile(mp3_file_path)

mp4_file_path = 'Video.mp4'
mp3_file_path = 'Output.mp3'

convert_mp4_to_mp3(mp4_file_path, mp3_file_path)
print("fertig Video to Audio")

import locale
import whisperx
from pydub import AudioSegment
import torch
import gc

def getpreferredencoding(do_setlocale = True):
    return "UTF-8"

locale.getpreferredencoding = getpreferredencoding 

def convert_mp3_to_wav(input_file, output_file):
    audio = AudioSegment.from_file(input_file, format="mp3")
    audio.export(output_file, format="wav") 

input_file = "Output.mp3" 
output_file = "output.wav"
convert_mp3_to_wav(input_file, output_file) 

device = "cpu"
audio_file = "output.wav"
batch_size = 16 
compute_type = "float32" 

model = whisperx.load_model("medium", device, compute_type=compute_type)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"]) 
torch.cuda.empty_cache();
del model 

model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
torch.cuda.empty_cache(); del model_a 

diarize_model = whisperx.DiarizationPipeline(use_auth_token="HF_Token", device="cpu") 
diarize_segments = diarize_model(audio_file)

result = whisperx.assign_word_speakers(diarize_segments, result)
transcriptions = result["segments"]

with open("transcriptions.txt", "w") as file:
    for i, segment in enumerate(transcriptions):
        file.write(f"Segment {i + 1}:\n")
        file.write(f"Start time: {segment['start']:.2f}\n")
        file.write(f"End time: {segment['end']:.2f}\n")
        file.write(f"Speaker: {segment['speaker']}\n")
        file.write(f"Transcript: {segment['text']}\n\n")


import openai
import os
import time

openai.api_key = 'API_Token'

def get_chatbot_response(text):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f'Translate this sentence from "{language_used}" one-to-one to "{intentional_language}":"{text}"'}]
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f'Error occurred: {e}, retrying in 10 seconds...')
            time.sleep(10)

with open("transcriptions.txt", "r") as file:
    lines = file.readlines()

translated_lines = []

for line in lines:
    if "Transcript: " in line:
        text = line.split('Transcript: ', 1)[1].strip()
        translated_text = get_chatbot_response(text)
        translated_lines.append(line.replace(text, translated_text))
        time.sleep(5.0)
    else:
        translated_lines.append(line)

# write translated texts to the file
with open("translated_transcriptions.txt", "w") as file:
    file.writelines(translated_lines)

print("Chatgpt")

import requests
import os
from pathlib import Path

def speak(text = None, filename="generated_audio", voice_id="3fyJImb2Wokl6iajyYE0"):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    api_key = "ElevenLabs_API"
    headers = { "Content-Type": "application/json", "xi-api-key" : api_key }

    data = {"text": text}
    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)

    if response.status_code == 200:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(f'{filename}.mp3', 'wb') as f:
            f.write(response.content)
        print(f"File {filename}.mp3 saved successfully.")
    else:
        print("Request failed with status code:", response.status_code)

segments = []
with open('translated_transcriptions.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('Transcript:'):
            transcript = line.split('Transcript:')[1].strip()
            transcript = transcript.replace('"', '')
            segments.append(transcript)

for idx, text in enumerate(segments):
    speak(text, f"generated_audio/segment_{idx+1}", "yoZ06aMxZJJ28mfd3POQ")


import re
from tinytag import TinyTag
from pydub import AudioSegment

times, final_times, pauses = [], [], []

with open('translated_transcriptions.txt', 'r') as file:
    data = file.read()

start_times = re.findall(r'Start time: (\d+.\d+)', data)
end_times = re.findall(r'End time: (\d+.\d+)', data)

assert len(start_times) == len(end_times)

pauses.append(start_times[0])

for i in range(len(start_times)):
    time_difference = round(float(end_times[i]) - float(start_times[i]), 2)
    times.append(str(time_difference))

for i in range(len(times)):
    tag = TinyTag.get(f'generated_audio/segment_{i+1}.mp3')
    mp3_duration = tag.duration
    final_time = round(float(times[i]) - mp3_duration, 2)
    final_times.append(str(final_time))

for i in range(1, len(start_times)):
    pause = round(float(start_times[i]) - float(end_times[i-1]), 2) + float(final_times[i-1])
    pauses.append(str(pause))

print(pauses)

final_audio = AudioSegment.empty()

for i in range(len(start_times)):
    if i < len(pauses):
        pause = int(float(pauses[i]) * 1000)
        final_audio += AudioSegment.silent(duration=pause)
    
    segment = AudioSegment.from_mp3(f'generated_audio/segment_{i+1}.mp3')
    final_audio += segment

final_audio.export("final_audio.wav", format="wav")


from moviepy.editor import *

question = question.lower()

if question == "yes":
    video = VideoFileClip("Video.mp4")
    original_audio = video.audio
    original_audio = original_audio.volumex(0.4)  # reduce volume by 60%
    video = video.without_audio()
    video.write_videofile("temp_no_audio.mp4")

    audioclip = AudioFileClip('final_audio.wav')
    audioclip = audioclip.volumex(1.0)  

    new_audio = CompositeAudioClip([audioclip, original_audio])
    videoclip = VideoFileClip("temp_no_audio.mp4")
    videoclip = videoclip.set_audio(new_audio)
    videoclip.write_videofile("Video_synchronized.mp4")

if question == "no":
  video = VideoFileClip("Video.mp4")
  video = video.without_audio()
  video.write_videofile("temp_no_audio.mp4")


  audioclip = AudioFileClip('final_audio.wav')
  videoclip = VideoFileClip("temp_no_audio.mp4")
  videoclip = videoclip.set_audio(audioclip)

  videoclip.write_videofile("Video_synchronized.mp4")


print("done")
