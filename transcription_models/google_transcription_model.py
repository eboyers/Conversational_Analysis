from google.cloud import speech
from google.cloud import translate_v2 as translate
import os

# language codes: 
# - 'en-US' for English, 
# - 'es' for Spanish, 
# - 'cmn' for Mandarin, 
# - 'fr' for French

def google_transcribe_chunk(file_path, source_language):
    """
    Transcribes a given audio file portion in a specified language.
    """
    client = speech.SpeechClient()

    with open(file_path, 'rb') as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        model="telephony", # OPTIONS: 'phone_call', 'medical_conversation', 'medical_dictation', 'default', 'telephony'
        encoding=speech.RecognitionConfig.AudioEncoding.MP3, # use MP3 format
        sample_rate_hertz=8000, # 8000 for telephony, 16000 for others
        language_code=source_language # set language as that spoken in audio file
    )

    response = client.recognize(config=config, audio=audio)
    transcript = ""

    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return transcript

def google_transcribe(folder_path, source_language):
    """
    Transcribes and concatenates transcription.
    """
    combined_transcript = ""

    files = sorted(f for f in os.listdir(folder_path))

    for file in files:
        file_path = os.path.join(folder_path, file)
        combined_transcript += google_transcribe_chunk(file_path, source_language)

    return combined_transcript

def google_translate(folder_path, source_language):
    """
    Translates an audio file in another language into English.
    """
    translate_client = translate.Client()
    text = google_transcribe(folder_path, source_language)
    translation = translate_client.translate(text, 
                                             source_language=source_language, 
                                             target_language='en-US')
    return translation['translatedText']

def save_google_file(folder_path, output_file, source_language):
    """
    Function to save Google transcription.
    """
    transcription = google_transcribe(folder_path, source_language)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transcription)
