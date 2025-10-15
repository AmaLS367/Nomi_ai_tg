import os
import httpx
from aiogram import Router, F
from aiogram.types import Message
from nomi.service import NomiService
from stt.vosk_stt import transcribe_bytes, SttNotConfigured

router = Router()

MAX_AUDIO_BYTES = int(os.getenv("MAX_AUDIO_BYTES", "10485760"))  # 10 MB

def _trim(s: str, n: int = 4000) -> str:
    s = (s or "").strip()
    if len(s) > n:
        return s[: n - 1] + "…"
    return s

async def _download_tg_file(bot, file_id: str) -> tuple[bytes, str]:
    f = await bot.get_file(file_id)
    path = f.file_path
    url = f"https://api.telegram.org/file/bot{bot.token}/{path}"
    async with httpx.AsyncClient(timeout=120) as s:
        r = await s.get(url)
        r.raise_for_status()
        data = r.content
    name = (path.rsplit("/", 1)[-1]) or "audio"
    return data, name

async def _send_and_reply(m: Message, service: NomiService, text: str):
    reply = await service.send(text)
    reply = _trim(reply) or "No response."
    await m.answer(reply)

def setup(service: NomiService) -> Router:
    @router.message(F.text)
    async def on_text(m: Message):
        text = (m.text or "").strip()
        if not text:
            return
        try:
            await _send_and_reply(m, service, _trim(text))
        except httpx.HTTPStatusError as e:
            sc = e.response.status_code
            if sc in (401, 403):
                await m.answer("Auth error. Check NOMI_API_KEY.")
            elif sc == 429:
                await m.answer("Rate limit. Try again in a moment.")
            elif sc >= 500:
                await m.answer("Server error on Nomi side. Try again later.")
            else:
                await m.answer(f"HTTP error {sc}. Try again.")
        except httpx.TimeoutException:
            await m.answer("Timeout. Please try again.")
        except Exception:
            await m.answer("Something went wrong. Please try again.")


    @router.message(F.voice)
    async def on_voice(m: Message):
        voice = m.voice
        if voice is None:
            return
        size = voice.file_size or 0
        if size > MAX_AUDIO_BYTES:
            await m.answer("Voice note is too large.")
            return
        try:
            data, name = await _download_tg_file(m.bot, voice.file_id)
            text = await transcribe_bytes(data, name)
            if not text:
                await m.answer("Transcription is empty.")
                return
            await _send_and_reply(m, service, _trim(text))
        except SttNotConfigured as e:
            await m.answer(str(e))
        except FileNotFoundError:
            await m.answer("FFmpeg not found. Install ffmpeg and add it to PATH.")
        except Exception:
            await m.answer("Audio transcription failed. Try again later.")

    @router.message(F.audio)
    async def on_audio(m: Message):
        audio = m.audio
        
        if audio is None:
             return
         
        size = audio.file_size or 0
        if size > MAX_AUDIO_BYTES:
            await m.answer("Audio file is too large.")
            return
        try:
            data, name = await _download_tg_file(m.bot, audio.file_id)
            text = await transcribe_bytes(data, name)
            if not text:
                await m.answer("Transcription is empty.")
                return
            await _send_and_reply(m, service, _trim(text))
        except SttNotConfigured as e:
            await m.answer(str(e))
        except FileNotFoundError:
            await m.answer("FFmpeg not found. Install ffmpeg and add it to PATH.")
        except Exception:
            await m.answer("Audio transcription failed. Try again later.")

    @router.message(F.photo)
    async def on_photo(m: Message):
        await m.answer("Image messages are not supported.")

    @router.message(F.animation)
    async def on_gif(m: Message):
        await m.answer("GIF messages are not supported.")

    @router.message(F.video)
    async def on_video(m: Message):
        await m.answer("Video messages are not supported.")

    @router.message(F.document)
    async def on_document(m: Message):
        await m.answer("Document messages are not supported.")

    @router.message(F.sticker)
    async def on_sticker(m: Message):
        await m.answer("Stickers are not supported.")

    return router
