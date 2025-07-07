import pyttsx3
from PyPDF2 import PdfReader
import os
import json

CONFIG_FILE = "config_cli.json"

def save_config(rate, pitch, voice_id, pages_per_chapter):
    config = {
        "rate": rate,
        "pitch": pitch,
        "voice_id": voice_id,
        "pages_per_chapter": pages_per_chapter
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def extract_text_from_pdf(pdf_path, start_page=0, end_page=None):
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    if end_page is None or end_page > num_pages:
        end_page = num_pages
    text = ""
    for i in range(start_page, end_page):
        page = reader.pages[i]
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

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    # --- Load Preferences ---
    config = load_config()
    default_rate = config['rate'] if config else 200
    default_pitch = config['pitch'] if config else 1.0
    default_voice_id = config['voice_id'] if config else None
    default_pages_per_chapter = config['pages_per_chapter'] if config else 1

    # --- User Input ---
    start = int(input(f"Enter start page (1 to {num_pages}): "))
    end = int(input(f"Enter end page ({start} to {num_pages}): "))

    process_as_chapters = input("Split into chapters? (yes/no): ").lower() == 'yes'
    pages_per_chapter = default_pages_per_chapter
    if process_as_chapters:
        pages_per_chapter = int(input(f"Pages per chapter (default: {default_pages_per_chapter}): ") or default_pages_per_chapter)

    # --- Voice Settings ---
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("\nAvailable Voices:")
    for i, voice in enumerate(voices):
        print(f"{i + 1}. ID: {voice.id} - Gender: {voice.gender}")
    
    voice_idx = int(input(f"\nSelect a voice (1 to {len(voices)}): ")) - 1
    voice_id = voices[voice_idx].id if 0 <= voice_idx < len(voices) else default_voice_id

    rate = int(input(f"Enter voice speed (default: {default_rate}): ") or default_rate)
    pitch = float(input(f"Enter voice pitch (default: {default_pitch}): ") or default_pitch)

    # --- Save Preferences ---
    save_config(rate, pitch, voice_id, pages_per_chapter)

    output_name = input("Enter base output filename (without .mp3): ") or "audiobook"

    # --- Conversion ---
    if process_as_chapters:
        for i, start_page in enumerate(range(start - 1, end, pages_per_chapter)):
            chapter_num = i + 1
            chapter_start = start_page
            chapter_end = min(start_page + pages_per_chapter, end)
            text = extract_text_from_pdf(pdf_path, chapter_start, chapter_end)
            if text.strip():
                output_file = f"{output_name}_chapter_{chapter_num}.mp3"
                print(f"\nConverting Chapter {chapter_num}... ")
                convert_text_to_speech(text, output_file, rate, pitch, voice_id)
                print(f"Chapter {chapter_num} saved as {output_file}")
    else:
        text = extract_text_from_pdf(pdf_path, start - 1, end)
        if text.strip():
            output_file = f"{output_name}.mp3"
            print("\nConverting text to audio...")
            convert_text_to_speech(text, output_file, rate, pitch, voice_id)
            print(f"Audio saved as {output_file}")
        else:
            print("No text found in selected page range.")

    open_after_save = input("Open audio file(s) after saving? (yes/no): ").lower() == 'yes'
    if open_after_save:
        if process_as_chapters:
            for i in range(len(range(start - 1, end, pages_per_chapter))):
                os.startfile(f"{output_name}_chapter_{i+1}.mp3")
        else:
            os.startfile(f"{output_name}.mp3")

if __name__ == "__main__":
    main()
