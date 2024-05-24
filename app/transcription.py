from moviepy.editor import VideoFileClip
import speech_recognition as sr

def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    transcription = recognizer.recognize_google(audio)
    return transcription
