from flask import Blueprint, request, jsonify, render_template
from app import celery
from app.transcription import extract_audio, transcribe_audio
import os

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video = request.files['video']
    video_path = os.path.join('/tmp', video.filename)
    video.save(video_path)

    audio_path = extract_audio(video_path)
    transcription = transcribe_audio(audio_path)

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
