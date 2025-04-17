# Examples

Simple scripts that demonstrate different ways to use `live_translation`.

## [Magic Word](magic_word.py)

Example of using `live_translation` with WebSocket to listen for an English phrase that translates to a specific "magic word" in Spanish.

**Run:** 
```bash
python -m examples.magic_word
```

## [Augmented Reality (AR) OpenCV](ar_opencv.py)

Example of using `live_translation` with OpenCV to overlay translated or transcribed text near a detected face in a webcam feed.

> **NOTE**: The example uses ***NotoSans*** fonts located by default at ***/usr/share/fonts/truetype/noto/*** on **Ubuntu** systems:
>

**Run:** 
```bash
python -m examples.ar_opencv [OPTIONS]
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
