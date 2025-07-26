import numpy as np
import tempfile
import os
import soundfile as sf
import time
from streamlit_webrtc import AudioProcessorBase
from faster_whisper import WhisperModel

# 🔁 Modelni bitta marta yuklab olish (global caching)
_model = None
def load_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", compute_type="auto")
    return _model

# 🎤 Ovozdan matn olish funksiyasi
def recognize_audio(audio_data: np.ndarray, lang: str = "uz") -> str:
    try:
        model = load_model()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            sf.write(tmpfile.name, audio_data, samplerate=16000)
            audio_path = tmpfile.name

        segments, info = model.transcribe(audio_path, language=lang)
        os.remove(audio_path)

        text = " ".join([segment.text for segment in segments])
        return text.strip()
    except Exception as e:
        print(f"❌ Tanib olishda xatolik: {e}")
        return ""

# 🎛️ Audio ishlovchi klass
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []
        self.last_voice_time = time.time()
        self.silence_threshold = 5  # jimlik chegarasi (sekund)
        self.sample_rate = 16000
        self.buffer_duration = 15  # maksimal ovoz yozish vaqti (sekund)

    def recv(self, frame):
        samples = frame.to_ndarray()
        volume = np.abs(samples).mean()

        now = time.time()

        # 🔊 Agar ovoz mavjud bo‘lsa, audio to‘planadi
        if volume > 0.01:
            self.last_voice_time = now
            self.frames.append(samples)
        else:
            # 🤫 Agar 5 soniyadan ko‘p jim bo‘lsa, yozishni to‘xtatish
            if now - self.last_voice_time > self.silence_threshold:
                return None  # bu `webrtc_streamer`ni to‘xtatadi

        return frame

    # 📄 Matnga aylantirish
    def transcribe(self):
        if self.frames:
            audio = np.concatenate(self.frames, axis=0).astype(np.float32)
            self.frames = []
            return recognize_audio(audio)
        return ""
