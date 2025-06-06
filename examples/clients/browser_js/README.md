# Browser JS Client

Minimal browser-based client for sending microphone audio to the live-translation server over WebSocket. It captures **raw PCM audio** (16-bit, mono, 16kHz), **encodes it to Opus** using WebAssembly in real time, and streams compressed packets to the server. Transcription and translation responses are logged live in the browser.

---

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/browser_js.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/browser_js.gif?raw=true" alt="Browser-Client Demo" />
</a>

---

## Features

- Captures microphone audio in the browser
- Captures raw 640, 16-bit PCM, audio chunks (mono, 16kHz) and encodes it to Opus in-browser before streaming
- Streams compressed Opus packets
- Receives and logs transcription and translation from the server
- Uses [`AudioWorklet`](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet) for low-latency audio processing
- Uses [`libopusjs`](https://github.com/ImagicTheCat/libopusjs) for WebAssembly-based Opus encoding

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