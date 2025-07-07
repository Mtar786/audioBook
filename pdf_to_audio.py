import pyttsx3
from PyPDF2 import PdfReader
import os

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def convert_text_to_speech(text, output_file, rate, pitch, voice_id):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('pitch', pitch)
    if voice_id:
        engine.setProperty('voice', voice_id)
    
    engine.save_to_file(text, output_file)
    engine.runAndWait()

def main():
    pdf_path = input("Enter the path to your PDF file: ").strip()

    if not os.path.exists(pdf_path):
        print("File not found.")
        return

    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    if not text.strip():
        print("No text found in the PDF.")
        return

    # --- Voice Settings ---
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print("\nAvailable Voices:")
    for i, voice in enumerate(voices):
        print(f"{i + 1}. ID: {voice.id} - Gender: {voice.gender}")

    try:
        voice_idx = int(input(f"\nSelect a voice (1 to {len(voices)}): ")) - 1
        if not 0 <= voice_idx < len(voices):
            print("Invalid selection. Using the first voice.")
            voice_idx = 0
        voice_id = voices[voice_idx].id
    except ValueError:
        print("Invalid input. Using the first voice.")
        voice_id = voices[0].id

    try:
        rate = int(input("Enter voice speed (e.g., 150): "))
    except ValueError:
        print("Invalid input. Using default speed (200).")
        rate = 200

    try:
        pitch = float(input("Enter voice pitch (e.g., 1.0): "))
    except ValueError:
        print("Invalid input. Using default pitch (1.0).")
        pitch = 1.0

    output_file = "audiobook.mp3"
    print("\nConverting text to audio...")
    convert_text_to_speech(text, output_file, rate, pitch, voice_id)
    
    print(f"\nDone! Audio saved as {output_file}")

if __name__ == "__main__":
    main()