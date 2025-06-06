# Go Client

Simple CLI Go client for sending microphone audio to the live-translation server over WebSocket. It captures **raw PCM** audio, encodes it using **Opus**, and streams it in real time. Server responses (transcription and translation) are logged to the console.

---

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/go.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/go.gif?raw=true" alt="Go-Client Demo" />
</a>

---

## Features

- Streams audio from the default system microphone
- Captures raw 640, 16-bit PCM, audio chunks (mono, 16kHz) and encodes it to Opus before streaming
- Streams compressed Opus packets
- Receives and logs transcription and translation from the server
- Cross-platform support via `malgo` (miniaudio) and `gorilla/websocket`
- Opus encoding via `github.com/hraban/opus`

---

## Prerequisites

Before running the project, you need to install the following system dependencies:
- [**Go**](https://go.dev/doc/install)
- [**libopus** and **libopusfile** development headers]()
    - **MacOS**
        ```zsh
        brew install opus opusfile
        ```
    - **Debian**
        ```bash
        sudo apt install libopus-dev libopusfile-dev
        ```
    - **Windows**
        ```
        Download the binaries from [here](https://opus-codec.org/downloads/)
- Make sure a **proper supported backend** is installed and configured for your operating system (e.g., ALSA for Linux, CoreAudio for MacOS, WASAPI for Windows).
    > **NOTE**: See [supported platforms/backends](https://pkg.go.dev/github.com/gen2brain/malgo#section-readme) for `malgo`

---

## Installation

```bash
cd examples/clients/go_client
go mod tidy
```

---

## Usage

- Start [**`server`**](../../../README.md#usage)
- Run the **`client`**
    ```bash
    go run main.go
    ```