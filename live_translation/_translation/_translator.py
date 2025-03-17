# translation/_translator.py

import torch
import queue
import multiprocessing as mp
import threading
from transformers import MarianMTModel, MarianTokenizer
from .. import config
from .._output import OutputManager


class Translator(mp.Process):
    """
    Translator retrieves transcriptions from a queue, translates them using 
    the M2M-100 model, and prints the translation.
    """
    def __init__(self, transcription_queue: mp.Queue, 
                 stop_event: threading.Event, 
                 cfg: config.Config, 
                 output_manager: OutputManager
                ):
        """Initialize the Translator."""
        super().__init__()
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        self.cfg = cfg
        self.output_manager = output_manager

        self.model_name = (
            f"{self.cfg.TRANS_MODEL}-"
            f"{self.cfg.SRC_LANG}-"
            f"{self.cfg.TGT_LANG}"
        )

        print(f"🔄 Translator: Loading {self.model_name} translation model...")
        self.tokenizer = MarianTokenizer.from_pretrained(
            self.model_name
        )
    
    def run(self):
        self.model = MarianMTModel.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32
        ).to(self.cfg.DEVICE)

        print("🌍 Translator: Ready to translate text...")

        try:
            while not (self.stop_event.is_set() and 
                    self.transcription_queue.empty()):
                # Get transcription from the queue
                try:
                    text = self.transcription_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                try:
                    translation = self.translate(text)
                    if not self.cfg.TRANSCRIBE_ONLY:
                        self.output_manager.write(text, translation)
                except Exception as e:
                    print(f"🚨 Translator Error: {e}")
        except Exception as e:
            print(f"🚨 Critical Translator Error: {e}")
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
            print("🌍 Translator: Stopped.")
    
    def translate(self, text: str) -> str:
        if not text.strip():
            return ""
        
        inputs = self.tokenizer(
            text, 
            return_tensors="pt"
        ).to(self.cfg.DEVICE)

        with torch.inference_mode():
            translated_tokens = self.model.generate(
                **inputs, 
            )
        translated_text = self.tokenizer.decode(
            translated_tokens[0], skip_special_tokens=True
        )
        return translated_text

    def _cleanup(self):
        """Clean up the translation model."""
        pass