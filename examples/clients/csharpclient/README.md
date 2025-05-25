# C# Client

Simple CLI C# client for sending microphone audio to the live-translation server over WebSocket. It streams **raw PCM** audio in real time and logs server responses (transcription and translation).

---

## Features

- Streams audio from the default system microphone
- Streams raw PCM audio in 16-bit, mono, 16kHz format
- Buffers and sends 512-sample (1024-byte) chunks
- Receives and logs transcription and translation from the server
- Cross-platform support via `PortAudioSharp2` (miniaudio) and `WebSocketSharp`

---

## Prerequisites

- [**.NET SDK**](https://dotnet.microsoft.com/en-us/download)
- [**PortAudio**](https://www.portaudio.com/)
    - **MacOS**
        ```zsh
        brew install sox
        ```
    - **Debian**
        ```bash
        sudo apt-get install sox libsox-fmt-all
        ```

---

## Installation

```bash
cd clients/csharpclient
dotnet restore
```

---

## Usage

- Start [**`server`**](../../../README.md#usage)
- Run the **`client`**
    ```bash
    dotnet run
    ```