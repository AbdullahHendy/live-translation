# Kotlin/Android Client

Simple Kotlin/Android app that captures microphone audio and sends it to the live-translation server over WebSocket. It streams **Opus-encoded** audio in real time and logs server responses (transcription and translation).

---

<a href="https://github.com/AbdullahHendy/live-translation/blob/main/doc/android.gif?raw=true" target="_blank">
  <img src="https://github.com/AbdullahHendy/live-translation/blob/main/doc/android.gif?raw=true" alt="Android-Client Demo" />
</a>

---

## Features

- Streams audio from the default system microphone
- Captures raw 640, 16-bit PCM, audio chunks (mono, 16kHz) and encodes it to Opus before streaming
- Streams compressed Opus packets
- Receives and logs transcription and translation from the server
- Simple UI with Start and Stop buttons
- Scrollable log view with color-coded output
---

## Prerequisites

Before running the project, you need to install the following system dependencies:
- [**Android Studio**](https://developer.android.com/studio/install)

---

## Installation

```bash
cd examples/clients/android
```
Open this project, `android`, in **Android Studio** and let it sync the Gradle files.

---

## Usage

- Start [**`server`**](../../../README.md#usage)
- Change the `WEBSOCKET_URL` constant in the `MainActivity.kt` to reflect the **host IP** running the server.
    > **NOTE**: `localhost` doesn't work in emulation environments. **host IP** should be used. 
    >
- If using the **emulator** window, Enable **“Virtual microphone uses host audio input”** in **Extended Controls > Microphone**.
    > **NOTE**: **Extended Controls** is usually the `three dots (⋮)` above the emulator window 
    >
- Run the app

---

## Security Notice
This app enable `cleartext traffic` in the [**AndroidManifest.xml**](./app/src/main/AndroidManifest.xml) via `android:usesCleartextTraffic="true"`.