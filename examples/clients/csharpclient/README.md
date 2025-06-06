# C# Client

Simple CLI C# client for sending microphone audio to the live-translation server over WebSocket. It captures **raw PCM** audio from the microphone, encodes it to **Opus** in real time, and streams the compressed packets to the server. Transcription and translation responses are logged to the console.

---

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/csharp.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/csharp.gif?raw=true" alt="C#-Client Demo" />
</a>

---

## Features

- Streams audio from the default system microphone
- Captures raw 640, 16-bit PCM, audio chunks (mono, 16kHz) and encodes it to Opus before streaming
- Streams compressed Opus packets
- Receives and logs transcription and translation from the server
- Cross-platform support via [`PortAudioSharp2`](https://www.nuget.org/packages/PortAudioSharp2) (miniaudio) and [`WebSocketSharp`](https://www.nuget.org/packages/WebSocketSharp)
- Uses [`Concentus`](https://www.nuget.org/packages/Concentus) for native-compatible Opus encoding

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