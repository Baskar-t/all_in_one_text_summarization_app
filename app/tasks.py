from celery import Celery
import pke
from textblob import TextBlob
import spacy

celery = Celery(__name__)

@celery.task
def process_text(text):
    summary = "Summary of the text"
    return summary

@celery.task
def extract_keyphrases(text):
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=text)
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=5)
    return keyphrases

@celery.task
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return {'polarity': sentiment.polarity, 'subjectivity': sentiment.subjectivity}

@celery.task
def recognize_entities(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities
