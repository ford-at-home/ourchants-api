import whisper

def transcribe_audio_whisper(mp3_path: str, model_size="base") -> str:
    model = whisper.load_model(model_size)  # Options: tiny, base, small, medium, large
    result = model.transcribe(mp3_path)
    return result.get("text", "").strip()

