# Nomi Telegram Companion

Single-owner Telegram bot that connects your chat to the Nomi API and replies back. Supports voice messages via offline Vosk speech-to-text on Windows.

## Features
- Chat with your Nomi from Telegram
- Voice notes to text with Vosk and FFmpeg
- Clean async stack on aiogram 3 and httpx
- Typed configuration with Pydantic
- Simple one-file run flow for Windows

## Tech stack
- Python 3.11+
- aiogram 3, httpx, pydantic, python-dotenv
- Vosk STT, imageio-ffmpeg, pydub

## Quick start on Windows

```powershell
git clone https://github.com/AmaLS367/Nomi_ai_tg.git
cd nomi_tg_companion

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

copy .env.example .env
# Edit .env and set at least:
# TELEGRAM_BOT_TOKEN=...
# NOMI_API_KEY=...
# NOMI_DEFAULT_NOMI_UUID=optional
```

Run the bot:
```powershell
python run.py
```

## Environment variables

| Name | Example | Description |
|---|---|---|
| TELEGRAM_BOT_TOKEN | 123456:ABC... | Token from @BotFather |
| NOMI_API_KEY | sk_live_xxx | API key from Nomi profile integrations |
| NOMI_DEFAULT_NOMI_UUID | 00000000-0000-0000-0000-000000000000 | Optional default Nomi ID used for chatting |
| LOG_LEVEL | INFO | Logging level: DEBUG, INFO, WARNING, ERROR |
| REQUEST_TIMEOUT_SEC | 30 | HTTP timeout in seconds for Nomi API calls |
| DB_PATH | ./data/app.db | Optional local SQLite path if used |
| MAX_AUDIO_BYTES | 10485760 | Max audio size to accept from Telegram |
| VOSK_MODEL_PATH | ./models/vosk-small-en | Path to unpacked Vosk model folder |
| FFMPEG_BIN | C:\ffmpeg\bin\ffmpeg.exe | Optional explicit path to ffmpeg.exe |

## Getting your Nomi UUID
You can query your account and copy the id field of your target Nomi:
```powershell
$env:NOMI_API_KEY="<your_nomi_api_key>"
$h = @{ Authorization = $env:NOMI_API_KEY }
irm -Headers $h https://api.nomi.ai/v1/nomis
```

## Voice notes requirements

1) FFmpeg  
Option A: Add ffmpeg to PATH on Windows  
Option B: Set FFMPEG_BIN in .env  
Quick check:
```powershell
.\.venv\Scripts\python.exe -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
```

2) Vosk model  
Download a small English model like `vosk-model-small-en-us-0.15`.  
Unpack to `./models/vosk-small-en` and set `VOSK_MODEL_PATH=./models/vosk-small-en` in `.env`.

## Bot commands and usage
- `/start` start and readiness check
- `/status` print active Nomi id
- Send any text message to chat with your Nomi
- For images or files, send a direct URL in the message or caption

## Project structure
```
.
├─ run.py
├─ requirements.txt
├─ .env.example
├─ src/
│  ├─ app.py
│  ├─ bot/
│  │  ├─ handlers/
│  │  └─ utils/
│  ├─ core/
│  ├─ services/
│  └─ ...
├─ data/
│  └─ logs/        (ignored)
└─ models/
   └─ vosk-small-en
```

## Troubleshooting

- FFmpeg not found  
  Set FFMPEG_BIN to the full path like `C:\ffmpeg\bin\ffmpeg.exe` or add that folder to PATH.

- Vosk model not found  
  Ensure VOSK_MODEL_PATH points to the folder that contains `model.conf` and `am` subfolder.

- Telegram updates not arriving  
  Confirm the bot token is correct and the bot is not paused in @BotFather.

## Development notes
- Keep `.env` out of git. Provide `.env.example` only.
- Exclude `data/logs/`, `build/`, `dist/`, and `*.egg-info/` in `.gitignore`.
- Prefer `requirements.txt` for this demo over `pyproject.toml` to keep setup simple.

## License
MIT. See LICENSE for details.
