# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from celery import Celery
from flask import request, jsonify, render_template

import os

from moviepy.editor import VideoFileClip
import assemblyai as aai

aai.settings.api_key = "53ae342c0bef4d36825651da23edf1b5"

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)   

    celery = make_celery(app)
    return app, celery

app, celery = create_app()

def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio(audio_path):
    recognizer = aai.Transcriber()
   
    transcription = recognizer.transcribe(audio_path)
    print(transcription.text)
    return transcription

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video = request.files['video']
    video_path = os.path.join('/tmp', video.filename)
    video.save(video_path)

    audio_path = extract_audio(video_path)
    transcription = transcribe_audio(audio_path)

    print(transcription)

    task_summarize = celery.signature('app.tasks.process_text', args=[transcription])
    task_keyphrases = celery.signature('app.tasks.extract_keyphrases', args=[transcription])
    task_sentiment = celery.signature('app.tasks.analyze_sentiment', args=[transcription])
    task_entities = celery.signature('app.tasks.recognize_entities', args=[transcription])

    result_summarize = task_summarize.apply_async()
    result_keyphrases = task_keyphrases.apply_async()
    result_sentiment = task_sentiment.apply_async()
    result_entities = task_entities.apply_async()

    summarize_result = result_summarize.get()
    keyphrases_result = result_keyphrases.get()
    sentiment_result = result_sentiment.get()
    entities_result = result_entities.get()

    response = {
        'transcription': transcription,
        'summary': summarize_result,
        'keyphrases': keyphrases_result,
        'sentiment': sentiment_result,
        'entities': entities_result
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run()
