import os
import sys
import datetime
from whisper_analysis import transcribe_audio_whisper
from essentia_analysis import analyze_audio_essentia

OUTPUT_DIR = ".output"
LOG_FILE = os.path.join(OUTPUT_DIR, "logstream.txt")

def log(message: str):
    timestamp = datetime.datetime.now().isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(line + "\n")

def full_analysis(mp3_path: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Ensure logstream.txt is being streamed to, not recreated
    open(LOG_FILE, "a").close()

    base_filename = os.path.splitext(os.path.basename(mp3_path))[0]
    output_txt_path = os.path.join(OUTPUT_DIR, f"{base_filename}.txt")

    log(f"🎧 Starting analysis for: {mp3_path}")

    try:
        transcription = transcribe_audio_whisper(mp3_path)
        log("✅ Whisper transcription complete.")
    except Exception as e:
        log(f"❌ Whisper transcription failed: {e}")
        transcription = "[Transcription failed]"

    try:
        analysis = analyze_audio_essentia(mp3_path)
        log("✅ Essentia audio analysis complete.")
    except Exception as e:
        log(f"❌ Essentia analysis failed: {e}")
        analysis = {"error": str(e)}

    with open(output_txt_path, 'w') as f:
        f.write(f"🎧 Audio File: {os.path.basename(mp3_path)}\n\n")
        f.write("=== Transcription ===\n")
        f.write(transcription + "\n\n")
        f.write("=== Audio Analysis (Essentia) ===\n")
        for key, val in analysis.items():
            f.write(f"{key}: {val}\n")

    log(f"✅ Results written to: {output_txt_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_song.py path/to/song.mp3")
        sys.exit(1)

    full_analysis(sys.argv[1])
