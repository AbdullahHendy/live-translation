# translation/translator.py

import queue
import threading
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from config import TRANS_MODEL_NAME, DEVICE, SRC_LANG, TARGET_LANG

class Translator(threading.Thread):
    """
    Translator retrieves transcriptions from a queue, translates them using 
    the M2M-100 model, and prints the translation.
    """
    def __init__(self, transcription_queue: queue.Queue, 
                 stop_event: threading.Event):
        super().__init__()
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        print("🔄 Translator: Loading M2M-100 translation model...")
        self.tokenizer = M2M100Tokenizer.from_pretrained(TRANS_MODEL_NAME)
        self.model = M2M100ForConditionalGeneration.from_pretrained(
            TRANS_MODEL_NAME
        ).to(DEVICE)
    
    def run(self):
        print("🌍 Translator: Ready to translate text...")
        while not (self.stop_event.is_set() and 
                   self.transcription_queue.empty()):
            try:
                text = self.transcription_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                translation = self.translate(text, SRC_LANG, TARGET_LANG)
                print(f"🌍 Translator: {translation}")
            except Exception as e:
                print(f"Translator Error: {e}")
    
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        if not text.strip():
            return ""
        self.tokenizer.src_lang = src_lang
        inputs = self.tokenizer(text, return_tensors="pt").to(DEVICE)
        translated_tokens = self.model.generate(
            **inputs, forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang)
        )
        translated_text = self.tokenizer.decode(
            translated_tokens[0], skip_special_tokens=True
        )
        return translated_text
