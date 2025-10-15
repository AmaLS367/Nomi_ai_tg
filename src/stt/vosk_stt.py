import os
import json
import subprocess
from typing import Optional
from vosk import Model, KaldiRecognizer
import imageio_ffmpeg

class SttNotConfigured(Exception):
    pass

_model: Optional[Model] = None

def _get_model() -> Model:
    global _model
    if _model is not None:
        return _model
    model_path = os.getenv("VOSK_MODEL_PATH", "").strip()
    if not model_path or not os.path.isdir(model_path):
        raise SttNotConfigured("VOSK_MODEL_PATH not set or invalid")
    _model = Model(model_path)  # EN model supported
    return _model

def _ffmpeg_path() -> str:
    p = os.getenv("FFMPEG_BIN", "").strip()
    if p:
        if not os.path.isfile(p):
            raise SttNotConfigured(f"FFMPEG_BIN points to non-file: {p}")
        return p
    p = imageio_ffmpeg.get_ffmpeg_exe()
    if not p or not os.path.exists(p):
        raise SttNotConfigured("FFmpeg not available (imageio-ffmpeg cache missing).")
    return p

def _decode_to_pcm16_mono16k_ffmpeg(data: bytes) -> bytes:
    ffmpeg_bin = _ffmpeg_path()
    try:
        proc = subprocess.run(
            [ffmpeg_bin, "-nostdin", "-hide_banner", "-loglevel", "error",
             "-i", "pipe:0", "-ac", "1", "-ar", "16000", "-f", "s16le", "pipe:1"],
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError as e:
        raise SttNotConfigured("FFmpeg not found (set FFMPEG_BIN or install).") from e
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode("utf-8", errors="ignore").strip()
        raise SttNotConfigured(f"FFmpeg decode error: {msg}") from e
    return proc.stdout  # RAW PCM16 mono 16kHz

async def transcribe_bytes(data: bytes, filename: str) -> str:
    pcm = _decode_to_pcm16_mono16k_ffmpeg(data)
    rec = KaldiRecognizer(_get_model(), 16000)
    rec.SetWords(True)

    chunk = 8000
    for i in range(0, len(pcm), chunk):
        rec.AcceptWaveform(pcm[i:i+chunk])

    try:
        final = json.loads(rec.FinalResult())
        return (final.get("text") or "").strip()
    except Exception:
        return ""
