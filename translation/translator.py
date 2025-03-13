# translation/translator.py

import torch
import queue
import multiprocessing as mp
import threading
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import config
from output_manager import OutputManager


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
        print("🔄 Translator: Loading M2M-100 translation model...")
        self.tokenizer = M2M100Tokenizer.from_pretrained(
            self.cfg.TRANS_MODEL
        )

    def run(self):
        self.model = M2M100ForConditionalGeneration.from_pretrained(
            self.cfg.TRANS_MODEL
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
                    translation = self.translate(
                        text, 
                        self.cfg.SRC_LANG, 
                        self.cfg.TARGET_LANG
                    )
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
    
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        if not text.strip():
            return ""
        self.tokenizer.src_lang = src_lang
        
        inputs = self.tokenizer(
            text, 
            return_tensors="pt"
        ).to(self.cfg.DEVICE)

        with torch.inference_mode():
            translated_tokens = self.model.generate(
                **inputs, 
                forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang)
            )
        translated_text = self.tokenizer.decode(
            translated_tokens[0], skip_special_tokens=True
        )
        return translated_text

    def _cleanup(self):
        """Clean up the translation model."""
        pass