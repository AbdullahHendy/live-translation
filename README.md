# Real-time Speech-to-Text Translation

This project provides a real-time speech-to-text translation solution. It captures audio from the microphone, transcribes it into text, and translates it to a target language. It uses the **Whisper** model for transcription and **M2M-100** for translation.

## Features

- Real-time speech capture using WebRTC VAD (Voice Activity Detection)
- Speech-to-text transcription using the Whisper model
- Translation of transcriptions from a source language to a target language
- Multithreaded design for efficient processing

## Prerequisites

Before running the project, you need to install the following system dependencies:

- **PortAudio** (for audio input handling)
    - On Ubuntu/Debian-based systems, you can install it with:
      ```bash
      sudo apt-get install portaudio19-dev
      ```
- **FFmpeg** (for audio and video processing)
    - On Ubuntu/Debian-based systems, you can install it with:
      ```bash
      sudo apt-get install ffmpeg
      ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/speech-to-text-translation.git
   cd speech-to-text-translation
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
3. Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
4. Install dependencies
    ```bash
    pip install -r requirements.txt    
    ```

## Usage & Configuration

1. **Run the application** with:
   ```bash
   python live_translation.py [OPTIONS]
   ```
    **OPTIONS**:
    ```bash
    usage: live_translation.py [-h] [--silence_threshold SILENCE_THRESHOLD] [--vad_aggressiveness {0,1,2,3}] [--device {cpu,cuda}]
                  [--whisper_model {tiny,base,small,medium,large,large-v2}] [--trans_model_name {facebook/m2m100_418M,facebook/m2m100_1.2B}]
                  [--src_lang SRC_LANG] [--tgt_lang TGT_LANG]

    Audio Processing Pipeline - Configure runtime settings.

    options:
      -h, --help            show this help message and exit
      --silence_threshold SILENCE_THRESHOLD
                            Number of consecutive 30ms silent chunks before detecting SILENCE. SILENCE triggers sending a 'FULL' audio buffer for transcription/translation. Default is 10.
      --vad_aggressiveness {0,1,2,3}
                            Voice Activity Detection (VAD) aggressiveness level (0-3). Higher values are more aggressive. Default is 3.
      --device {cpu,cuda}   Device for processing ('cpu', 'cuda'). Default is 'cpu'.
      --whisper_model {tiny,base,small,medium,large,large-v2}
                            Whisper model size ('tiny', 'base', 'small', 'medium', 'large', 'large-v2'). Default is 'base'.
      --trans_model_name {facebook/m2m100_418M,facebook/m2m100_1.2B}
                            Translation model name ('facebook/m2m100_418M', 'facebook/m2m100_1.2B'). Default is 'facebook/m2m100_418M'.
      --src_lang SRC_LANG   Source/Input language for transcription (e.g., 'en', 'fr'). Default is 'en'.
      --tgt_lang TGT_LANG   Target language for translation (e.g., 'es', 'de'). Default is 'es'.
    ```

2. The program will continuously listen for speech, transcribe the audio, and print the translated text to the console.
3. To stop the program, press **Ctrl+C**.

## Tested Environment

This project was tested and developed on the following system configuration:

- **Architecture**: x86_64 (64-bit)
- **Operating System**: Ubuntu 24.10 (Oracular Oriole)
- **Kernel Version**: 6.11.0-18-generic
- **Python Version**: 3.12.7
- **Processor**: 13th Gen Intel(R) Core(TM) i9-13900HX
- **GPU**: GeForce RTX 4070 Max-Q / Mobile [^1]
- **RAM**: 16GB DDR5
- **Dependencies**: All required dependencies are listed in `requirements.txt` and [Prerequisites](#prerequisites)

[^1]: CUDA not utilized, as the `DEVICE` configuration is set to `"cpu"`. Additional Nvidia drivers, CUDA, cuDNN installation needed if option `"cuda"` were to be used.

## Improvements

- **Block Diagram**: Include a block diagram to visually represent the flow and architecture of the system, making it easier to understand the overall design.
- **Better Error Handling**: Improve error handling across various components (audio, transcription, translation) to ensure the system is robust and can handle unexpected scenarios gracefully.
- **Performance Optimization**: Investigate performance bottlenecks including checking sleep durations and optimizing concurrency management to minimize lag.
- **Concurrency Design Check**: Review and optimize the threading design to ensure thread safety and prevent issues like race conditions or deadlocks, etc., revisit the current design of ***AudioRecorder*** being a thread while ***Transcriber*** and ***Translator*** being processes.
- **Missed Translation Context**: Address potential issues with missing context during translation. Consider implementing context management to ensure translations are coherent and make use of preceding information.
- **Code Formatting**: Ensure consistent code formatting across the entire project using tools like `black` or `autopep8` to follow PEP-8 standards and make the code more readable.
- **Unit Testing**: Add unit tests for various components, including the audio capture, transcription, and translation modules, to improve test coverage and ensure system stability.
- **Logging**: Integrate detailed logging to track system activity, errors, and performance metrics. This will help with debugging, monitoring, and maintaining the application in production environments.

