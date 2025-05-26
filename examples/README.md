# Examples

Simple scripts that demonstrate different ways to use `live_translation`. The following commands assume current directory to be `live-translation/examples`

* **Install** examples dependencies:
    ```bash
    pip install --upgrade pip
    pip install .[examples]
    ```

## [Magic Word](magic_word.py)

Example of using `live_translation` with WebSocket to listen for an English phrase that translates to a specific "magic word" in Spanish.

**Run:** 
```bash
python magic_word
```

## [Augmented Reality (AR) OpenCV](ar_opencv.py)

Example of using `live_translation` with OpenCV to overlay translated or transcribed text near a detected face in a webcam feed.

> **NOTE**: The example uses ***NotoSans*** fonts located by default at ***/usr/share/fonts/truetype/noto/*** on **Ubuntu** systems:
>

**Run:** 
```bash
python ar_opencv [OPTIONS]
```
- **OPTIONS:**
    ```bash
    usage: ar_opencv.py [-h] [--src_lang SRC_LANG] [--tgt_lang TGT_LANG] [--device DEVICE] [--whisper_model WHISPER_MODEL] [--transcription_only] [--debug]

    options:
    -h, --help            show this help message and exit
    --src_lang SRC_LANG
    --tgt_lang TGT_LANG
    --device DEVICE
    --whisper_model WHISPER_MODEL
    --transcription_only
    --debug               Enable debug to show face box and add background to text.
    ```

## [Client Examples](./clients/)

This section provides minimal example clients in different environments (e.g. Node.js, C#, JavaScript, Go, Kotlin/Android) that demonstrate how to communicate with the live-translation server over **WebSocket** using the expected audio protocol:
**raw PCM, 16-bit, mono, 16kHz, 512-sample chunks i.e. 1024-byte chunks**.
Each client shows how to parse the server's **JSON responses**.

These examples focus purely on the communication protocol, and intentionally omit the complexities found in the main [**Python**](../live_translation/client/) implementation (e.g. callback chaining, concurrency control, async options). They are designed to help developers understand how to send audio to the server and receive transcription/translation responses.