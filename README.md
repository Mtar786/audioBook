# PDF to Audiobook Converter

This project contains two Python scripts that convert PDF files into audiobooks:

1.  `pdf_to_audio_gui.py`: A graphical user interface (GUI) application built with Tkinter.
2.  `pdf_to_audio.py`: A command-line interface (CLI) application.

## Features

- **PDF to Audio Conversion**: Extracts text from a PDF file and converts it into an MP3 audio file.
- **Custom Page Selection**: Allows users to specify a range of pages to convert.
- **Chapter-Based Conversion**: Split a long PDF into multiple audio files, each representing a chapter.
- **Voice Customization**:
    - **Voice Selection**: Choose between different available voices (e.g., male, female).
    - **Speed (Rate) Control**: Adjust the speaking speed.
    - **Pitch Control**: Modify the voice pitch.
- **Save User Preferences**: The application saves your settings (e.g., voice, speed, pitch) for future use.
- **Progress Bar (GUI)**: Visual feedback during the conversion process.
- **Open File on Completion**: Automatically open the generated audio file(s) once the conversion is finished.
- **Cross-Platform**: Both scripts are written in Python and should run on any platform where the required libraries are installed.

## Requirements

- Python 3
- `PyPDF2`
- `pyttsx3`

You can install the required libraries using pip:
```bash
pip install PyPDF2 pyttsx3
```

## Usage

### GUI Version

To run the graphical application, execute the following command in your terminal:

```bash
python pdf_to_audio_gui.py
```

1.  **Adjust Settings**: Use the sliders to set the desired voice speed and pitch. Select a voice from the dropdown menu.
2.  **Chapter Settings**: Decide if you want to split the PDF into chapters and specify the number of pages per chapter.
3.  **Select PDF**: Click the "Select PDF and Convert" button to choose a PDF file.
4.  **Set Page Range**: You will be prompted to enter the start and end pages for the conversion.
5.  **Save File**: Enter a name for the output MP3 file(s).
6.  **Conversion**: The progress bar will show the status of the conversion. A message will appear once it's complete.

### Command-Line Version

To run the command-line application, use this command:

```bash
python pdf_to_audio.py
```

1.  **Enter PDF Path**: Provide the full path to your PDF file.
2.  **Chapter Settings**: Choose whether to split the PDF into chapters and define the number of pages per chapter.
3.  **Select Voice**: A list of available voices will be displayed. Choose one by entering its corresponding number.
4.  **Set Speed and Pitch**: Enter the desired values for voice speed (rate) and pitch.
5.  **Conversion**: The script will convert the text and save it as one or more audio files.
6.  **Open Files**: You'll be asked if you want to open the generated audio file(s).