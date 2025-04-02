# Examples

This directory contains simple scripts that demonstrate different ways to use `live_translation`.

## [Magic Word](magic_word.py)

Example of using `live_translation` with WebSocket to listen for an English phrase that translates to a specific "magic word" in Spanish.

**Run:** 
```bash
python -m examples.magic_word
```

## [Augmented Reality (AR) OpenCV](ar_opencv.py)

Example of using `live_translation` with OpenCV to overlay translated or transcribed text near a detected face in a webcam feed.

**Run:** 
```bash
python -m examples.ar_opencv [OPTION]
```
- **OPTION:**
    ```bash
    --transcription_only  Overlay only the transcription text
    ```

