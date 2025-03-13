# Real-time Speech-to-Text Translation

This project provides a real-time speech-to-text translation solution. It captures audio from the microphone, transcribes it into text, and translates it to a target language. It uses the **Whisper** model for transcription and **M2M-100** for translation.

## Features

- Real-time speech capture using Silero VAD (Voice Activity Detection)
- Speech-to-text transcription using the Whisper model
- Translation of transcriptions from a source language to a target language
- Multithreaded design for efficient processing
- Different output modes: stdout, JSON file, websocket server

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
    usage: live_translation.py [-h] [--silence_threshold SILENCE_THRESHOLD] [--vad_aggressiveness {0,1,2,3,4,5,6,7,8,9}] [--max_buffer_duration {5,6,7,8,9,10}] [--device {cpu,cuda}] [--whisper_model {tiny,base,small,medium,large,large-v2}]
                            [--trans_model_name {Helsinki-NLP/opus-mt,Helsinki-NLP/opus-mt-tc-big}] [--src_lang SRC_LANG] [--tgt_lang TGT_LANG] [--output {print,file,websocket}] [--ws_port WS_PORT] [--transcribe_only]

    Audio Processing Pipeline - Configure runtime settings.

    options:
    -h, --help            show this help message and exit
    --silence_threshold SILENCE_THRESHOLD
                            Number of consecutive 32ms silent chunks to detect SILENCE.
                            SILENCE triggers sending a 'FULL' audio buffer for transcription/translation.
                            Default is 65 (~ 2s).
    --vad_aggressiveness {0,1,2,3,4,5,6,7,8,9}
                            Voice Activity Detection (VAD) aggressiveness level (0-9).
                            Higher values mean VAD has to be more confident to detect speech.
                            Default is 8.
    --max_buffer_duration {5,6,7,8,9,10}
                            Max audio buffer duration in seconds before cutting 75% of it.
                            Default is 7 seconds.
    --device {cpu,cuda}   Device for processing ('cpu', 'cuda').
                            Default is 'cpu'.
    --whisper_model {tiny,base,small,medium,large,large-v2}
                            Whisper model size ('tiny', 'base', 'small', 'medium', 'large', 'large-v2').
                            Default is 'base'.
    --trans_model_name {Helsinki-NLP/opus-mt,Helsinki-NLP/opus-mt-tc-big}
                            Translation model name ('Helsinki-NLP/opus-mt', 'Helsinki-NLP/opus-mt-tc-big'). 
                            NOTE: Don't include source and target languages here.
                            Default is 'Helsinki-NLP/opus-mt'.
    --src_lang SRC_LANG   Source/Input language for transcription (e.g., 'en', 'fr').
                            Default is 'en'.
    --tgt_lang TGT_LANG   Target language for translation (e.g., 'es', 'de').
                            Default is 'es'.
    --output {print,file,websocket}
                            Output method ('print', 'file', 'websocket').
                            - 'print': Prints transcriptions and translations to stdout.
                            - 'file': Saves structured JSON data (see below) in transcripts/transcriptions.json.
                            - 'websocket': Sends structured JSON data (see below) over WebSocket.
                            JSON format for 'file' and 'websocket':
                            {
                                "timestamp": "2025-03-06T12:34:56.789Z",
                                "transcription": "Hello world",
                                "translation": "Hola mundo"
                            }.
                            Default is 'print'.
    --ws_port WS_PORT     WebSocket port for sending transcriptions.
                            Required if --output is 'websocket'.
    --transcribe_only     Transcribe only mode. No translations are performed.
    ```

2. The program will continuously listen for speech, transcribe the audio, and send the output using the selected mode.
    > **NOTE**: The output including timestamp, ***src_lang*** transcription, and ***tgt_lang*** translation is sent out after the translation stage.
    >
    > **NOTE**: One can safely ignore the following warning:
    >
    > ALSA lib pcm_dsnoop.c:567:(snd_pcm_dsnoop_open) unable to open slave
    > ALSA lib pcm_dmix.c:1000:(snd_pcm_dmix_open) unable to open slave
    > ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
    > ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
    > ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
    > ALSA lib pcm_dmix.c:1000:(snd_pcm_dmix_open) unable to open slave
    > Cannot connect to server socket err = No such file or directory
    > Cannot connect to server request channel
    > jack server is not running or cannot be started
    > JackShmReadWritePtr::~JackShmReadWritePtr - Init not done for -1, skipping unlock
    > JackShmReadWritePtr::~JackShmReadWritePtr - Init not done for -1, skipping unlock
    >
    
    - in case of websockets, one can connect to the server using: 
      - curl, wscat, etc..
      ```bash
      curl --include --no-buffer ws://localhost:<PORT_NUM>
      ```
      ```bash
      wscat -c ws://localhost:<PORT_NUM>
      ```
      - more structured client code
      ```python
      import asyncio
      import websockets

      PORT_NUMBER = 4567

      async def connect():
          async with websockets.connect(f"ws://localhost:{PORT_NUMBER}") as ws:
              print("Connected to WebSocket server!")
              try:
                  while True:
                      print(f"Received: {await ws.recv()}")
              except websockets.exceptions.ConnectionClosed:
                  print("Connection closed!")
              except asyncio.CancelledError:
                  print("Stopped!")

      async def main():
          await connect()

      asyncio.run(main())
      ```
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
- **Concurrency Design Check**: Review and optimize the threading design to ensure thread safety and prevent issues like race conditions or deadlocks, etc., revisit the current design of ***AudioRecorder*** being a thread while ***AudioProcessor***, ***Transcriber***, and ***Translator*** being processes.
- **Missed Translation Context**: Address potential issues with missing context during translation. Consider implementing context management to ensure translations are coherent and make use of preceding information.
- **Code Formatting**: Ensure consistent code formatting across the entire project using tools like `black` or `autopep8` to follow PEP-8 standards and make the code more readable.
- **Unit Testing**: Add unit tests for various components, including the audio capture, transcription, and translation modules with proper coverage.
- **Logging**: Integrate detailed logging to track system activity, errors, and performance metrics using a more formal logging framework.

