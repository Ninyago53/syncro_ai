# syncro_ai

# Python YouTube Video Translator

This Python script uses multiple APIs and libraries to download, transcribe, translate, and generate voiceovers for YouTube videos. Users can save the YouTube video of their choosing, convert the video's audio text into any chosen language, and then convert the translated text into speech. The script supports user input to control whether the original audio is included at a reduced volume.

## Script Functions

1. The Python script first uses the yt_dlp library to download a YouTube video.

2. The downloaded video is then converted into an audio file.

3. The audio file is subsequently segmented and transcribed, using the WhisperX and Torch libraries.

4. After transcription, the OpenAI model gpt-3.5-turbo translates the transcribed text into the user's desired language.

5. The translated text is then again converted into speech, and a separate audio file is generated for each dialogue segment of the video.

6. The audio files are then synchronized with the original video files, and the user has the option to include original audio at reduced volume.

7. Finally, the video is output with the translated voiceover.

## Prerequisites 

* Python installed (Python 3.8+ is recommended)
* An installation of pip (Python's package installer)
* Git installed to clone this repository

## Installation Instructions

Clone the repository to your local system:

```cmd
git clone https://github.com/Ninyago53/syncro_ai
```
Navigate to the cloned repo's directory

```cmd
cd syncro_ai
```
Create a virtual environment:

Make sure you're in the same directory as your Python script. Then create a new virtual environment in your terminal/command line:

```cmd
python3 -m venv env
```

Activate the virtual environment:

Windows:
```cmd
.\env\Scripts\activate
```
Mac/Linux:
```cmd
source env/bin/activate
```
Install the dependencies:

```cmd
pip install -r requirements.txt
```

## How to use this script
After installing the packages, run the script like any other Python script:

```cmd
python main.py
```

Follow the prompts in the console to download, transcribe, translate and generate a voiceover for a YouTube video.
