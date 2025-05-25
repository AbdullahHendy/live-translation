# Node.js Client

Simple CLI Go client for sending microphone audio to the live-translation server over WebSocket. It streams **raw PCM** audio in real time and logs server responses (transcription and translation).

---

## Features

- Streams audio from the default system microphone
- Streams raw PCM audio in 16-bit, mono, 16kHz format
- Buffers and sends 512-sample (1024-byte) chunks
- Receives and logs transcription and translation from the server
- Cross-platform support via `malgo` (miniaudio) and `gorilla/websocket`

---

## Prerequisites

Before running the project, you need to install the following system dependencies:
- [**Go**](https://go.dev/doc/install)
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