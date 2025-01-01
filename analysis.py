import threading
import re
from openai import AzureOpenAI
from soap_notes_and_transcripts.transcripts import *
from soap_notes_and_transcripts.individual_soap_notes import *
from soap_notes_and_transcripts.transcript_soap_notes import *
from prompts.transcript_meat_prompts import *
from prompts.soap_meat_prompts import *
from prompts.soap_and_transcript_meat_prompts import *
from reg_models.gpt_model import run_gpt
from reg_models.medlm_model import run_medlm

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #

CHUNK_SIZE = 2 # 2 sentences per chunk
SOAP_NOTE = 1 # SOAP Note to analyze
TRANSCRIPT = 1 # transcript to analyze
MODEL = 'gpt-4o' # change for other models (gpt-35-turbo, gpt-4o, gpt-4-turbo, medium, or large)

default_analysis = { # default = no findings
    "Monitoring": "Unable to find enough relevant information to accurately populate the Monitoring findings. Please review this section.",
    "Evaluation": "Unable to find enough relevant information to accurately populate the Evaluation findings. Please review this section.",
    "Assessment": "Unable to find enough relevant information to accurately populate the Assessment findings. Please review this section.",
    "Treatment": "Unable to find enough relevant information to accurately populate the Treatment findings. Please review this section."
}

def analyze_text(chunk, model_type):
    """
    Chosen model analyzes a certain chunk of text from the text and returns the analysis.
    """
    analysis = {"Monitoring": set(), "Evaluation": set(), "Assessment": set(), "Treatment": set()} # sets to eliminate duplicate values

    for meat_prompt in meat_prompts_soap_and_transcript:

        prompts = [p for p in meat_prompt['query'] if p['role'] == 'user']
        query = prompts[0]['content'].format(soap_note=chunk, transcript=chunk) # extract query for model
        output = None
        
        ### USING GPT MODELS ###
        if model_type in ['gpt-35-turbo', 'gpt-4-turbo', 'gpt-4o']: 
            output = run_gpt(query, model_type)
        ### USING MEDLM MODELS ###
        elif model_type in ['medium', 'large']: 
            output = run_medlm(query, model_type)
            
        sections = output.split('\n') # split output into sections (lines)
        cur_criteria = None

        for section in sections:
            section = section.strip()
            if section.endswith(':'): # extract criteria label
                cur_criteria = section[:-1]
            elif cur_criteria and cur_criteria in analysis:
                negative_words = ["does not", "no", "not", "neither", "lack", "lacks", "fail", "fails"] # safeguard against adding negative comments
                if section and not any(word in section for word in negative_words): # section doesn't contain negative comments
                    analysis[cur_criteria].add(section)

    return analysis

def summarize_section(section, section_label):
    """
    Use GPT-4o to summarize each section of analysis and reduce redundancies.
    """
    if not section: return default_analysis[section_label] # if no analysis, report no findings

    combined_analysis = " ".join(section)

    client = AzureOpenAI(
        api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # HIDDEN
        api_version="xxxxxxxxxxxxxx",
        azure_endpoint="https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.openai.azure.com/",
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
                "content": "You summarize the following text about {section_label} into a more concise statement:"},
                {"role": "user",
                "content": combined_analysis}
        ],
        temperature=0,
        max_tokens=200 # shortish summaries
    )

    return response.choices[0].message.content.strip()
    
def merge_format_analysis(cur_analysis, new_analysis):
    """
    Merge new analysis with current analysis, apply proper formatting.
    """
    for criteria in cur_analysis.keys():
        cur_analysis[criteria].update(new_analysis[criteria]) # merge existing analysis with new analysis

    formatted = "" # initialize formatted analysis

    for criteria, analysis in cur_analysis.items(): # now format the analysis
        if not analysis:
            formatted += f"{criteria}:\n- {default_analysis[criteria]}\n\n" # add default message if no good analysis
        else:
            formatted += f"{criteria}:\n- {summarize_section(analysis, criteria)}\n\n" # else summarize analyses into more concise statements

    return formatted.strip()

def real_time_analysis(transcript, soap_note, soap_widg, analysis_widg):
    """
    Analyze text chunk by chunk, simulate real-time analysis.
    """
    cur_pos = 0
    text = transcript + soap_note # concatenate both documents
    sentences = re.split(r'(?<=[.!?]) +', text) # split into sentences based on punctuation
    total_analysis = {"Monitoring": set(), "Evaluation": set(), "Assessment": set(), "Treatment": set()} # initialize analysis

    while cur_pos < len(sentences): # process SOAP note in pieces delegated by number of 'CHUNK_SIZE' sentences
        
        chunk = " ".join(sentences[cur_pos: cur_pos + CHUNK_SIZE]) # join section's sentences together
        soap_widg.insert(tk.END, f"{chunk} ") # add chunks to full SOAP note as processed

        cur_analysis = analyze_text(chunk, model_type=MODEL) # analyze section
        updated_analysis = merge_format_analysis(total_analysis, cur_analysis) # combine it with existing analysis

        analysis_widg.delete("1.0", tk.END)
        analysis_widg.insert(tk.END, updated_analysis) # insert updated analysis

        cur_pos += CHUNK_SIZE

def do_analysis(soap_widg, analysis_widg):
    """
    Initializes the analysis process with a thread. 
    """
    transcript = transcripts_text[TRANSCRIPT]
    soap_note = individual_soap_notes_text[SOAP_NOTE] # extract SOAP note to analyze

    threading.Thread(target=real_time_analysis, # start a thread for our analysis
                     args=(transcript, 
                           soap_note,
                           soap_widg,
                           analysis_widg)).start()

# ---------------------------------------------------------------------------- #
# -------------------------- ### GUI Components ### -------------------------- #

import tkinter as tk
from tkinter import scrolledtext

def run_analysis():

    window = tk.Tk()
    window.title("Real-Time MEAT Analysis")

    # SOAP Note section (label and widget)
    soap_lbl = tk.Label(window, text="SOAP Note")
    soap_lbl.pack(pady=10, padx=10)
    
    soap_widg = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=120, height=20)
    soap_widg.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Analysis section (label and widget)
    analysis_lbl = tk.Label(window, text="MEAT Analysis")
    analysis_lbl.pack(pady=10, padx=10)

    analysis_widg = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=120, height=20)
    analysis_widg.pack(pady=10, padx=10,fill="both",expand=True)
    
    # Start button
    start_btn = tk.Button(window, text="Start Analysis", command=lambda: do_analysis(soap_widg, analysis_widg))
    start_btn.pack(pady=10, padx=10)

    window.mainloop()
    
def main():
    run_analysis()

if __name__ == "__main__":
    main()
