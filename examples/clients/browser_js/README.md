# Browser JS Client

Minimal browser-based client for sending microphone audio to the live-translation server over WebSocket. It streams **raw PCM** audio in real time and logs server responses (transcription and translation).

---

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/browser_js.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/browser_js.gif?raw=true" alt="Browser-Client Demo" />
</a>

---

## Features

- Captures microphone audio in the browser
- Streams raw PCM audio in 16-bit, mono, 16kHz format
- Buffers and sends 512-sample (1024-byte) chunks
- Receives and logs transcription and translation from the server
- Uses [`AudioWorklet`](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet) for low-latency audio processing

---

## Prerequisites

- A [modern browser](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet#browser_compatibility) that supports `AudioWorklet`.
- `live-translation` WebSocket server running and accessible (e.g. `ws://localhost:8765`)
- Page must be served over `http://localhost` or `https://` (not `file://`)

---

## Usage

- Start [**`server`**](../../../README.md#usage)
- Serve ***this folder*** via a local HTTP server, for example:
    - **Python**
    ```bash
    cd examples/clients/browser_js
    python3 -m http.server 8000
    # then open http://localhost:8000
    ```
    - **Node.js**
    ```bash
    cd examples/clients/browser_js
    npx serve . -l 8000
    # then open http://localhost:8000
    ```