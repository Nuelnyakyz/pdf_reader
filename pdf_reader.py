import PyPDF2
import pyttsx3
import re
import os
import time

import text2speech

def read_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        pdf_text = ''

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            pdf_text += page.extract_text()

    return pdf_text

def clean_text(text):
    cleaned_text = re.sub('\n', ' ', text)
    return cleaned_text.strip()

def save_audio(text, pdf_audio):
    engine = pyttsx3.init()

    engine.save_to_file(text, pdf_audio)
    engine.runAndWait()

def main():
    pdf_name = input("Enter .pdf file name: ")
    pdf_file = f"PDFs/{pdf_name}"  # can be replaced with 'path/to/your/pdf'
    speed_factor = 0.9
    retries = 3
    delay = 2

    try:
        
        print("started ...0")

        extracted_text = read_pdf(pdf_file)
        print("extracted ...1")

        cleaned_text = clean_text(extracted_text)
        print("cleaned ...2")

        My_Deepgram_key = os.getenv('MY_DEEPGRAM_KEY')
        
        tts = text2speech.DeepgramTextToSpeech(api_key=My_Deepgram_key, input_filename=pdf_file)
        print("Creating audio, this may take some time ...3")
        tts.text_to_speech(cleaned_text, speed_factor=speed_factor, retries=retries, delay=delay)

    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    main()