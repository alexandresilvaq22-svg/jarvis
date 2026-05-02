import tempfile
import os
import base64
from gtts import gTTS

def text_to_audio_base64(text: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        tts = gTTS(text=text, lang='pt', tld='com.br', slow=False)
        tts.save(tmp_path)
        with open(tmp_path, "rb") as f:
            audio_data = f.read()
        return base64.b64encode(audio_data).decode("utf-8")
    finally:
        os.unlink(tmp_path)