# Node.js Client

Simple CLI client for sending microphone audio to the live-translation server over WebSocket. It captures **raw PCM** audio from the system microphone, encodes it to **Opus**, and streams the compressed packets to the server. Transcription and translation responses are logged to the console.

---

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/nodejs.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/nodejs.gif?raw=true" alt="Nodejs-Client Demo" />
</a>

---

## Features

- Streams audio from the default system microphone
- Captures raw 640, 16-bit PCM, audio chunks (mono, 16kHz) and encodes it to Opus before streaming
- Streams compressed Opus packets
- Receives and logs transcription and translation from the server
- Uses `node-record-lpcm16` for mic input, `@discordjs/opus` for encoding, and `ws` for WebSocket communication

---

## Prerequisites

Before running the project, you need to install the following system dependencies:
- [**Node.js**](https://nodejs.org/en/download)
- [**SOX**](https://github.com/chirlu/sox?tab=readme-ov-file)
    - **MacOS**
        ```zsh
        brew install sox
        ```
    - **Debian**
        ```bash
        sudo apt-get install sox libsox-fmt-all
        ```
    - **Windows**
        ```
        Working version for Windows is 14.4.1. download the binaries from [here](https://sourceforge.net/projects/sox/files/sox/14.4.1/)
        ```

---

## Installation

```bash
cd examples/clients/nodejs
npm install
```

---

## Usage

- Start [**`server`**](../../../README.md#usage)
- Run the **`client`**
    ```bash
    node client.js
    ```
> **NOTE**: Do **not** open the HTML file by double-clicking it. Browsers will block mic access and module loading when opened with ***file://***.