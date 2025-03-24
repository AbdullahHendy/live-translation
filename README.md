# Real-time Speech-to-Text Translation

This project provides a real-time speech-to-text translation solution. It captures audio from the microphone, processes it, transcribes it into text, and translates it to a target language. It uses the **Silero** model for processing (Voice Activity Detection), **Whisper** model for transcription and **Opus-MT** for translation. The output can be through ***stdout***, a ***JSON file***, or ***websockets***. 

#### 🖥️ Print Output Demo

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/print.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/print.gif?raw=true" alt="Print Demo" />
</a>

#### 🌍 WebSocket Output Demo

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/websocket.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/websocket.gif?raw=true" alt="WebSocket Demo" />
</a>

## Architecture Overview
<img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/live-translation-piepline.png?raw=true" alt="Architecture Diagram" />


## Features

- Real-time speech capture and processing using **Silero** VAD (Voice Activity Detection)
- Speech-to-text transcription using the Whisper model
- Translation of transcriptions from a source language to a target language
- Multithreaded design for efficient processing
- Different output modes: stdout, **JSON** file, websocket server

## Prerequisites

Before running the project, you need to install the following system dependencies:

- **PortAudio** (for audio input handling)
- **FFmpeg** (for audio and video processing)
    - On Ubuntu/Debian-based systems, you can install it with:
      ```bash
      sudo apt-get install portaudio19-dev ffmpeg
      ```

## Installation

**(RECOMMENDED)**: install this package inside a virtual environment to avoid dependency conflicts.
```bash
python -m venv .venv
source .venv/bin/activate
```

**Install** the [PyPI package](https://pypi.org/project/live-translation/0.3.2/):
```bash
pip install live-translation
```

**Verify** the installation:
```bash
python -c "import live_translation; print('live-translation installed successfully!')"
```

## Usage

> **NOTE**: One can safely ignore the following warning that might appear on **Linux** systems:
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

### CLI 
live-translation can be run directly from the command line:
```bash
live-translate [OPTIONS]
```

**[OPTIONS]**
```bash
usage: live-translate [-h] [--silence_threshold SILENCE_THRESHOLD] [--vad_aggressiveness {0,1,2,3,4,5,6,7,8,9}] [--max_buffer_duration {5,6,7,8,9,10}] [--device {cpu,cuda}] [--whisper_model {tiny,base,small,medium,large,large-v2}]
                      [--trans_model {Helsinki-NLP/opus-mt,Helsinki-NLP/opus-mt-tc-big}] [--src_lang SRC_LANG] [--tgt_lang TGT_LANG] [--output {print,file,websocket}] [--ws_port WS_PORT] [--transcribe_only]

Live Translation Pipeline - Configure runtime settings.

options:
  -h, --help            show this help message and exit
  --silence_threshold SILENCE_THRESHOLD
                        Number of consecutive 32ms silent chunks to detect SILENCE.
                        SILENCE clears the audio buffer for transcription/translation.
                        NOTE: Minimum value is 16.
                        Default is 65 (~ 2s).
  --vad_aggressiveness {0,1,2,3,4,5,6,7,8,9}
                        Voice Activity Detection (VAD) aggressiveness level (0-9).
                        Higher values mean VAD has to be more confident to detect speech vs silence.
                        Default is 8.
  --max_buffer_duration {5,6,7,8,9,10}
                        Max audio buffer duration in seconds before trimming it.
                        Default is 7 seconds.
  --device {cpu,cuda}   Device for processing ('cpu', 'cuda').
                        Default is 'cpu'.
  --whisper_model {tiny,base,small,medium,large,large-v2}
                        Whisper model size ('tiny', 'base', 'small', 'medium', 'large', 'large-v2').
                        Default is 'base'.
  --trans_model {Helsinki-NLP/opus-mt,Helsinki-NLP/opus-mt-tc-big}
                        Translation model ('Helsinki-NLP/opus-mt', 'Helsinki-NLP/opus-mt-tc-big'). 
                        NOTE: Don't include source and target languages here.
                        Default is 'Helsinki-NLP/opus-mt'.
  --src_lang SRC_LANG   Source/Input language for transcription (e.g., 'en', 'fr').
                        Default is 'en'.
  --tgt_lang TGT_LANG   Target language for translation (e.g., 'es', 'de').
                        Default is 'es'.
  --output {print,file,websocket}
                        Output method ('print', 'file', 'websocket').
                          - 'print': Prints transcriptions and translations to stdout.
                          - 'file': Saves structured JSON data (see below) in ./transcripts/transcriptions.json.
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

- in case of **websockets**, one can connect to the server using **curl**, **wscat**, etc.. 
  ```bash
  curl --include --no-buffer ws://localhost:<PORT_NUM>
  ```
  ```bash
  wscat -c ws://localhost:<PORT_NUM>
  ```

### API
You can also import and use live_translation directly in your Python code.
The following is a ***simple*** example of running *live_translation* in a server/client fashion.
For more detailed examples see [examples/](/examples/).

- **Server**
  ```python
  from live_translation.config import Config
  from live_translation.app import LiveTranslationApp

  def main():
      config = Config(
          device="cpu",
          output="websocket",
          ws_port=8765
      )

      # Create and start the Live Translation App
      app = LiveTranslationApp(config)
      app.run()

  # Main guard is CRITICAL for systems that uses spawn method to create new processes
  # This is the case for Windows and MacOS
  if __name__ == "__main__":
      main()
  ```

- **Client**
  ```python
  import asyncio
  import websockets
  import json

  async def listen():
      uri = "ws://localhost:8765"
      async with websockets.connect(uri) as websocket:
          print("🔌 Connected to Live Translation WebSocket server.")

          try:
              while True:
                  message = await websocket.recv()
                  data = json.loads(message)

                  print(f"⏳ Timestamp: {data['timestamp']}")
                  print(f"📝 Transcription: {data['transcription']}")
                  print(f"🌍 Translation: {data['translation']}\n")

          except websockets.exceptions.ConnectionClosed:
              print("WebSocket connection closed.")

  asyncio.run(listen())
  ```

## Development

To contribute or modify this project, these steps might be helpful:
> **NOTE**: This workflow below is made for Linux-based systems. One might need to do some step manually on other systems. For example run test manually using `python -m pytest -s tests/` instead of `make test`. 
> See **Makefile** for more details.


**Clone** the repository:
```bash
git clone git@github.com:AbdullahHendy/live-translation.git
cd live-translation
```

**Ceate** a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate 
```

**Install** Dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Test** the package:
```bash
make test
```

**Build** the package:
```bash
make build
```
> **NOTE**: Building does ***lint*** and checks for ***formatting*** using [ruff](https://docs.astral.sh/ruff/). One can do that seprately using `make format` and `make lint`. For linting and formatting rules, see the [ruff config](/ruff.toml).

> **NOTE**: Building generates a ***.whl*** file that can be ***pip*** installed in a new environment for testing

**If needed**, run the program within the virtual environment:
```bash
python -m live_translation.cli [OPTIONS]
```

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

- **Better Error Handling**: Improve error handling across various components (audio, transcription, translation) to ensure the system is robust and can handle unexpected scenarios gracefully.
- **Performance Optimization**: Investigate performance bottlenecks including checking sleep durations and optimizing concurrency management to minimize lag.
- **Concurrency Design Check**: Review and optimize the threading design to ensure thread safety and prevent issues like race conditions or deadlocks, etc., revisit the current design of ***AudioRecorder*** being a thread while ***AudioProcessor***, ***Transcriber***, and ***Translator*** being processes.
- **Logging**: Integrate detailed logging to track system activity, errors, and performance metrics using a more formal logging framework.

## Citations
 ```bibtex
  @article{Whisper,
    title = {Robust Speech Recognition via Large-Scale Weak Supervision},
    url = {https://arxiv.org/abs/2212.04356},
    author = {Radford, Alec and Kim, Jong Wook and Xu, Tao and Brockman, Greg and McLeavey, Christine and Sutskever, Ilya},
    publisher = {arXiv},
    year = {2022}
  }

  @misc{Silero VAD,
    author = {Silero Team},
    title = {Silero VAD: pre-trained enterprise-grade Voice Activity Detector (VAD), Number Detector and Language Classifier},
    year = {2021},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/snakers4/silero-vad}},
    email = {hello@silero.ai}
  }

  @article{tiedemann2023democratizing,
    title={Democratizing neural machine translation with {OPUS-MT}},
    author={Tiedemann, J{\"o}rg and Aulamo, Mikko and Bakshandaeva, Daria and Boggia, Michele and Gr{\"o}nroos, Stig-Arne and Nieminen, Tommi and Raganato, Alessandro and Scherrer, Yves and Vazquez, Raul and Virpioja, Sami},
    journal={Language Resources and Evaluation},
    number={58},
    pages={713--755},
    year={2023},
    publisher={Springer Nature},
    issn={1574-0218},
    doi={10.1007/s10579-023-09704-w}
  }

  @InProceedings{TiedemannThottingal:EAMT2020,
    author = {J{\"o}rg Tiedemann and Santhosh Thottingal},
    title = {{OPUS-MT} — {B}uilding open translation services for the {W}orld},
    booktitle = {Proceedings of the 22nd Annual Conference of the European Association for Machine Translation (EAMT)},
    year = {2020},
    address = {Lisbon, Portugal}
  }
```