import numpy as np
import tempfile
import os
import soundfile as sf
import pandas as pd
from difflib import get_close_matches
from streamlit_webrtc import AudioProcessorBase
from faster_whisper import WhisperModel

# -------------------------
# 1. Whisper modelni kesh bilan yuklash
# -------------------------
_model = None

def load_model():
    global _model
    if _model is None:
        try:
            _model = WhisperModel("base", compute_type="auto")  # CPU yoki GPU da avtomatik
        except Exception as e:
            print(f"❌ Whisper model yuklashda xatolik: {e}")
            raise e
    return _model

# -------------------------
# 2. Ovozdan matnga konvertatsiya
# -------------------------
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
        print(f"❌ Matn tanib olishda xatolik: {e}")
        return ""

# -------------------------
# 3. Streamlit WebRTC audio processori
# -------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame):
        self.frames.append(frame.to_ndarray())
        return frame

    def get_audio_data(self):
        if self.frames:
            audio = np.concatenate(self.frames, axis=0)
            self.frames = []
            return audio
        return None

# -------------------------
# 4. CSV yuklash
# -------------------------
def load_data(csv_path: str = "alternativa1.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        print(f"❌ Fayl topilmadi: {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ CSVni o‘qishda xatolik: {e}")
        return pd.DataFrame()

# -------------------------
# 5. Dori nomini qidirish
# -------------------------
def find_alternatives(drug_name: str, df: pd.DataFrame):
    if df.empty:
        return None, None, []

    try:
        match = get_close_matches(drug_name.lower(), df["Dori nomi yoki alternativ"].str.lower(), n=1, cutoff=0.6)
        if not match:
            return None, None, []

        matched_name = match[0]
        original_row = df[df["Dori nomi yoki alternativ"].str.lower() == matched_name]

        if original_row.empty:
            return None, None, []

        active_substance = original_row.iloc[0]["Faol modda"]
        alternatives = df[df["Faol modda"] == active_substance]["Dori nomi yoki alternativ"].tolist()

        return matched_name, active_substance, alternatives
    except Exception as e:
        print(f"❌ Dori topishda xatolik: {e}")
        return None, None, []
