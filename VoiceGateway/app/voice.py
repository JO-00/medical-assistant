from faster_whisper import WhisperModel
import numpy as np
import librosa
import torch
from transformers import VitsModel, AutoTokenizer

class FrenchSTT:
    BLACKLIST = {
        # Whisper subtitle hallucinations
        "amara",
        "sous titre",
        "sous-titre",
        "sous titres",
        "sous-titres",
        "sous titrage",
        "réalisé par la communauté",
        "réalisés par la communauté",
        "subtitles",
        "subtitle",

        # Empty / noise hallucinations
        "♪",
        "...",
    }

    def __init__(self):
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

    def is_hallucination(self, text: str) -> bool:
        normalized = text.lower().strip()

        if not normalized:
            return True

        return any(
            phrase in normalized
            for phrase in self.BLACKLIST
        )

    def stt(self, audio):
        sample_rate, audio_data = audio

        # (1, samples) -> (samples,)
        audio_data = np.squeeze(audio_data)

        # int16 -> float32 [-1, 1]
        audio_data = audio_data.astype(np.float32) / 32768.0

        # Resample to 16kHz
        if sample_rate != 16000:
            audio_data = librosa.resample(
                audio_data,
                orig_sr=sample_rate,
                target_sr=16000
            )

        segments, info = self.model.transcribe(
            audio_data,
            language="fr",
            vad_filter=True,
            condition_on_previous_text=False
        )

        text_parts = []
        confidence_scores = []

        for segment in segments:
            text_parts.append(segment.text)
            confidence_scores.append(segment.avg_logprob)

        text = "".join(text_parts).strip()

        # Remove Whisper hallucinations
        if self.is_hallucination(text):
            print("[STT] Hallucination ignored:", text)
            return ""

        # Reject very uncertain outputs
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)

            if avg_confidence < -1.0:
                print("[STT] Low confidence ignored:", avg_confidence)
                return ""

        # Medical vocabulary correction
        replacements = {
            "passion": "patient",
            "passions": "patients",
        }

        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)

        return text

stt_model = FrenchSTT()




class FrenchTTS:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "facebook/mms-tts-fra"
        )

        self.model = VitsModel.from_pretrained(
            "facebook/mms-tts-fra"
        )

        self.sample_rate = self.model.config.sampling_rate

    def stream_tts_sync(self, text):

        inputs = self.tokenizer(
            text,
            return_tensors="pt"
        )

        with torch.no_grad():
            output = self.model(**inputs)

        audio = output.waveform.squeeze().numpy()

        yield (self.sample_rate, audio)

tts_model = FrenchTTS()