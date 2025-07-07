import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import pyttsx3
from PyPDF2 import PdfReader
import threading
import json
import os

CONFIG_FILE = "config.json"

def save_config(rate, pitch, voice_name, open_after_save, pages_per_chapter):
    config = {
        "rate": rate,
        "pitch": pitch,
        "voice_name": voice_name,
        "open_after_save": open_after_save,
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

def convert_text_to_speech(text, output_file, rate, pitch, voice_id, progress_bar, open_after_save):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('pitch', pitch)
        if voice_id:
            engine.setProperty('voice', voice_id)

        total_len = len(text)
        processed_len = 0

        def speak_chunk(chunk):
            nonlocal processed_len
            engine.save_to_file(chunk, output_file)
            engine.runAndWait()
            processed_len += len(chunk)
            progress = (processed_len / total_len) * 100
            progress_bar['value'] = progress
            root.update_idletasks()

        chunk_size = 200
        for i in range(0, total_len, chunk_size):
            chunk = text[i:i+chunk_size]
            speak_chunk(chunk)

        progress_bar['value'] = 100
        messagebox.showinfo("Success", f"Audio saved as {output_file}")

        if open_after_save:
            os.startfile(output_file)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")
    finally:
        progress_bar['value'] = 0

def select_pdf():
    file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    try:
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)

        # --- User Input --- #
        start = simpledialog.askinteger("Start Page", f"Enter start page (1 to {num_pages}):", minvalue=1, maxvalue=num_pages)
        end = simpledialog.askinteger("End Page", f"Enter end page (start ", " end ", " {num_pages}):", minvalue=start, maxvalue=num_pages)
        if start is None or end is None or start > end:
            messagebox.showerror("Invalid Input", "Page range is invalid.")
            return

        # --- Chapter Settings --- #
        process_as_chapters = messagebox.askyesno("Process as Chapters?", "Do you want to split the PDF into chapters?")
        pages_per_chapter = 1
        if process_as_chapters:
            pages_per_chapter = simpledialog.askinteger("Pages per Chapter", "Enter the number of pages per chapter:", minvalue=1, maxvalue=(end - start + 1))
            if not pages_per_chapter:
                return

        # --- Output Settings --- #
        output_name = simpledialog.askstring("Save As", "Enter base output filename (without .mp3):")
        if not output_name:
            output_name = "audiobook"

        # --- Get Settings from GUI --- #
        rate = int(rate_scale.get())
        pitch = pitch_scale.get()
        voice_name = voice_combobox.get()
        voice_id = voice_map.get(voice_name)
        open_after_save = open_after_save_var.get()

        # --- Save Preferences --- #
        save_config(rate, pitch, voice_name, open_after_save, pages_per_chapter if process_as_chapters else 1)

        progress_bar.pack(pady=10, fill=tk.X, padx=20)

        # --- Conversion Logic --- #
        def conversion_thread():
            if process_as_chapters:
                for i, start_page in enumerate(range(start - 1, end, pages_per_chapter)):
                    chapter_num = i + 1
                    chapter_start = start_page
                    chapter_end = min(start_page + pages_per_chapter, end)
                    text = extract_text_from_pdf(file_path, chapter_start, chapter_end)
                    if text.strip():
                        output_file = f"{output_name}_chapter_{chapter_num}.mp3"
                        convert_text_to_speech(text, output_file, rate, pitch, voice_id, progress_bar, open_after_save)
            else:
                text = extract_text_from_pdf(file_path, start - 1, end)
                if text.strip():
                    output_file = f"{output_name}.mp3"
                    convert_text_to_speech(text, output_file, rate, pitch, voice_id, progress_bar, open_after_save)
                else:
                    messagebox.showerror("Error", "No text found in selected page range.")
            
            progress_bar.pack_forget()

        threading.Thread(target=conversion_thread).start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# --- GUI Setup --- #
root = tk.Tk()
root.title("PDF to Audiobook Converter")
root.geometry("550x550")
root.resizable(False, False)

# --- Voice Engine Initialization --- #
engine = pyttsx3.init()
voices = engine.getProperty('voices')
voice_map = {f"Voice {i+1} ({v.gender or 'Unknown'})": v.id for i, v in enumerate(voices)}

# --- Style --- #
style = ttk.Style()
style.theme_use('clam')

# --- Main Frame --- #
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(expand=True, fill=tk.BOTH)

title_label = ttk.Label(main_frame, text="PDF to Audiobook Converter", font=("Arial", 18, "bold"))
title_label.pack(pady=(0, 20))

# --- Controls Frame --- #
controls_frame = ttk.Frame(main_frame)
controls_frame.pack(pady=10, fill=tk.X, padx=20)

# --- Load Preferences --- #
config = load_config()

# Rate
ttk.Label(controls_frame, text="Speed (Rate):").grid(row=0, column=0, sticky=tk.W, pady=5)
rate_scale = tk.Scale(controls_frame, from_=50, to=300, orient=tk.HORIZONTAL, length=350)
rate_scale.set(config['rate'] if config else 200)
rate_scale.grid(row=0, column=1, sticky=tk.EW)

# Pitch
ttk.Label(controls_frame, text="Pitch:").grid(row=1, column=0, sticky=tk.W, pady=5)
pitch_scale = tk.Scale(controls_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, length=350)
pitch_scale.set(config['pitch'] if config else 1.0)
pitch_scale.grid(row=1, column=1, sticky=tk.EW)

# Voice Selection
ttk.Label(controls_frame, text="Voice:").grid(row=2, column=0, sticky=tk.W, pady=5)
voice_combobox = ttk.Combobox(controls_frame, values=list(voice_map.keys()), state="readonly", width=45)
if voice_map:
    default_voice = config['voice_name'] if config and config['voice_name'] in voice_map else list(voice_map.keys())[0]
    voice_combobox.set(default_voice)
voice_combobox.grid(row=2, column=1, sticky=tk.EW)

# --- Additional Options --- #
options_frame = ttk.Frame(main_frame)
options_frame.pack(pady=10, fill=tk.X, padx=20)

open_after_save_var = tk.BooleanVar(value=(config['open_after_save'] if config else True))
open_after_save_check = ttk.Checkbutton(options_frame, text="Open audio file(s) after saving", variable=open_after_save_var)
open_after_save_check.pack(side=tk.LEFT)

# --- Button and Progress Bar --- #
select_button = ttk.Button(main_frame, text="Select PDF and Convert", command=select_pdf)
select_button.pack(pady=20)

progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')

root.mainloop()