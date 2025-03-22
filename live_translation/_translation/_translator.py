# translation/_translator.py

from datetime import datetime, timezone
import torch
import queue
import multiprocessing as mp
import threading
from transformers import MarianMTModel, MarianTokenizer
from .. import config


class Translator(mp.Process):
    """
    Translator retrieves transcriptions from a queue, translates them using
    the M2M-100 model, and prints the translation.
    """

    def __init__(
        self,
        transcription_queue: mp.Queue,
        stop_event: threading.Event,
        cfg: config.Config,
        output_queue: mp.Queue,
    ):
        """Initialize the Translator."""
        super().__init__()
        self._transcription_queue = transcription_queue
        self._stop_event = stop_event
        self._cfg = cfg
        self._output_queue = output_queue

        self._model_name = (
            f"{self._cfg.TRANS_MODEL}-{self._cfg.SRC_LANG}-{self._cfg.TGT_LANG}"
        )

        print(f"🔄 Translator: Loading {self._model_name} model...")
        self._tokenizer = MarianTokenizer.from_pretrained(self._model_name)

    def run(self):
        self.model = MarianMTModel.from_pretrained(
            self._model_name, torch_dtype=torch.float32
        ).to(self._cfg.DEVICE)

        print("🌍 Translator: Ready to translate text...")

        try:
            while not (self._stop_event.is_set() and self._transcription_queue.empty()):
                # Get transcription from the queue
                try:
                    text = self._transcription_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                try:
                    translation = self._translate(text)
                    if not self._cfg.TRANSCRIBE_ONLY:
                        entry = {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "transcription": text,
                            "translation": translation,
                        }
                        self._output_queue.put(entry)
                except Exception as e:
                    print(f"🚨 Translator Error: {e}")
        except Exception as e:
            print(f"🚨 Critical Translator Error: {e}")
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
            print("🌍 Translator: Stopped.")

    def _translate(self, text: str) -> str:
        if not text.strip():
            return ""

        inputs = self._tokenizer(text, return_tensors="pt").to(self._cfg.DEVICE)

        with torch.inference_mode():
            translated_tokens = self.model.generate(
                **inputs,
            )
        translated_text = self._tokenizer.decode(
            translated_tokens[0], skip_special_tokens=True
        )
        return translated_text

    def _cleanup(self):
        """Clean up the translation model."""
        pass
