import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import pyttsx3
from PyPDF2 import PdfReader
import threading

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

def convert_text_to_speech(text, output_file, rate, pitch, voice_id, progress_bar):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('pitch', pitch)
        if voice_id:
            engine.setProperty('voice', voice_id)

        # Estimate progress based on text length
        total_len = len(text)
        processed_len = 0

        def update_progress():
            if processed_len < total_len:
                progress = (processed_len / total_len) * 100
                progress_bar['value'] = progress
                root.after(100, update_progress)
            else:
                progress_bar['value'] = 100

        # This is a simplified progress simulation
        def speak_chunk(chunk):
            nonlocal processed_len
            engine.save_to_file(chunk, output_file)
            engine.runAndWait()
            processed_len += len(chunk)

        # Process in chunks to update progress
        chunk_size = 200 
        for i in range(0, total_len, chunk_size):
            chunk = text[i:i+chunk_size]
            speak_chunk(chunk)
            update_progress() # Manually update after each chunk

        progress_bar['value'] = 100
        messagebox.showinfo("Success", f"Audio saved as {output_file}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")
    finally:
        progress_bar['value'] = 0

def select_pdf():
    file_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    try:
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)

        start = simpledialog.askinteger("Start Page", f"Enter start page (1 to {num_pages}):", minvalue=1, maxvalue=num_pages)
        end = simpledialog.askinteger("End Page", f"Enter end page (start ", " end ", " {num_pages}):", minvalue=start, maxvalue=num_pages)

        if start is None or end is None or start > end:
            messagebox.showerror("Invalid Input", "Page range is invalid.")
            return

        text = extract_text_from_pdf(file_path, start - 1, end)
        if not text.strip():
            messagebox.showerror("Error", "No text found in selected page range.")
            return

        output_name = simpledialog.askstring("Save As", "Enter output filename (without .mp3):")
        if not output_name:
            output_name = "audiobook"
        output_file = f"{output_name}.mp3"

        rate = int(rate_scale.get())
        pitch = pitch_scale.get()
        voice_name = voice_combobox.get()
        voice_id = voice_map.get(voice_name)

        progress_bar.pack(pady=10, fill=tk.X, padx=20)
        
        # Run conversion in a separate thread to keep GUI responsive
        threading.Thread(
            target=convert_text_to_speech,
            args=(text, output_file, rate, pitch, voice_id, progress_bar)
        ).start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

# --- GUI Setup ---
root = tk.Tk()
root.title("PDF to Audiobook Converter")
root.geometry("500x450")
root.resizable(False, False)

# --- Voice Engine Initialization ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
voice_map = {f"Voice {i+1} ({v.gender or 'Unknown'})": v.id for i, v in enumerate(voices)}

# --- Style ---
style = ttk.Style()
style.theme_use('clam')

# --- Main Frame ---
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(expand=True, fill=tk.BOTH)

title_label = ttk.Label(main_frame, text="PDF to Audiobook Converter", font=("Arial", 16, "bold"))
title_label.pack(pady=(0, 20))

# --- Controls Frame ---
controls_frame = ttk.Frame(main_frame)
controls_frame.pack(pady=10, fill=tk.X, padx=20)

# Rate
ttk.Label(controls_frame, text="Speed (Rate):").grid(row=0, column=0, sticky=tk.W, pady=5)
rate_scale = tk.Scale(controls_frame, from_=50, to=300, orient=tk.HORIZONTAL, length=300)
rate_scale.set(200)
rate_scale.grid(row=0, column=1, sticky=tk.EW)

# Pitch
ttk.Label(controls_frame, text="Pitch:").grid(row=1, column=0, sticky=tk.W, pady=5)
pitch_scale = tk.Scale(controls_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, length=300)
pitch_scale.set(1.0)
pitch_scale.grid(row=1, column=1, sticky=tk.EW)

# Voice Selection
ttk.Label(controls_frame, text="Voice:").grid(row=2, column=0, sticky=tk.W, pady=5)
voice_combobox = ttk.Combobox(controls_frame, values=list(voice_map.keys()), state="readonly", width=40)
if voice_map:
    voice_combobox.current(0)
voice_combobox.grid(row=2, column=1, sticky=tk.EW)

# --- Button and Progress Bar ---
select_button = ttk.Button(main_frame, text="Select PDF and Convert", command=select_pdf)
select_button.pack(pady=20)

progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
# Progress bar is packed later when needed

root.mainloop()