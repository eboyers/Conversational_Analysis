from openai import AzureOpenAI
import os

# language codes: 
# - 'en' for English, 
# - 'es' for Spanish, 
# - 'zh' for Mandarin, 
# - 'fr' for French

client = AzureOpenAI(
    api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # HIDDEN
    api_version="xxxxxxxxxxxxxx",
    azure_endpoint="https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.openai.azure.com/",
)

deployment_id = "xxxxxxxxxxxxxxxx"

def whisper_transcribe(file_path, language):
    """
    Transcribes a given audio file in a specified language.
    """
    contents = open(file_path, 'rb')
    transcription = client.audio.transcriptions.create(
        file=contents,
        model=deployment_id,
        response_format="text",
        language=language, 
        )
    return transcription

def whisper_translate(file_path, language):
    """
    Translates a given audio file to English.
    """
    contents = open(file_path, 'rb')
    translation = client.audio.translations.create(
        file=contents,
        model=deployment_id,
        prompt=f"You are given an audio file in {language}. Please translate and return it in English", # prompt it for translation
        response_format="text"
    )
    return translation

def save_whisper_file(file_path, language):
    """
    Save a Whisper transcription to directory. 
    """
    transcription = whisper_transcribe(file_path, language) # whisper_transcribe(file_path) or whisper_translate(file_path)
    
    save_dir = "whisper_transcriptions" # "whisper_transcriptions" or "whisper_translations"
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    save_file_path = os.path.join(save_dir, f"{file_name}_whisper.txt")
    
    with open(save_file_path, 'w', encoding='utf-8') as f:
        f.write(transcription)