import subprocess
from essentia.standard import (
    MonoLoader, RhythmExtractor2013, KeyExtractor,
    Loudness, MFCC, PitchYin, OnsetRate
)

def convert_mp3_to_wav(mp3_path: str) -> str:
    wav_path = mp3_path.replace('.mp3', '.wav')
    subprocess.run(['ffmpeg', '-y', '-i', mp3_path, wav_path], check=True)
    return wav_path

def analyze_audio_essentia(mp3_path: str) -> dict:
    wav_path = convert_mp3_to_wav(mp3_path)
    audio = MonoLoader(filename=wav_path)()

    bpm, _, _, _, _ = RhythmExtractor2013(method="multifeature")(audio)
    key, scale, _ = KeyExtractor()(audio)
    loudness = Loudness()(audio)
    pitch, _ = PitchYin()(audio)
    mfcc, _ = MFCC()(audio)
    onset_rate = OnsetRate()(audio)

    return {
        "tempo_bpm": round(bpm, 2),
        "key": key,
        "scale": scale,
        "loudness_lufs": round(loudness, 2),
        "pitch_hz": round(pitch, 2),
        "onset_rate_hz": round(onset_rate, 2),
        "mfcc_shape": str(mfcc.shape)
    }

